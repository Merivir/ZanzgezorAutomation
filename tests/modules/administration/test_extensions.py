import csv
import pytest
import time 

from tests.config.automation_config import (
    load_config,
    get_active_client,
    get_client_config,
    get_user_credentials,
)
from tests.config.testcase import testcase
from tests.pages.login_page import LoginPage
from tests.pages.administration_page import AdministrationPage
from tests.pages.extensions_page import ExtensionsPage

from tests.db.connection import get_db_connection
from tests.db.extension_queries import get_extension_numbers


EXPECTED_EXPORT_COLUMNS = ["Extension", "Real Extension", "Password", "Type", "Transport Type", "Status"]
EXPORT_COLUMN_ALIASES = {
    "Extension": "Extension",
    "Real Extension": "Real Extension",
    "Password": "Password",
    "Type": "Type",
    "Transport type": "Transport Type",
    "Transport Type": "Transport Type",
    "Status": "Status",
}


def wait_for_csv_download(download_dir, timeout=20):
    deadline = time.time() + timeout
    while time.time() < deadline:
        csv_files = list(download_dir.glob("*.csv"))
        active_downloads = list(download_dir.glob("*.crdownload"))
        if csv_files and not active_downloads:
            return max(csv_files, key=lambda path: path.stat().st_mtime)
        time.sleep(1)

    pytest.fail(f"No CSV file was downloaded to {download_dir}.")


def read_csv_rows(csv_path):
    content = csv_path.read_text(encoding="utf-8-sig").strip()
    assert content not in {"501", "505"}, f"Export returned server error status in CSV file: {content}"
    assert not content.startswith(("501", "505")), f"Export returned server error instead of table data: {content[:120]}"
    assert '"status":5' not in content, f"Export returned server error response instead of CSV table data: {content[:120]}"

    sample = content[:1024]
    try:
        dialect = csv.Sniffer().sniff(sample)
    except csv.Error:
        dialect = csv.excel

    return list(csv.reader(content.splitlines(), dialect))


def column_values(rows, column_name):
    header = [cell.strip() for cell in rows[0]]
    column_index = header.index(column_name)
    return [row[column_index].strip() for row in rows[1:] if len(row) > column_index]


def csv_records(rows):
    header = [cell.strip() for cell in rows[0]]
    return [dict(zip(header, row)) for row in rows[1:]]


def records_by_column(records, column_name):
    return {record[column_name]: record for record in records if record.get(column_name)}


def normalize_record_value(value):
    return str(value or "").strip()


@pytest.fixture(scope="module")
def opened_extensions_page(driver, wait):
    config = load_config()
    active_client = get_active_client(config)
    client_config = get_client_config(config, active_client)
    credentials = get_user_credentials(config, "default")

    login_page = LoginPage(driver, wait, client_config["base_url"])
    administration_page = AdministrationPage(driver, wait)
    extensions_page = ExtensionsPage(driver, wait)

    login_page.open()
    login_page.login(credentials["username"], credentials["password"])
    administration_page.open_administration_page()
    administration_page.open_extensions()
    extensions_page.wait_until_loaded()

    return extensions_page

def get_existing_extension_number():
    connection = get_db_connection()
    extension_numbers = get_extension_numbers(connection)
    if not extension_numbers:
        pytest.skip("No extensions found in the database to test with.")
    return extension_numbers[0]  # Return the first extension number

def get_non_existing_extension_number():
    connection = get_db_connection()
    active_extension_numbers = [int(number) for number in get_extension_numbers(connection)]
    if not active_extension_numbers:
        pytest.skip("No active extensions found in the database to test with.")
    return max(active_extension_numbers) + 1


def get_non_existing_extension_range(size=2):
    connection = get_db_connection()
    active_extension_numbers = [int(number) for number in get_extension_numbers(connection)]
    if not active_extension_numbers:
        pytest.skip("No active extensions found in the database to test with.")

    start = max(active_extension_numbers) + 1
    end = start + size - 1
    return start, end


def add_extension_from_ui(extensions_page, extension_number, end_extension_number=None, password="Test1234"):
    if end_extension_number is None:
        end_extension_number = extension_number

    if extensions_page.is_delete_confirmation_open():
        extensions_page.cancel_delete_confirmation()
        time.sleep(2)
    if extensions_page.is_add_popup_open():
        extensions_page.close_add_popup()
        time.sleep(2)

    extensions_page.open_add_popup()
    time.sleep(2)
    extensions_page.choose_extension_type("pjsip")
    time.sleep(2)
    extensions_page.choose_transport_type("udp")
    time.sleep(2)
    extensions_page.fill_add_popup(extension_number, end_extension_number, password=password)
    time.sleep(2)
    extensions_page.submit_add_popup()
    time.sleep(2)
    extensions_page.search_for_extension_number(extension_number)
    time.sleep(2)
    assert extensions_page.has_visible_extension(extension_number), (
        f"Expected disposable extension '{extension_number}' to be visible after adding it."
    )
    return str(extension_number)


