import pytest

from tests.db.connection import get_db_connection
from tests.db.extension_queries import delete_extensions, get_existing_extensions, get_extension_numbers


def get_extension_numbers_from_database():
    connection = get_db_connection()
    try:
        return get_extension_numbers(connection)
    finally:
        connection.close()


def extensions_remaining_in_database(extension_numbers):
    connection = get_db_connection()
    try:
        return get_existing_extensions(connection, extension_numbers)
    finally:
        connection.close()


def delete_extensions_from_database(extension_numbers):
    numbers = [str(number) for number in extension_numbers]
    if not numbers:
        return 0

    connection = get_db_connection()
    try:
        return delete_extensions(connection, numbers)
    finally:
        connection.close()


def cleanup_extensions_with_db_fallback(extensions_page, extension_numbers, ui_cleanup):
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

    remaining = extensions_remaining_in_database(numbers)
    if not remaining:
        extensions_page.log_action(f"Cleanup: extension(s) removed: {', '.join(numbers)}")
        return

    deleted_count = delete_extensions_from_database(remaining)
    extensions_page.log_action(
        f"DB fallback cleanup removed {deleted_count} extension(s): {', '.join(remaining)}"
    )


def get_existing_extension_number():
    extension_numbers = get_extension_numbers_from_database()
    if not extension_numbers:
        pytest.skip("No extensions found in the database to test with.")
    return extension_numbers[0]


def get_non_existing_extension_number():
    active_extension_numbers = [int(number) for number in get_extension_numbers_from_database()]
    if not active_extension_numbers:
        return 1000
    return max(active_extension_numbers) + 1


def get_non_existing_extension_range(size=2):
    active_extension_numbers = [int(number) for number in get_extension_numbers_from_database()]
    if not active_extension_numbers:
        start = 1000
        return start, start + size - 1

    start = max(active_extension_numbers) + 1
    end = start + size - 1
    return start, end


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