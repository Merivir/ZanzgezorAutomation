from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait


class AdministrationPage:
    # Main entry in the portal that opens Administration in a new tab.
    ADMINISTRATION_MENU = (
        By.XPATH,
        "//*[self::button or self::a or @role='button']["
        ".//*[normalize-space()='Administration'] or contains(normalize-space(), 'Administration') or "
        "contains(@href, 'administration')]",
    )
    # Sidebar entries inside the Administration tab.
    ADMINISTRATION_SIDEBAR = (
        By.XPATH,
        "//app-root//cc-sidebar//nav | //app-root//cc-sidebar",
    )
    DASHBOARD_BUTTON = (
        By.XPATH,
        "/html/body/app-root/div/div[1]/cc-sidebar/nav/ol/div/div/li[1]/button",
    )
    TOOLS_BUTTON = (
        By.XPATH,
        "/html/body/app-root/div/div[1]/cc-sidebar/nav/ol/div/div/li[2]/button",
    )
    FLOW_BUTTON = (
        By.XPATH,
        "//app-root//cc-sidebar//*[self::button or self::li or self::a][contains(normalize-space(), 'Flow')]",
    )
    USERS_BUTTON = (
        By.XPATH,
        "/html/body/app-root/div/div[1]/cc-sidebar/nav/ol/div/div/li[6]/button",
    )
    INTEGRATIONS_LAYER_BUTTON = (
        By.XPATH,
        "/html/body/app-root/div/div[1]/cc-sidebar/nav/ol/div/div/li[8]/button",
    )
    EVALUATION_BUTTON = (
        By.XPATH,
        "/html/body/app-root/div/div[1]/cc-sidebar/nav/ol/div/div/li[9]/button",
    )
    SKILLS_BUTTON = (
        By.XPATH,
        "/html/body/app-root/div/div[1]/cc-sidebar/nav/ol/div/div/li[13]/button",
    )       
    STATUSES_BUTTON = (
        By.XPATH,
        "/html/body/app-root/div/div[1]/cc-sidebar/nav/ol/div/div/li[14]/button",
    )
    EXTENSIONS_BUTTON = (
        By.XPATH,
        "//app-root//cc-sidebar//*[self::button or self::li or self::a][contains(normalize-space(), 'Extensions')]",
    )
    SPECIAL_NUMBERS_BUTTON = (
        By.XPATH,
        "//cc-sidebar//li[contains(@class, 'sub-link') and contains(normalize-space(), 'Special Numbers')]",
    )
    TEMPLATES_BUTTON = (
        By.XPATH,
        "/html/body/app-root/div/div[1]/cc-sidebar/nav/ol/div/div/li[16]/button",
    )   
    NOTIFICATIONS_BUTTON = (
        By.XPATH,
        "//app-root//cc-sidebar//*[self::button or self::li or self::a]"
        "[contains(normalize-space(), 'Notifications')]",
    )
    LOGO_BUTTON = (
        By.XPATH,
        "/html/body/app-root/cc-header/div/header/div/div[1]",
    )

    def __init__(self, driver, wait):
        self.driver = driver
        self.wait = wait

    def wait_until_loaded(self):
        # The administration sidebar is our signal that the new tab is ready.
        self.wait.until(ec.presence_of_element_located(self.ADMINISTRATION_SIDEBAR))

    def open_administration_page(self):
        # Click the menu entry. Some environments open Administration in a new tab, others navigate in the same tab.
        current_tabs = self.driver.window_handles
        try:
            administration_menu = self.wait.until(ec.element_to_be_clickable(self.ADMINISTRATION_MENU))
        except Exception as e:
            print(f"Error while waiting for Administration menu: {e}")
            raise

        administration_menu.click()

        try:
            WebDriverWait(self.driver, 3).until(lambda d: len(d.window_handles) > len(current_tabs))
            self.driver.switch_to.window(self.driver.window_handles[-1])
        except TimeoutException:
            pass
        self.wait_until_loaded()

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
        self.wait.until(ec.element_to_be_clickable(self.NOTIFICATIONS_BUTTON)).click()
    