def add_extension_range_from_ui(extensions_page, start_extension, end_extension, password="Test1234"):
    add_extension_from_ui(extensions_page, start_extension, end_extension, password=password)
    missing_extensions = []
    for extension_number in range(int(start_extension), int(end_extension) + 1):
        extensions_page.search_for_extension_number(extension_number)
        time.sleep(2)
        if not extensions_page.has_visible_extension(extension_number):
            missing_extensions.append(str(extension_number))

    if missing_extensions:
        bottom_delete_extension_range_from_ui(extensions_page, start_extension, end_extension)
        pytest.fail(
            f"Range add did not create all expected extensions from {start_extension} to {end_extension}. "
            f"Missing: {', '.join(missing_extensions)}."
        )

    return str(start_extension), str(end_extension)


def row_delete_extension_range_from_ui(extensions_page, start_extension, end_extension):
    for extension_number in range(int(start_extension), int(end_extension) + 1):
        row_delete_extension_from_ui(extensions_page, extension_number)


def bottom_delete_extension_range_from_ui(extensions_page, start_extension, end_extension):
    extensions_page.open_bottom_delete_popup()
    time.sleep(2)
    try:
        extensions_page.fill_add_popup(start_extension, end_extension)
        time.sleep(2)
        extensions_page.submit_popup_and_wait_closed()
        time.sleep(2)
    finally:
        if extensions_page.is_add_popup_open():
            extensions_page.close_add_popup()


def row_delete_extension_from_ui(extensions_page, extension_number):
    extensions_page.search_for_extension_number(extension_number)
    time.sleep(2)
    if not extensions_page.has_visible_extension(extension_number):
        return

    extensions_page.open_first_row_delete_confirmation()
    time.sleep(2)
    extensions_page.confirm_delete_confirmation()
    time.sleep(2)


def skip_not_automated_yet():
    pytest.skip("Linked to TestLink, but Selenium steps are not automated yet.")


def not_automated(test_func):
    test_func = pytest.mark.not_automated(test_func)
    return pytest.mark.skip(reason="Linked to TestLink, but Selenium steps are not automated yet.")(test_func)


not_automated.__test__ = False


@testcase("808-808", "Verify Company Extensions: Navigation - Extensions page opens correctly")
@pytest.mark.administration
@pytest.mark.extensions
def test_extensions_page_opens_correctly(opened_extensions_page):
    assert opened_extensions_page.is_loaded(), "Extensions page did not load correctly."


@testcase("808-3033", "Verify Company Extensions: Search - Matching extension returns filtered result")
@pytest.mark.administration
@pytest.mark.extensions
def test_extension_search_functionality(opened_extensions_page):
    existing_extension_number = get_existing_extension_number()
    extensions_page = opened_extensions_page.search_for_extension_number(existing_extension_number)
    rows = extensions_page.visible_table_rows()
    time.sleep(2)  # Wait for search results to update
    assert len(rows) > 0, f"No results found in the table after searching for extension '{existing_extension_number}'."


@testcase("808-3034", "Verify Company Extensions: Search - Empty search returns full extensions list")
@pytest.mark.administration
@pytest.mark.extensions
def test_empty_extension_search_returns_full_extensions_list(opened_extensions_page):
    extensions_page = opened_extensions_page.search_for_extension_number("")
    time.sleep(2)  # Wait for search results to update
    rows = extensions_page.visible_table_rows()
    assert len(rows) > 0, "Expected extensions to be displayed after running an empty search."


@pytest.mark.skipif(False, reason="Temporarily disabled")
def test_extension_search_no_results(opened_extensions_page):
    non_existing_extension_number = get_non_existing_extension_number()
    extensions_page = opened_extensions_page.search_for_extension_number(non_existing_extension_number)
    time.sleep(2)  # Wait for search results to update
    message = extensions_page.driver.find_elements(*extensions_page.EMPTY_TABLE_MESSAGE)
    assert message[0].text.strip() == "No data to display!", "Expected 'No data' message when searching for non-existent extension, but it was not found."  


