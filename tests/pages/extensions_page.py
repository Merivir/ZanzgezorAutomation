from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec


class ExtensionsPage:
    # Main controls we expect on the Extensions configuration page.
    EXTENSIONS_HEADER = (
        By.XPATH,
        "/html/body/app-root/div/div[2]/cc-main-page/div/div/cc-main/div/h1"
    )
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
        "//*[@id=\"pn_id_7-table\"]"
    )
    COLUMN_TOGGLE = (
        By.XPATH,
        "//*[@id='pn_id_10']/div[3]" 
    )
    TABLE_ROWS = (By.XPATH, "//table//tbody/tr")
    EMPTY_TABLE_MESSAGE = (
        By.XPATH,
        "//*[@id=\"pn_id_7-table\"]/tbody/tr/td"
    )

    def __init__(self, driver, wait):
        self.driver = driver
        self.wait = wait

    def wait_until_loaded(self):
        # the presence of the header is our signal that the page is ready for interaction.
        self.wait.until(ec.presence_of_element_located(self.EXTENSIONS_HEADER))

    def has_main_controls(self) -> bool:
        # Basic smoke check for the most important page controls.
        required_locators = [
            self.EXTENSIONS_HEADER,
            self.SEARCH_INPUT,
            self.SEARCH_BUTTON,
            self.EXPORT_BUTTON,
            self.ADD_BUTTON,
            self.DELETE_BUTTON,
            self.PUBLISH_BUTTON,
            self.TABLE,
        ]
        return all(self.driver.find_elements(*locator) for locator in required_locators)

    def is_loaded(self) -> bool:
        # Final check to confirm the page is fully loaded and ready for interaction.
        return self.has_main_controls()
    
    def visible_table_rows(self):
        # Returns only the rows that are currently visible (i.e. not filtered out or hidden).
        return self.driver.find_elements(*self.TABLE_ROWS)  
    
    def get_extension_column_value(self, row):
        # Assuming the first column contains the extension name/number, this function retrieves that value from a given row element.
        return row.find_element(By.XPATH, "./td[1]").text.strip()

    def has_single_result_with_extension(self, expected_extension):
        rows = self.visible_table_rows()
        if len(rows) != 1:
            return False

        first_value = self.get_extension_column_value(rows[0])
        print(f"Expected extension: {expected_extension}, Found in table: {first_value}")
        return first_value == expected_extension