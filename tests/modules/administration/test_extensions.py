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

@pytest.mark.skipif(False, reason="Temporarily disabled")
def test_extensions_page_opens_correctly(opened_extensions_page):
    assert opened_extensions_page.is_loaded(), "Extensions page did not load correctly."

@pytest.mark.skipif(True, reason="Temporarily disabled")
def test_extensions_page_main_controls(opened_extensions_page):
    assert opened_extensions_page.has_main_controls(), "Not all main controls are present on the Extensions page."

@pytest.mark.skipif(True, reason="Temporarily disabled")
def test_extension_search_functionality(opened_extensions_page):
    extensions_page = opened_extensions_page
    search_input = extensions_page.driver.find_element(*extensions_page.SEARCH_INPUT)

    """
    here im going to write 200 but here we should latly check in db active extensions and 
    write the search query based on that, but for now i will just write 200 and check if we
    get results in the table after searching for 200.
    """
    search_input.send_keys("200")

    search_button = extensions_page.driver.find_element(*extensions_page.SEARCH_BUTTON)
    search_button.click()
    rows = extensions_page.visible_table_rows()
    time.sleep(2)  # Wait for search results to update
    assert len(rows) > 0, "No results found in the table after searching for '200'."

@pytest.mark.skipif(False, reason="Temporarily disabled")
def test_extension_search_no_results(opened_extensions_page):
    """
    Here im going to search for a random string that is
    not an extension and check that we get no results in the table.
    """
    extensions_page = opened_extensions_page
    search_input = extensions_page.driver.find_element(*extensions_page.SEARCH_INPUT)
    search_input.clear()
    search_input.send_keys("199") # Assuming 199 is not an active extension, this should yield no results.
    search_button = extensions_page.driver.find_element(*extensions_page.SEARCH_BUTTON)
    search_button.click()   
    time.sleep(2)  # Wait for search results to update
    message = extensions_page.driver.find_elements(*extensions_page.EMPTY_TABLE_MESSAGE)
    assert message[0].text.strip() == "No data to display!", "Expected 'No data' message when searching for non-existent extension, but it was not found."  

@pytest.mark.skipif(False, reason="Temporarily disabled")
def test_extension_clear_filters(opened_extensions_page):
    extensions_page = opened_extensions_page
    search_input = extensions_page.driver.find_element(*extensions_page.SEARCH_INPUT)
    search_input.clear()
    search_input.send_keys("200")
    search_button = extensions_page.driver.find_element(*extensions_page.SEARCH_BUTTON)
    search_button.click()
    time.sleep(1)  # Wait for search results to update
    clear_filters_button = extensions_page.driver.find_element(*extensions_page.CLEAR_FILTERS)
    clear_filters_button.click()
    search_button.click()
    time.sleep(2)  # Wait for table to refresh after clearing filters
    rows = extensions_page.visible_table_rows()
    assert len(rows) > 1, "No results found in the table after clearing filters, expected to see all extensions."