@testcase("808-3035", "Verify Company Extensions: Filters - Clear filters resets search field")
@pytest.mark.administration
@pytest.mark.extensions
def test_extension_clear_filters(opened_extensions_page):
    existing_extension_number = get_existing_extension_number()
    extensions_page = opened_extensions_page.search_for_extension_number(existing_extension_number)
    search_button = extensions_page.driver.find_element(*extensions_page.SEARCH_BUTTON)
    time.sleep(1)  # Wait for search results to update
    clear_filters_button = extensions_page.driver.find_element(*extensions_page.CLEAR_FILTERS)
    clear_filters_button.click()
    search_button.click()
    time.sleep(2)  # Wait for table to refresh after clearing filters
    rows = extensions_page.visible_table_rows()
    assert len(rows) > 1, "No results found in the table after clearing filters, expected to see all extensions."


@testcase("808-3036", "Verify Company Extensions: Columns - Visible columns can be changed from dropdown")
@pytest.mark.administration
@pytest.mark.extensions
def test_visible_columns_can_be_changed_from_dropdown(opened_extensions_page):
    opened_extensions_page.set_all_column_visibility(True)
    initial_column_count = opened_extensions_page.visible_table_column_count()
    assert initial_column_count > 0, "Expected visible table columns before changing column visibility."

    try:
        opened_extensions_page.open_column_visibility_dropdown()
        time.sleep(2)
        assert opened_extensions_page.column_visibility_option_count() == 7, "Expected 7 column visibility options."
        column_labels = opened_extensions_page.column_visibility_option_labels()
        opened_extensions_page.close_column_visibility_dropdown()
        time.sleep(2)

        opened_extensions_page.set_all_column_visibility(False)
        time.sleep(2)
        opened_extensions_page.wait_for_visible_table_column_count(0)

        opened_extensions_page.set_columns_visibility(column_labels[:3], True)
        time.sleep(2)
        opened_extensions_page.wait_for_visible_table_column_count(3)

        opened_extensions_page.set_columns_visibility(column_labels[3:], True)
        time.sleep(2)
        opened_extensions_page.wait_for_visible_table_column_count(initial_column_count)
    finally:
        opened_extensions_page.set_all_column_visibility(True)
        time.sleep(2)


@testcase("808-3037", "Verify Company Extensions: Export - Export downloads extension data")
@pytest.mark.administration
@pytest.mark.extensions
def test_export_downloads_extension_data(opened_extensions_page, download_dir):
    existing_extension_number = str(get_existing_extension_number())

    opened_extensions_page.set_all_column_visibility(True)
    time.sleep(2)

    opened_extensions_page.export_extensions()
    time.sleep(2)

    csv_path = wait_for_csv_download(download_dir)
    rows = read_csv_rows(csv_path)

    assert len(rows) > 1, f"Expected exported CSV to contain header and table data, got: {rows}"
    header = [cell.strip() for cell in rows[0]]
    missing_columns = [column for column in EXPECTED_EXPORT_COLUMNS if column not in header]
    assert not missing_columns, f"Exported CSV is missing columns: {missing_columns}. Header was: {header}"

    exported_extensions = column_values(rows, "Extension")
    assert existing_extension_number in exported_extensions, (
        f"Expected existing extension '{existing_extension_number}' to appear in exported CSV. "
        f"Exported extensions included: {exported_extensions[:10]}"
    )

    real_extensions = column_values(rows, "Real Extension")
    assert any(real_extensions), "Expected exported CSV to contain at least one Real Extension value."


@testcase("808-3038", "Verify Company Extensions: Export - Export contains records from all pages")
@pytest.mark.administration
@pytest.mark.extensions
def test_export_contains_records_from_all_pages(opened_extensions_page, download_dir):
    opened_extensions_page.set_all_column_visibility(True)
    time.sleep(2)

    table_records = opened_extensions_page.all_visible_table_records()
    time.sleep(2)
    assert table_records, "Expected visible table records from at least one page before export."

    opened_extensions_page.export_extensions()
    time.sleep(2)

    csv_path = wait_for_csv_download(download_dir)
    rows = read_csv_rows(csv_path)
    exported_records = csv_records(rows)
    exported_by_extension = records_by_column(exported_records, "Extension")

    missing_extensions = [
        record["Extension"]
        for record in table_records
        if record.get("Extension") not in exported_by_extension
    ]
    assert not missing_extensions, (
        "Exported CSV is missing extensions visible across paginated table pages: "
        f"{missing_extensions[:10]}"
    )

    for table_record in table_records:
        exported_record = exported_by_extension[table_record["Extension"]]
        for table_column, export_column in EXPORT_COLUMN_ALIASES.items():
            if table_column not in table_record or export_column not in exported_record:
                continue
            assert normalize_record_value(table_record[table_column]) == normalize_record_value(exported_record[export_column]), (
                f"Exported value mismatch for extension {table_record['Extension']} column {export_column}. "
                f"Table value: {table_record[table_column]!r}; CSV value: {exported_record[export_column]!r}"
            )


