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
    active_extension_numbers = get_extension_numbers(connection)
    if not active_extension_numbers:
        pytest.skip("No active extensions found in the database to test with.")
    # Generate a random extension number that is not in the list of active extensions
    non_existing_extension_number = int(active_extension_numbers[-1]) + 1  # Start with the last active extension number
    return non_existing_extension_number


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
@not_automated
def test_visible_columns_can_be_changed_from_dropdown(opened_extensions_page):
    skip_not_automated_yet()


@testcase("808-3037", "Verify Company Extensions: Export - Export downloads extension data")
@pytest.mark.administration
@pytest.mark.extensions
@not_automated
def test_export_downloads_extension_data(opened_extensions_page):
    skip_not_automated_yet()


@testcase("808-3038", "Verify Company Extensions: Export - Export contains records from all pages")
@pytest.mark.administration
@pytest.mark.extensions
@not_automated
def test_export_contains_records_from_all_pages(opened_extensions_page):
    skip_not_automated_yet()


@testcase("808-3039", "Verify Company Extensions: Edit - Edit popup opens with existing record data")
@pytest.mark.administration
@pytest.mark.extensions
@not_automated
def test_edit_popup_opens_with_existing_record_data(opened_extensions_page):
    skip_not_automated_yet()


@testcase("808-3040", "Verify Company Extensions: Edit - Generate Password checkbox hides password field")
@pytest.mark.administration
@pytest.mark.extensions
@not_automated
def test_edit_generate_password_checkbox_hides_password_field(opened_extensions_page):
    skip_not_automated_yet()


@testcase("808-3041", "Verify Company Extensions: Edit - Existing extension can be edited successfully")
@pytest.mark.administration
@pytest.mark.extensions
@not_automated
def test_existing_extension_can_be_edited_successfully(opened_extensions_page):
    skip_not_automated_yet()


@testcase("808-3042", "Verify Company Extensions: Edit - Cancel keeps original extension values")
@pytest.mark.administration
@pytest.mark.extensions
@not_automated
def test_edit_cancel_keeps_original_extension_values(opened_extensions_page):
    skip_not_automated_yet()


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
        assert opened_extensions_page.is_add_popup_submit_disabled(), "Submit should be disabled when required Add fields are empty."
        assert opened_extensions_page.add_popup_number_fields_are_empty(), "Start and End should stay empty while required validation is shown."
    finally:
        opened_extensions_page.close_add_popup()


@testcase("808-3045", "Verify Company Extensions: Add - Generate Password checkbox hides password field in Add popup")
@pytest.mark.administration
@pytest.mark.extensions
@not_automated
def test_add_generate_password_checkbox_hides_password_field(opened_extensions_page):
    skip_not_automated_yet()


@testcase("808-3046", "Verify Company Extensions: Add - New extension range can be added successfully")
@pytest.mark.administration
@pytest.mark.extensions
def test_adding_non_existent_extension(opened_extensions_page):
    non_existing_extension_number = get_non_existing_extension_number()
    opened_extensions_page.open_add_popup()
    time.sleep(2)
    opened_extensions_page.choose_extension_type("pjsip")
    time.sleep(2)
    opened_extensions_page.choose_transport_type("udp")
    time.sleep(2)
    opened_extensions_page.fill_add_popup(non_existing_extension_number, non_existing_extension_number, password="Test1234")
    time.sleep(2)
    opened_extensions_page.submit_add_popup()
    time.sleep(2)  # Wait for the new extension to be added and the table to refresh
    opened_extensions_page.go_to_last_page()
    assert opened_extensions_page.has_visible_extension(non_existing_extension_number), f"Expected to find the newly added extension '{non_existing_extension_number}' on the last page, but it was not found."


@testcase("808-3047", "Verify Company Extensions: Mobile - Mobile popup opens for selected extension")
@pytest.mark.administration
@pytest.mark.extensions
@not_automated
def test_mobile_popup_opens_for_selected_extension(opened_extensions_page):
    skip_not_automated_yet()


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
@not_automated
def test_row_delete_cancel_keeps_record(opened_extensions_page):
    skip_not_automated_yet()


@testcase("808-3051", "Verify Company Extensions: Delete - Row delete removes selected extension")
@pytest.mark.administration
@pytest.mark.extensions
@not_automated
def test_row_delete_removes_selected_extension(opened_extensions_page):
    skip_not_automated_yet()


@testcase("808-3052", "Verify Company Extensions: Delete - Bottom delete popup opens for extension range")
@pytest.mark.administration
@pytest.mark.extensions
@not_automated
def test_bottom_delete_popup_opens_for_extension_range(opened_extensions_page):
    skip_not_automated_yet()


@testcase("808-3053", "Verify Company Extensions: Delete - Cancel in bottom delete keeps extension range")
@pytest.mark.administration
@pytest.mark.extensions
@not_automated
def test_bottom_delete_cancel_keeps_extension_range(opened_extensions_page):
    skip_not_automated_yet()


@testcase("808-3054", "Verify Company Extensions: Delete - Bottom delete removes selected extension range")
@pytest.mark.administration
@pytest.mark.extensions
@not_automated
def test_bottom_delete_removes_selected_extension_range(opened_extensions_page):
    skip_not_automated_yet()


@testcase("808-3055", "Verify Company Extensions: Pagination - Page navigation and items per page work correctly")
@pytest.mark.administration
@pytest.mark.extensions
@not_automated
def test_page_navigation_and_items_per_page_work_correctly(opened_extensions_page):
    skip_not_automated_yet()


@testcase("808-3056", "Verify Company Extensions: Publish - Publish applies saved changes successfully")
@pytest.mark.administration
@pytest.mark.extensions
@not_automated
def test_publish_applies_saved_changes_successfully(opened_extensions_page):
    skip_not_automated_yet()
