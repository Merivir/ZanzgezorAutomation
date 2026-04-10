from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec


class ExtensionsPage:
    # Main controls we expect on the Extensions configuration page.
    SEARCH_INPUT = (
        By.XPATH,
        "/html/body/app-root/div/div[2]/cc-main-page/div/div/cc-main/div/div/cc-dynamic-filter/div/div[2]/cc-dynamic-form/form/div[2]/div/div/cc-text-control/div/div/span/input"
    )
    
    SEARCH_BUTTON = (
        By.XPATH,
        "/html/body/app-root/div/div[2]/cc-main-page/div/div/cc-main/div/div/cc-dynamic-filter/div/div[2]/div/div[2]/cc-button/p-button/button"
    )
    CLEAR_FILTERS = (
        By.XPATH,
        "/html/body/app-root/div/div[2]/cc-main-page/div/div/cc-main/div/div/cc-dynamic-filter/div/div[2]/div/div[1]/cc-button/p-button/button"
    )
    EXPORT_BUTTON = (
        By.XPATH,
        "//*[@id='pn_id_7']/div[1]/div/div[2]/div/cc-button/p-button/button"
    )
    ADD_BUTTON = (
        By.XPATH,
        "/html/body/app-root/div/div[2]/cc-main-page/div/div/cc-main/div/div/cc-dynamic-actions/div/cc-button[2]/p-button/button"
    )
    DELETE_BUTTON = (
        By.XPATH,
        "/html/body/app-root/div/div[2]/cc-main-page/div/div/cc-main/div/div/cc-dynamic-actions/div/cc-button[3]/p-button/button"
    )
    PUBLISH_BUTTON = (
        By.XPATH,
        "/html/body/app-root/div/div[2]/cc-main-page/div/div/cc-main/div/div/cc-dynamic-actions/div/cc-button[1]/p-button/button"
    )
    TABLE = (
        By.XPATH,
        "//*[@id='pn_id_7-table']"
    )
    COLUMN_TOGGLE = (
        By.XPATH,
        "//*[@id='pn_id_10']/div[3]"
    )

    def __init__(self, driver, wait):
        self.driver = driver
        self.wait = wait

    def wait_until_loaded(self):
        # The table is the simplest signal that the page finished opening.
        self.wait.until(ec.presence_of_element_located(self.TABLE))

    def has_main_controls(self) -> bool:
        # Basic smoke check for the most important page controls.
        required_locators = [
            self.SEARCH_INPUT,
            self.SEARCH_BUTTON,
            self.EXPORT_BUTTON,
            self.ADD_BUTTON,
            self.DELETE_BUTTON,
            self.PUBLISH_BUTTON,
            self.TABLE,
        ]
        return all(self.driver.find_elements(*locator) for locator in required_locators)

    def visible_headers(self) -> list[str]:
        # Helper for future assertions around visible table columns.
        header_nodes = self.driver.find_elements(By.XPATH, "//table//th")
        return [node.text.strip() for node in header_nodes if node.text.strip()]