@testcase("808-3039", "Verify Company Extensions: Edit - Edit popup opens with existing record data")
@pytest.mark.administration
@pytest.mark.extensions
def test_edit_popup_opens_with_existing_record_data(opened_extensions_page):
    opened_extensions_page.set_all_column_visibility(True)
    time.sleep(2)
    opened_extensions_page.go_to_first_page()
    time.sleep(2)

    first_row_text = opened_extensions_page.first_visible_table_row_text()
    assert first_row_text, "Expected at least one extension row before opening Edit popup."

    opened_extensions_page.open_first_row_edit_popup()
    time.sleep(2)

    try:
        assert opened_extensions_page.is_add_popup_open(), "Edit popup did not open."
        popup_values = opened_extensions_page.popup_field_values()
        assert popup_values, "Expected Edit popup to show existing record values."

        popup_password = opened_extensions_page.edit_popup_password_value()
        assert popup_password in first_row_text, (
            f"Edit popup Password value is not visible in the selected table row. "
            f"Popup value: {popup_password!r}; row text: {first_row_text!r}"
        )

        popup_type = opened_extensions_page.edit_popup_type_value()
        assert popup_type in first_row_text, (
            f"Edit popup Type value is not visible in the selected table row. "
            f"Popup value: {popup_type!r}; row text: {first_row_text!r}"
        )

        popup_transport_type = opened_extensions_page.edit_popup_transport_type_value()
        assert popup_transport_type in first_row_text, (
            f"Edit popup Transport type value is not visible in the selected table row. "
            f"Popup value: {popup_transport_type!r}; row text: {first_row_text!r}"
        )
    finally:
        time.sleep(2)
        opened_extensions_page.close_add_popup()


@testcase("808-3040", "Verify Company Extensions: Edit - Generate Password checkbox hides password field")
@pytest.mark.administration
@pytest.mark.extensions
def test_edit_generate_password_checkbox_hides_password_field(opened_extensions_page):
    extension_number = add_extension_from_ui(opened_extensions_page, get_non_existing_extension_number(), password="Test1234")

    opened_extensions_page.set_all_column_visibility(True)
    time.sleep(2)
    opened_extensions_page.search_for_extension_number(extension_number)
    time.sleep(2)

    edit_record = opened_extensions_page.first_visible_table_record()
    assert edit_record and edit_record["Extension"] == extension_number, (
        f"Expected added extension '{extension_number}' before editing, got: {edit_record}"
    )

    opened_extensions_page.open_first_row_edit_popup()
    time.sleep(2)

    try:
        assert opened_extensions_page.is_add_popup_open(), "Edit popup did not open."
        old_password = opened_extensions_page.edit_popup_password_value()
        assert opened_extensions_page.is_edit_popup_password_visible(), "Password field should be visible before Generate Password is checked."

        opened_extensions_page.toggle_edit_popup_generate_password()
        time.sleep(2)

        assert not opened_extensions_page.is_edit_popup_password_visible(), "Password field should be hidden after Generate Password is checked."
        opened_extensions_page.submit_edit_popup()
        time.sleep(2)
    finally:
        if opened_extensions_page.is_add_popup_open():
            opened_extensions_page.close_add_popup()

    opened_extensions_page.search_for_extension_number(extension_number)
    time.sleep(2)
    opened_extensions_page.open_first_row_edit_popup()
    time.sleep(2)
    try:
        generated_password = opened_extensions_page.edit_popup_password_value()
        assert generated_password, "Expected generated password to be visible after reopening Edit popup."
        assert generated_password != old_password, (
            f"Expected generated password to differ from old password {old_password!r}, got {generated_password!r}."
        )
    finally:
        time.sleep(2)
        opened_extensions_page.close_add_popup()
        row_delete_extension_from_ui(opened_extensions_page, extension_number)


