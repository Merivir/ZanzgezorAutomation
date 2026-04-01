from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec


class ExtensionsPage:
    SEARCH_INPUT = (
        By.XPATH,
        "//input[contains(@placeholder, 'extension') or @name='extension' or @type='text']",
    )
    SEARCH_BUTTON = (
        By.XPATH,
        "//button[normalize-space()='Search' or contains(., 'Search')]",
    )
    CLEAR_FILTERS = (
        By.XPATH,
        "//a[contains(., 'Clear filters')] | //button[contains(., 'Clear filters')]",
    )
    EXPORT_BUTTON = (
        By.XPATH,
        "//button[contains(., 'Export')]",
    )
    ADD_BUTTON = (
        By.XPATH,
        "//button[contains(., 'Add')]",
    )
    DELETE_BUTTON = (
        By.XPATH,
        "//button[contains(., 'Delete')]",
    )
    PUBLISH_BUTTON = (
        By.XPATH,
        "//button[contains(., 'Publish')]",
    )
    TABLE = (
        By.XPATH,
        "//table",
    )
    COLUMN_TOGGLE = (
        By.XPATH,
        "//*[self::button or self::div or self::span][contains(., 'Column') or contains(., 'column')]",
    )

    def __init__(self, driver, wait):
        self.driver = driver
        self.wait = wait

    def wait_until_loaded(self):
        self.wait.until(ec.presence_of_element_located(self.TABLE))

    def has_main_controls(self) -> bool:
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
        header_nodes = self.driver.find_elements(By.XPATH, "//table//th")
        return [node.text.strip() for node in header_nodes if node.text.strip()]
