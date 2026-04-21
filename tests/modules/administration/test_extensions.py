import pytest
import time 

from tests.config.automation_config import (
    load_config,
    get_active_client,
    get_client_config,
    get_user_credentials,
)
from tests.pages import extensions_page
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

@pytest.mark.skipif(False, reason="Temporarily disabled")
def test_extensions_page_opens_correctly(opened_extensions_page):
    assert opened_extensions_page.is_loaded(), "Extensions page did not load correctly."

@pytest.mark.skipif(True, reason="Temporarily disabled")
def test_extensions_page_main_controls(opened_extensions_page):
    assert opened_extensions_page.has_main_controls(), "Not all main controls are present on the Extensions page."

@pytest.mark.skipif(True, reason="Temporarily disabled")
def test_extension_search_functionality(opened_extensions_page):
    existing_extension_number = get_existing_extension_number()
    extensions_page = opened_extensions_page.search_for_extension_number(existing_extension_number)
    rows = extensions_page.visible_table_rows()
    time.sleep(2)  # Wait for search results to update
    assert len(rows) > 0, f"No results found in the table after searching for extension '{existing_extension_number}'."

@pytest.mark.skipif(False, reason="Temporarily disabled")
def test_extension_search_no_results(opened_extensions_page):
    non_existing_extension_number = get_non_existing_extension_number()
    extensions_page = opened_extensions_page.search_for_extension_number(non_existing_extension_number)
    time.sleep(2)  # Wait for search results to update
    message = extensions_page.driver.find_elements(*extensions_page.EMPTY_TABLE_MESSAGE)
    assert message[0].text.strip() == "No data to display!", "Expected 'No data' message when searching for non-existent extension, but it was not found."  

@pytest.mark.skipif(False, reason="Temporarily disabled")
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

@pytest.mark.skipif(False, reason="Temporarily disabled")
def test_adding_non_existent_extension(opened_extensions_page):
    non_existing_extension_number = get_non_existing_extension_number()
    opened_extensions_page.open_add_popup()
    opened_extensions_page.choose_extension_type("pjsip")
    opened_extensions_page.choose_transport_type("udp")
    opened_extensions_page.fill_add_popup(non_existing_extension_number, non_existing_extension_number, password="Test1234")
    opened_extensions_page.submit_add_popup()
    time.sleep(2)  # Wait for the new extension to be added and the table to refresh
    assert opened_extensions_page.has_single_result_with_extension(str(non_existing_extension_number)), f"Expected to find the newly added extension '{non_existing_extension_number}' in the table, but it was not found."