@testcase("808-3041", "Verify Company Extensions: Edit - Existing extension can be edited successfully")
@pytest.mark.administration
@pytest.mark.extensions
def test_existing_extension_can_be_edited_successfully(opened_extensions_page):
    extension_number = add_extension_from_ui(opened_extensions_page, get_non_existing_extension_number(), password="Test1234")

    opened_extensions_page.set_all_column_visibility(True)
    time.sleep(2)
    opened_extensions_page.search_for_extension_number(extension_number)
    time.sleep(2)

    original_record = opened_extensions_page.last_visible_table_record()
    assert original_record and original_record["Extension"] == extension_number, (
        f"Expected added extension '{extension_number}' before editing, got: {original_record}"
    )

    opened_extensions_page.open_first_row_edit_popup()
    time.sleep(2)

    try:
        assert opened_extensions_page.is_add_popup_open(), "Edit popup did not open."
        original_password = opened_extensions_page.edit_popup_password_value()
        updated_password = f"{original_password}!"

        updated_type = opened_extensions_page.choose_different_extension_type()
        time.sleep(2)
        updated_transport_type = opened_extensions_page.choose_different_transport_type()
        time.sleep(2)
        opened_extensions_page.set_edit_popup_password(updated_password)
        time.sleep(2)

        opened_extensions_page.submit_edit_popup()
        time.sleep(2)
    finally:
        if opened_extensions_page.is_add_popup_open():
            opened_extensions_page.close_add_popup()

    opened_extensions_page.search_for_extension_number(extension_number)
    time.sleep(2)

    updated_record = opened_extensions_page.first_visible_table_record()
    assert updated_record, f"Expected edited extension '{extension_number}' to remain visible after saving."
    assert updated_record["Extension"] == extension_number, (
        f"Expected to find edited extension '{extension_number}', but found: {updated_record}"
    )
    assert updated_record["Type"] == updated_type, (
        f"Type was not updated in table. Expected {updated_type!r}, got {updated_record['Type']!r}."
    )
    assert updated_record["Transport type"] == updated_transport_type, (
        "Transport type was not updated in table. "
        f"Expected {updated_transport_type!r}, got {updated_record['Transport type']!r}."
    )

    opened_extensions_page.open_first_row_edit_popup()
    time.sleep(2)
    try:
        saved_password = opened_extensions_page.edit_popup_password_value()
        assert saved_password == updated_password, (
            f"Password was not updated in Edit popup. Expected {updated_password!r}, got {saved_password!r}."
        )
    finally:
        time.sleep(2)
        opened_extensions_page.close_add_popup()
        row_delete_extension_from_ui(opened_extensions_page, extension_number)


@testcase("808-3042", "Verify Company Extensions: Edit - Cancel keeps original extension values")
@pytest.mark.administration
@pytest.mark.extensions
def test_edit_cancel_keeps_original_extension_values(opened_extensions_page):
    extension_number = add_extension_from_ui(opened_extensions_page, get_non_existing_extension_number(), password="Test1234")

    opened_extensions_page.set_all_column_visibility(True)
    time.sleep(2)
    opened_extensions_page.search_for_extension_number(extension_number)
    time.sleep(2)

    original_record = opened_extensions_page.last_visible_table_record()
    assert original_record and original_record["Extension"] == extension_number, (
        f"Expected added extension '{extension_number}' before editing, got: {original_record}"
    )

    opened_extensions_page.open_first_row_edit_popup()
    time.sleep(2)

    try:
        assert opened_extensions_page.is_add_popup_open(), "Edit popup did not open."
        original_password = opened_extensions_page.edit_popup_password_value()
        assert original_password, "Expected existing Password value before testing Cancel."

        opened_extensions_page.choose_different_extension_type()
        time.sleep(2)
        opened_extensions_page.choose_different_transport_type()
        time.sleep(2)
        opened_extensions_page.set_edit_popup_password(f"Cancel{int(time.time())}")
        time.sleep(2)
        opened_extensions_page.close_add_popup()
        time.sleep(2)
    finally:
        if opened_extensions_page.is_add_popup_open():
            opened_extensions_page.close_add_popup()

    opened_extensions_page.search_for_extension_number(extension_number)
    time.sleep(2)

    current_record = opened_extensions_page.first_visible_table_record()
    assert current_record, f"Expected extension '{extension_number}' to remain visible after cancelling Edit."
    assert current_record["Extension"] == extension_number, (
        f"Expected to find extension '{extension_number}', but found: {current_record}"
    )
    assert current_record["Type"] == original_record["Type"], (
        f"Type changed after Cancel. Expected {original_record['Type']!r}, got {current_record['Type']!r}."
    )
    assert current_record["Transport type"] == original_record["Transport type"], (
        "Transport type changed after Cancel. "
        f"Expected {original_record['Transport type']!r}, got {current_record['Transport type']!r}."
    )

    opened_extensions_page.open_first_row_edit_popup()
    time.sleep(2)
    try:
        current_password = opened_extensions_page.edit_popup_password_value()
        assert current_password == original_password, (
            f"Password changed after Cancel. Expected {original_password!r}, got {current_password!r}."
        )
    finally:
        time.sleep(2)
        opened_extensions_page.close_add_popup()
        row_delete_extension_from_ui(opened_extensions_page, extension_number)


