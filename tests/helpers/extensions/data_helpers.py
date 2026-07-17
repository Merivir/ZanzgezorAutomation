import pytest

from tests.config.automation_config import get_extensions_config, load_config
from tests.db.connection import get_db_connection
from tests.db.extension_queries import (
    delete_extensions,
    get_existing_extensions,
    get_extension_numbers,
    get_extension_identity,
    get_last_extension_number,
)


PJSIP_EXTENSION_TYPE = "pjsip"
WEBRTC_EXTENSION_TYPE = "webrtc"


def _extension_scope(extension_type):
    extensions_config = get_extensions_config(load_config())
    company_name = extensions_config.get("company_name")
    missing = [
        key
        for key, value in (("company_name", company_name), ("extension_type", extension_type))
        if not value
    ]
    if missing:
        raise ValueError(f"Missing extension database scope configuration: {', '.join(missing)}")
    return company_name, extension_type


def get_extension_numbers_from_database(extension_type=PJSIP_EXTENSION_TYPE):
    company_name, extension_type = _extension_scope(extension_type)
    connection = get_db_connection()
    try:
        return get_extension_numbers(connection, company_name, extension_type)
    finally:
        connection.close()


def get_extension_identity_from_database(extension_number, extension_type=PJSIP_EXTENSION_TYPE):
    company_name, extension_type = _extension_scope(extension_type)
    connection = get_db_connection()
    try:
        identity = get_extension_identity(
            connection,
            extension_number,
            company_name,
            extension_type,
        )
    finally:
        connection.close()

    if identity is None:
        raise AssertionError(
            f"Extension '{extension_number}' was not found for company '{company_name}' "
            f"with type '{extension_type}'."
        )

    extension, real_extension = identity
    return {
        "extension": extension,
        "real_extension": real_extension,
        "sip_extension": real_extension or extension,
        "requires_publish": bool(real_extension),
    }


def extensions_remaining_in_database(extension_numbers, extension_type=PJSIP_EXTENSION_TYPE):
    company_name, extension_type = _extension_scope(extension_type)
    connection = get_db_connection()
    try:
        return get_existing_extensions(
            connection,
            extension_numbers,
            company_name,
            extension_type,
        )
    finally:
        connection.close()


def delete_extensions_from_database(extension_numbers, extension_type=PJSIP_EXTENSION_TYPE):
    numbers = [str(number) for number in extension_numbers]
    if not numbers:
        return 0

    company_name, extension_type = _extension_scope(extension_type)
    connection = get_db_connection()
    try:
        return delete_extensions(
            connection,
            numbers,
            company_name,
            extension_type,
        )
    finally:
        connection.close()


def cleanup_extensions_with_db_fallback(
    extensions_page,
    extension_numbers,
    ui_cleanup,
    extension_type=PJSIP_EXTENSION_TYPE,
):
    numbers = [str(number) for number in extension_numbers]
    if not numbers:
        return

    ui_cleanup_succeeded = False
    try:
        extensions_page.log_action(f"Cleanup: delete extension(s) from UI: {', '.join(numbers)}")
        ui_cleanup()
        ui_cleanup_succeeded = True
    except Exception as error:
        extensions_page.log_action(f"UI cleanup failed, will try DB fallback: {error}")

    if ui_cleanup_succeeded:
        try:
            extensions_page.log_action("Cleanup: publish deletion changes")
            extensions_page.publish_changes()
            extensions_page.wait_for_ui_idle()
        except Exception as error:
            extensions_page.log_action(f"Publish after UI cleanup failed, will check DB fallback: {error}")

    remaining = extensions_remaining_in_database(numbers, extension_type)
    if not remaining:
        extensions_page.log_action(f"Cleanup: extension(s) removed: {', '.join(numbers)}")
        return

    deleted_count = delete_extensions_from_database(remaining, extension_type)
    extensions_page.log_action(
        f"DB fallback cleanup removed {deleted_count} extension(s): {', '.join(remaining)}"
    )


def get_existing_extension_number(extension_type=PJSIP_EXTENSION_TYPE):
    extension_numbers = get_extension_numbers_from_database(extension_type)
    if not extension_numbers:
        pytest.skip(f"No scoped {extension_type} extensions found in the database to test with.")
    return extension_numbers[0]


def get_non_existing_extension_number(extension_type=PJSIP_EXTENSION_TYPE):
    company_name, extension_type = _extension_scope(extension_type)
    connection = get_db_connection()
    try:
        last_extension = get_last_extension_number(connection, company_name, extension_type)
    finally:
        connection.close()

    if last_extension is None:
        return 1000
    return int(last_extension) + 1


def get_non_existing_extension_range(size=2, extension_type=PJSIP_EXTENSION_TYPE):
    start = get_non_existing_extension_number(extension_type)
    return start, start + size - 1


def add_extension_from_ui(extensions_page, extension_number, end_extension_number=None, password="Test1234"):
    extensions_page.create_extension(
        extension_number=extension_number,
        end_extension_number=end_extension_number,
        password=password,
    )
    assert extensions_page.has_visible_extension(extension_number), (
        f"Expected disposable extension '{extension_number}' to be visible after adding it."
    )
    return str(extension_number)


def add_extension_range_from_ui(extensions_page, start_extension, end_extension, password="Test1234"):
    extension_numbers = list(range(int(start_extension), int(end_extension) + 1))
    try:
        add_extension_from_ui(extensions_page, start_extension, end_extension, password=password)
        extensions_page.assert_extensions_exist(extension_numbers)
    except Exception:
        cleanup_extensions_with_db_fallback(
            extensions_page,
            extension_numbers,
            lambda: bottom_delete_extension_range_from_ui(extensions_page, start_extension, end_extension),
        )
        raise

    return str(start_extension), str(end_extension)


def row_delete_extension_range_from_ui(extensions_page, start_extension, end_extension):
    for extension_number in range(int(start_extension), int(end_extension) + 1):
        row_delete_extension_from_ui(extensions_page, extension_number)


def bottom_delete_extension_range_from_ui(extensions_page, start_extension, end_extension):
    extension_range = list(range(int(start_extension), int(end_extension) + 1))
    if not extensions_remaining_in_database(extension_range):
        return

    try:
        (
            extensions_page
            .open_bottom_delete_popup()
            .fill_add_popup(start_extension, end_extension)
            .submit_add_popup(wait_until_closed=True)
        )
        if extensions_page.is_delete_confirmation_open():
            extensions_page.confirm_delete_confirmation()
        extensions_page.wait_for_success_notification().reload_extensions_table()
    finally:
        if extensions_page.is_add_popup_open():
            extensions_page.close_add_popup()


def row_delete_extension_from_ui(extensions_page, extension_number):
    extensions_page.delete_extension_if_exists(extension_number)
