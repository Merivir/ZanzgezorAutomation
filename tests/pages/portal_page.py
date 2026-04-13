from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from tests.conftest import driver


class PortalPage:
    # These locators point to the sidebar menu entries in the current new UI.
    ADMINISTRATION_MENU = (
        By.XPATH,
        "/html/body/cc-root/div/div[1]/cc-sidebar/nav/ol/div/div/li[11]/button"
    )
    EXTENSIONS_LINK = (
        By.XPATH,
        "/html/body/app-root/div/div[1]/cc-sidebar/nav/ol/div/div/li[15]/button"
    )


    def __init__(self, driver, wait):
        self.driver = driver
        self.wait = wait

    def wait_until_loaded(self):
        # We consider the portal loaded when the user is inside /zz-portal
        # and the Administration menu is present in the sidebar.
        self.wait.until(lambda d: "/zz-portal" in d.current_url and ec.presence_of_element_located(self.ADMINISTRATION_MENU)(d))

    def open_administration(self):
        current_tabs = self.driver.window_handles
        self.wait.until(ec.presence_of_element_located(self.ADMINISTRATION_MENU))
        self.driver.find_element(*self.ADMINISTRATION_MENU).click()

        self.wait.until(lambda d: len(d.window_handles) > len(current_tabs))
        new_tabs = self.driver.window_handles
        self.driver.switch_to.window(new_tabs[-1])

    def open_extensions(self):
        # Open the Extensions page from the sidebar after Administration is expanded.
        self.wait.until(ec.presence_of_element_located(self.EXTENSIONS_LINK))
        self.wait.until(ec.presence_of_element_located(self.EXTENSIONS_LINK))
        self.driver.find_element(*self.EXTENSIONS_LINK).click()