@testcase("808-3043", "Verify Company Extensions: Add - Add popup opens correctly")
@pytest.mark.administration
@pytest.mark.extensions
def test_add_popup_opens_correctly(opened_extensions_page):
    opened_extensions_page.open_add_popup()
    try:
        assert opened_extensions_page.has_add_popup_controls(), "Not all Add popup controls are visible."
    finally:
        opened_extensions_page.close_add_popup()


@testcase("808-3044", "Verify Company Extensions: Add - Required fields validation works in Add popup")
@pytest.mark.administration
@pytest.mark.extensions
def test_add_required_fields_validation_works(opened_extensions_page):
    opened_extensions_page.open_add_popup()
    try:
        opened_extensions_page.touch_add_popup_required_fields()
        time.sleep(2)  # Wait for validation to trigger
        assert opened_extensions_page.is_add_popup_submit_disabled(), "Submit should be disabled when required Add fields are empty."
        time.sleep(2)  # Wait for validation messages to appear
        assert opened_extensions_page.add_popup_number_fields_are_empty(), "Start and End should stay empty while required validation is shown."
    finally:
        time.sleep(2)  # Wait before closing the popup to ensure validation messages are visible    
        opened_extensions_page.close_add_popup()


@testcase("808-3045", "Verify Company Extensions: Add - Generate Password checkbox hides password field in Add popup")
@pytest.mark.administration
@pytest.mark.extensions
def test_add_generate_password_checkbox_hides_password_field(opened_extensions_page):
    opened_extensions_page.clear_search_and_submit()
    time.sleep(2)
    opened_extensions_page.open_add_popup()
    time.sleep(2)

    try:
        assert opened_extensions_page.is_add_popup_open(), "Add popup did not open."
        assert opened_extensions_page.is_add_popup_password_visible(), "Password field should be visible before Generate Password is checked."

        opened_extensions_page.toggle_add_popup_generate_password()
        time.sleep(2)

        assert not opened_extensions_page.is_add_popup_password_visible(), "Password field should be hidden after Generate Password is checked."
    finally:
        time.sleep(2)
        opened_extensions_page.close_add_popup()


@testcase("808-3046", "Verify Company Extensions: Add - New extension range can be added successfully")
@pytest.mark.administration
@pytest.mark.extensions
def test_adding_non_existent_extension(opened_extensions_page):
    extension_number = add_extension_from_ui(opened_extensions_page, get_non_existing_extension_number())
    try:
        opened_extensions_page.search_for_extension_number(extension_number)
        time.sleep(2)
        assert opened_extensions_page.has_visible_extension(extension_number), (
            f"Expected to find the newly added extension '{extension_number}' after searching, but it was not found."
        )
    finally:
        row_delete_extension_from_ui(opened_extensions_page, extension_number)


@pytest.mark.administration
@pytest.mark.extensions
def test_adding_non_existent_extension_range(opened_extensions_page):
    start_extension, end_extension = get_non_existing_extension_range(size=5)
    start_extension, end_extension = add_extension_range_from_ui(
        opened_extensions_page,
        start_extension,
        end_extension,
    )

    try:
        for extension_number in range(int(start_extension), int(end_extension) + 1):
            opened_extensions_page.search_for_extension_number(extension_number)
            time.sleep(2)
            assert opened_extensions_page.has_visible_extension(extension_number), (
                f"Expected extension '{extension_number}' from added range to be visible."
            )
    finally:
        bottom_delete_extension_range_from_ui(opened_extensions_page, start_extension, end_extension)


@testcase("808-3047", "Verify Company Extensions: Mobile - Mobile popup opens for selected extension")
@pytest.mark.administration
@pytest.mark.extensions
def test_mobile_popup_opens_for_selected_extension(opened_extensions_page):
    opened_extensions_page.clear_search_and_submit()
    time.sleep(2)
    opened_extensions_page.go_to_first_page()
    time.sleep(2)

    opened_extensions_page.open_first_row_mobile_popup()
    time.sleep(2)

    try:
        assert opened_extensions_page.is_mobile_popup_open(), "Mobile popup did not open."
        assert opened_extensions_page.has_mobile_popup_controls(), "Not all Mobile popup controls are visible."
    finally:
        time.sleep(2)
        opened_extensions_page.close_mobile_popup()


