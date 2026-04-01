import pytest

from tests.config.modules import is_module_enabled
from tests.pages.extensions_page import ExtensionsPage
from tests.pages.login_page import LoginPage
from tests.pages.portal_page import PortalPage


def _require_role(credentials: dict, role: str):
    role_data = credentials.get(role, {})
    username = role_data.get("username", "")
    password = role_data.get("password", "")
    if not username or not password:
        pytest.skip(f"Missing credentials for '{role}'.")
    return username, password


@pytest.mark.parametrize("role", ["admin", "supervisor"])
def test_extensions_page_can_be_opened_from_administration_menu(
    driver, wait, base_url, credentials, module_flags, role
):
    if not is_module_enabled(module_flags, "administration"):
        pytest.skip("Administration module check is disabled in config.")

    username, password = _require_role(credentials, role)

    login = LoginPage(driver, wait, base_url)
    login.open()
    login.login(username, password)

    portal = PortalPage(driver, wait)
    portal.wait_until_loaded()
    portal.open_administration()
    portal.open_extensions()

    extensions = ExtensionsPage(driver, wait)
    extensions.wait_until_loaded()

    assert "extension" in driver.page_source.lower() or "extension" in driver.current_url.lower()
    assert extensions.has_main_controls(), "Extensions page opened, but main controls were not all found."


def test_agent_cannot_open_extensions_page(driver, wait, base_url, credentials, module_flags):
    if not is_module_enabled(module_flags, "administration"):
        pytest.skip("Administration module check is disabled in config.")

    username, password = _require_role(credentials, "agent")

    login = LoginPage(driver, wait, base_url)
    login.open()
    login.login(username, password)

    portal = PortalPage(driver, wait)
    portal.wait_until_loaded()

    if driver.find_elements(*PortalPage.ADMINISTRATION_MENU):
        pytest.fail("Agent should not see Administration menu.")
