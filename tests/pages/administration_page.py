from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec


class AdministrationPage:
    # Main entry in the portal that opens Administration in a new tab.
    ADMINISTRATION_MENU = (
        By.XPATH,
        "/html/body/cc-root/div/div[1]/cc-sidebar/nav/ol/div/div/li[11]/button",
    )
    # Sidebar entries inside the Administration tab.
    ADMINISTRATION_SIDEBAR = (
        By.XPATH,
        "/html/body/app-root/div/div[1]/cc-sidebar/nav/ol/div/div",
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
        "/html/body/app-root/div/div[1]/cc-sidebar/nav/ol/div/div/li[3]/button",
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
        "/html/body/app-root/div/div[1]/cc-sidebar/nav/ol/div/div/li[15]/button",
    )
    TEMPLATES_BUTTON = (
        By.XPATH,
        "/html/body/app-root/div/div[1]/cc-sidebar/nav/ol/div/div/li[16]/button",
    )   
    NOTIFICATIONS_BUTTON = (
        By.XPATH, 
        "/html/body/app-root/div/div[1]/cc-sidebar/nav/ol/div/div/li[17]/button",
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
        # Click the menu entry that opens the administration page in a new tab, then switch to that tab and wait for it to load.
        current_tabs = self.driver.window_handles
        try:
            self.wait.until(ec.element_to_be_clickable(self.ADMINISTRATION_MENU))
        except Exception as e:
            print(f"Error while waiting for Administration menu: {e}")
            raise

        self.driver.find_element(*self.ADMINISTRATION_MENU).click()

        self.wait.until(lambda d: len(d.window_handles) > len(current_tabs))
        self.driver.switch_to.window(self.driver.window_handles[-1])
        self.wait_until_loaded()

    def open_extensions(self):
        # Click the Extensions button in the administration sidebar and wait for the page to load.
        try :
            self.wait.until(ec.element_to_be_clickable(self.EXTENSIONS_BUTTON))
        except Exception as e:
            print(f"Error while waiting for Extensions button: {e}")
            raise

        self.driver.find_element(*self.EXTENSIONS_BUTTON).click()

    