@testcase("808-3048", "Verify Company Extensions: Mobile - Number can be added and active phone selected")
@pytest.mark.administration
@pytest.mark.extensions
@not_automated
def test_mobile_number_can_be_added_and_active_phone_selected(opened_extensions_page):
    skip_not_automated_yet()


@testcase("808-3049", "Verify Company Extensions: Mobile - Cancel keeps phone data unchanged")
@pytest.mark.administration
@pytest.mark.extensions
@not_automated
def test_mobile_cancel_keeps_phone_data_unchanged(opened_extensions_page):
    skip_not_automated_yet()


@testcase("808-3050", "Verify Company Extensions: Delete - Cancel in row delete confirmation keeps record")
@pytest.mark.administration
@pytest.mark.extensions
def test_row_delete_cancel_keeps_record(opened_extensions_page):
    extension_number = add_extension_from_ui(opened_extensions_page, get_non_existing_extension_number())

    assert opened_extensions_page.has_visible_extension(extension_number), (
        f"Expected disposable extension '{extension_number}' before opening row delete confirmation."
    )
    opened_extensions_page.open_first_row_delete_confirmation()
    time.sleep(2)
    try:
        assert opened_extensions_page.is_delete_confirmation_open(), "Row delete confirmation did not open."
        opened_extensions_page.cancel_delete_confirmation()
        time.sleep(2)
    finally:
        if opened_extensions_page.is_delete_confirmation_open():
            opened_extensions_page.cancel_delete_confirmation()

    assert opened_extensions_page.has_visible_extension(extension_number), (
        f"Extension '{extension_number}' disappeared after cancelling row delete."
    )

    opened_extensions_page.open_first_row_delete_confirmation()
    time.sleep(2)
    opened_extensions_page.confirm_delete_confirmation()
    time.sleep(2)
    opened_extensions_page.clear_search_and_submit()
    time.sleep(2)


@testcase("808-3051", "Verify Company Extensions: Delete - Row delete removes selected extension")
@pytest.mark.administration
@pytest.mark.extensions
def test_row_delete_removes_selected_extension(opened_extensions_page):
    extension_number = add_extension_from_ui(opened_extensions_page, get_non_existing_extension_number())

    assert opened_extensions_page.has_visible_extension(extension_number), (
        f"Expected disposable extension '{extension_number}' before row delete."
    )
    opened_extensions_page.open_first_row_delete_confirmation()
    time.sleep(2)
    assert opened_extensions_page.is_delete_confirmation_open(), "Row delete confirmation did not open."
    opened_extensions_page.confirm_delete_confirmation()
    time.sleep(2)

    opened_extensions_page.search_for_extension_number(extension_number)
    time.sleep(2)
    assert not opened_extensions_page.has_visible_extension(extension_number), (
        f"Deleted extension '{extension_number}' is still visible after row delete."
    )
    opened_extensions_page.clear_search_and_submit()
    time.sleep(2)


@testcase("808-3052", "Verify Company Extensions: Delete - Bottom delete popup opens for extension range")
@pytest.mark.administration
@pytest.mark.extensions
def test_bottom_delete_popup_opens_for_extension_range(opened_extensions_page):
    start_extension, end_extension = get_non_existing_extension_range(size=5)
    start_extension, end_extension = add_extension_range_from_ui(
        opened_extensions_page,
        start_extension,
        end_extension,
    )

    opened_extensions_page.open_bottom_delete_popup()
    time.sleep(2)
    try:
        assert opened_extensions_page.is_add_popup_open(), "Bottom delete range popup did not open."
        assert opened_extensions_page.add_popup_number_fields_are_empty(), (
            "Bottom delete range fields should be empty when the popup opens."
        )
    finally:
        opened_extensions_page.close_add_popup()
        time.sleep(2)

    opened_extensions_page.search_for_extension_number(start_extension)
    time.sleep(2)
    assert opened_extensions_page.has_visible_extension(start_extension), (
        f"Extension '{start_extension}' disappeared after opening and rejecting bottom delete confirmation."
    )

    bottom_delete_extension_range_from_ui(opened_extensions_page, start_extension, end_extension)


