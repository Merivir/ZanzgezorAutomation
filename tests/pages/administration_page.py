from pathlib import Path

from selenium.webdriver.common.by import By
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait


class AdministrationPage:
    # Main entry in the portal that opens Administration in a new tab.
    ADMINISTRATION_MENU = (
        By.XPATH,
        "//*[self::button or self::a or @role='button']["
        "contains(translate(normalize-space(.), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'administration') or "
        "contains(translate(@href, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'administration')"
        "]",
    )
    # Sidebar entries inside the Administration tab.
    ADMINISTRATION_SIDEBAR = (
        By.XPATH,
        "//app-root//cc-sidebar//nav | //app-root//cc-sidebar",
    )
    DASHBOARD_BUTTON = (
        By.XPATH,
        "//cc-sidebar//*[self::button or self::li or self::a][contains(normalize-space(), 'Dashboard')]",
    )
    TOOLS_BUTTON = (
        By.XPATH,
        "//cc-sidebar//*[self::button or self::li or self::a][contains(normalize-space(), 'Tools')]",
    )
    FLOW_BUTTON = (
        By.XPATH,
        "//cc-sidebar//*[self::button or self::li or self::a][contains(normalize-space(), 'Flow')]",
    )
    USERS_BUTTON = (
        By.XPATH,
        "//cc-sidebar//*[self::button or self::li or self::a][contains(normalize-space(), 'Users')]",
    )
    INTEGRATIONS_LAYER_BUTTON = (
        By.XPATH,
        "//cc-sidebar//*[self::button or self::li or self::a][contains(normalize-space(), 'Integrations')]",
    )
    EVALUATION_BUTTON = (
        By.XPATH,
        "//cc-sidebar//*[self::button or self::li or self::a][contains(normalize-space(), 'Evaluation')]",
    )
    SKILLS_BUTTON = (
        By.XPATH,
        "//cc-sidebar//*[self::button or self::li or self::a][contains(normalize-space(), 'Skills')]",
    )       
    STATUSES_BUTTON = (
        By.XPATH,
        "//cc-sidebar//*[self::button or self::li or self::a][contains(normalize-space(), 'Statuses')]",
    )
    EXTENSIONS_BUTTON = (
        By.XPATH,
        "//cc-sidebar//*[self::button or self::li or self::a][contains(normalize-space(), 'Extensions')]",
    )
    SPECIAL_NUMBERS_BUTTON = (
        By.XPATH,
        "//cc-sidebar//li[contains(@class, 'sub-link') and contains(normalize-space(), 'Special Numbers')]",
    )
    TEMPLATES_BUTTON = (
        By.XPATH,
        "//cc-sidebar//*[self::button or self::li or self::a][contains(normalize-space(), 'Templates')]",
    )   
    NOTIFICATIONS_BUTTON = (
        By.XPATH,
        "//app-root//cc-sidebar//*[self::button or self::li or self::a]"
        "[contains(normalize-space(), 'Notifications')]",
    )
    LOGO_BUTTON = (
        By.XPATH,
        "//cc-header//header//*[self::img or contains(@class, 'logo') or contains(@class, 'brand')][1] | //cc-header//header/div[1]",
    )

    def __init__(self, driver, wait):
        self.driver = driver
        self.wait = wait

    def wait_until_loaded(self):
        # The administration sidebar is our signal that the new tab is ready.
        self.wait.until(ec.presence_of_element_located(self.ADMINISTRATION_SIDEBAR))

    def open_administration_page(self):
        # Click the Administration entry from the rendered UI when present.
        # Some envs load the main call-center shell without exposing an Administration link, so fall back to admin-ui.
        if self._is_administration_loaded():
            return

        current_tabs = self.driver.window_handles
        try:
            administration_menu = WebDriverWait(self.driver, 15).until(lambda driver: self._administration_menu_option())
        except TimeoutException:
            Path("tests/downloads/debug_administration_menu.html").write_text(self.driver.page_source, encoding="utf-8")
            origin = self.driver.execute_script("return window.location.origin")
            self.driver.get(f"{origin}/admin-ui/")
            self.wait_until_loaded()
            return

        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", administration_menu)
        administration_menu.click()

        try:
            WebDriverWait(self.driver, 5).until(lambda d: len(d.window_handles) > len(current_tabs))
            self.driver.switch_to.window(self.driver.window_handles[-1])
        except TimeoutException:
            pass

        self.wait_until_loaded()

    def _administration_menu_option(self):
        options = []
        for element in self.driver.find_elements(*self.ADMINISTRATION_MENU):
            try:
                if element.is_displayed() and element.is_enabled():
                    options.append(element)
            except StaleElementReferenceException:
                continue
        if not options:
            return False
        return options[1] if len(options) > 1 else options[0]

    def _is_administration_loaded(self):
        try:
            return any(element.is_displayed() for element in self.driver.find_elements(*self.ADMINISTRATION_SIDEBAR))
        except StaleElementReferenceException:
            return False

    def open_extensions(self):
        # Click the Extensions button in the administration sidebar and wait for the page to load.
        try :
            self.wait.until(ec.element_to_be_clickable(self.EXTENSIONS_BUTTON))
        except Exception as e:
            print(f"Error while waiting for Extensions button: {e}")
            raise

        self.driver.find_element(*self.EXTENSIONS_BUTTON).click()

    def open_special_numbers(self):
        # Special Numbers lives under Administration > Flow.
        self.wait.until(ec.element_to_be_clickable(self.FLOW_BUTTON)).click()
        self.wait.until(ec.element_to_be_clickable(self.SPECIAL_NUMBERS_BUTTON)).click()

    def open_notifications(self):
        try:
            self.wait.until(ec.element_to_be_clickable(self.NOTIFICATIONS_BUTTON)).click()
            return
        except TimeoutException:
            pass

        origin = self.driver.execute_script("return window.location.origin")
        candidate_paths = (
            "/admin-ui/notifications",
            "/admin-ui/notification-types",
            "/admin-ui/notification-type",
            "/admin-ui/notification",
            "/admin-ui/administration/notifications",
            "/admin-ui/administration/notification-types",
            "/admin-ui/flow/notifications",
            "/admin-ui/flow/notification-types",
            "/admin-ui/#/notifications",
            "/admin-ui/#/notification-types",
            "/admin-ui/#/notification-type",
            "/admin-ui/#/notification",
            "/admin-ui/#/administration/notifications",
            "/admin-ui/#/administration/notification-types",
            "/admin-ui/#/flow/notifications",
            "/admin-ui/#/flow/notification-types",
        )
        loaded_locator = (
            By.XPATH,
            "//cc-notification-types | //cc-notifications | //*[self::h1 or self::h2 or self::h3][contains(normalize-space(), 'Notification')]",
        )

        for path in candidate_paths:
            self.driver.get(f"{origin}{path}")
            try:
                WebDriverWait(self.driver, 5).until(ec.presence_of_element_located(loaded_locator))
                return
            except TimeoutException:
                continue

        Path("tests/downloads/debug_notifications_navigation.html").write_text(self.driver.page_source, encoding="utf-8")
        raise TimeoutException("Notifications page was not reachable from sidebar or known direct routes.")
