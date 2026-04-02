from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec


class PortalPage:
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
        self.wait.until(lambda d: "/zz-portal" in d.current_url and ec.presence_of_element_located(self.ADMINISTRATION_MENU)(d))

    def open_administration(self):
        self.wait.until(ec.presence_of_element_located(self.ADMINISTRATION_MENU))
        self.driver.find_element(*self.ADMINISTRATION_MENU).click()

    def open_extensions(self):
        self.wait.until(ec.presence_of_element_located(self.EXTENSIONS_LINK))
        self.driver.find_element(*self.EXTENSIONS_LINK).click()
