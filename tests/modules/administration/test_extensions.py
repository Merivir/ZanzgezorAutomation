from tests.config.automation_config import (
    load_config,
    get_active_client,
    get_client_config,
    get_user_credentials,
)
from tests.pages.login_page import LoginPage
from tests.pages.portal_page import PortalPage
from tests.pages.extensions_page import ExtensionsPage


def test_extensions_page_opens_correctly(driver, wait):
    # Load configuration
    config = load_config()
    active_client = get_active_client(config)
    client_config = get_client_config(config, active_client)
    creadentials = get_user_credentials(config, "default")
    
    login_page = LoginPage(driver, wait, client_config["base_url"])
    portal_page = PortalPage(driver, wait)
    extensions_page = ExtensionsPage(driver, wait)

    login_page.open()
    login_page.login(creadentials["username"], creadentials["password"])

    portal_page.wait_until_loaded()
    portal_page.open_administration()
    portal_page.open_extensions()

    extensions_page.wait_until_loaded()
    assert extensions_page.is_loaded(), "Extensions page did not load correctly"