@testcase("808-3053", "Verify Company Extensions: Delete - Cancel in bottom delete keeps extension range")
@pytest.mark.administration
@pytest.mark.extensions
def test_bottom_delete_cancel_keeps_extension_range(opened_extensions_page):
    start_extension, end_extension = get_non_existing_extension_range(size=5)
    start_extension, end_extension = add_extension_range_from_ui(
        opened_extensions_page,
        start_extension,
        end_extension,
    )

    opened_extensions_page.open_bottom_delete_popup()
    time.sleep(2)
    try:
        assert opened_extensions_page.is_add_popup_open(), "Bottom delete range popup did not open."
        opened_extensions_page.fill_add_popup(start_extension, end_extension)
        time.sleep(2)
        opened_extensions_page.close_add_popup()
        time.sleep(2)
    finally:
        if opened_extensions_page.is_add_popup_open():
            opened_extensions_page.close_add_popup()

    opened_extensions_page.search_for_extension_number(start_extension)
    time.sleep(2)
    assert opened_extensions_page.has_visible_extension(start_extension), (
        f"Extension '{start_extension}' disappeared after cancelling bottom delete."
    )

    opened_extensions_page.search_for_extension_number(end_extension)
    time.sleep(2)
    assert opened_extensions_page.has_visible_extension(end_extension), (
        f"Extension '{end_extension}' disappeared after cancelling bottom delete."
    )

    bottom_delete_extension_range_from_ui(opened_extensions_page, start_extension, end_extension)


@testcase("808-3054", "Verify Company Extensions: Delete - Bottom delete removes selected extension range")
@pytest.mark.administration
@pytest.mark.extensions
def test_bottom_delete_removes_selected_extension_range(opened_extensions_page):
    start_extension, end_extension = get_non_existing_extension_range(size=5)
    start_extension, end_extension = add_extension_range_from_ui(
        opened_extensions_page,
        start_extension,
        end_extension,
    )

    opened_extensions_page.open_bottom_delete_popup()
    time.sleep(2)
    try:
        assert opened_extensions_page.is_add_popup_open(), "Bottom delete range popup did not open."
        opened_extensions_page.fill_add_popup(start_extension, end_extension)
        time.sleep(2)
        opened_extensions_page.submit_popup_and_wait_closed()
        time.sleep(2)
    finally:
        if opened_extensions_page.is_add_popup_open():
            opened_extensions_page.close_add_popup()

    for extension_number in range(int(start_extension), int(end_extension) + 1):
        opened_extensions_page.search_for_extension_number(extension_number)
        time.sleep(2)
        assert not opened_extensions_page.has_visible_extension(extension_number), (
            f"Extension '{extension_number}' is still visible after bottom delete range removal."
        )
    opened_extensions_page.clear_search_and_submit()
    time.sleep(2)


@testcase("808-3055", "Verify Company Extensions: Pagination - Page navigation and items per page work correctly")
@pytest.mark.administration
@pytest.mark.extensions
def test_page_navigation_and_items_per_page_work_correctly(opened_extensions_page):
    opened_extensions_page.clear_search_and_submit()
    time.sleep(2)
    opened_extensions_page.go_to_first_page()
    time.sleep(2)

    first_page_number = opened_extensions_page.current_page_number()
    first_page_records = opened_extensions_page.visible_table_records()
    assert first_page_records, "Expected records on the first page before testing pagination."

    if not opened_extensions_page.go_to_next_page():
        pytest.skip("Only one Extensions page is available; pagination navigation cannot be verified.")
    time.sleep(2)

    second_page_number = opened_extensions_page.current_page_number()
    second_page_records = opened_extensions_page.visible_table_records()
    assert second_page_records, "Expected records on the next page after pagination."
    assert second_page_number != first_page_number or second_page_records != first_page_records, (
        "Expected paginator to move to another page or show different records."
    )

    assert opened_extensions_page.go_to_previous_page(), "Expected Previous Page to be available after moving forward."
    time.sleep(2)
    assert opened_extensions_page.current_page_number() == first_page_number, "Expected paginator to return to the first page."


@testcase("808-3056", "Verify Company Extensions: Publish - Publish applies saved changes successfully")
@pytest.mark.administration
@pytest.mark.extensions
def test_publish_applies_saved_changes_successfully(opened_extensions_page):
    opened_extensions_page.clear_search_and_submit()
    time.sleep(2)
    opened_extensions_page.click_publish()
    time.sleep(2)

    if opened_extensions_page.is_delete_confirmation_open():
        opened_extensions_page.confirm_delete_confirmation()
        time.sleep(2)

    assert opened_extensions_page.is_loaded(), "Extensions page did not remain loaded after publishing changes."
