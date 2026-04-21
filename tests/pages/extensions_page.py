from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import TimeoutException


class ExtensionsPage:
    # Main page locators
    EXTENSIONS_HEADER = (By.XPATH, "/html/body/app-root/div/div[2]/cc-main-page/div/div/cc-main/div/h1")
    SEARCH_INPUT = (By.XPATH, "/html/body/app-root/div/div[2]/cc-main-page/div/div/cc-main/div/div/cc-dynamic-filter/div/div[2]/cc-dynamic-form/form/div[2]/div/div/cc-text-control/div/div/span/input")
    SEARCH_BUTTON = (By.XPATH, "/html/body/app-root/div/div[2]/cc-main-page/div/div/cc-main/div/div/cc-dynamic-filter/div/div[2]/div/div[2]/cc-button/p-button/button")
    CLEAR_FILTERS = (By.XPATH, "/html/body/app-root/div/div[2]/cc-main-page/div/div/cc-main/div/div/cc-dynamic-filter/div/div[2]/div/div[1]/cc-button/p-button/button")
    EXPORT_BUTTON = (By.XPATH, "//*[@id='pn_id_7']/div[1]/div/div[2]/div/cc-button/p-button/button")
    ADD_BUTTON = ( By.XPATH, "/html/body/app-root/div/div[2]/cc-main-page/div/div/cc-main/div/div/cc-dynamic-actions/div/cc-button[2]/p-button/button")
    DELETE_BUTTON = (By.XPATH, "/html/body/app-root/div/div[2]/cc-main-page/div/div/cc-main/div/div/cc-dynamic-actions/div/cc-button[3]/p-button/button")
    PUBLISH_BUTTON = (By.XPATH, "/html/body/app-root/div/div[2]/cc-main-page/div/div/cc-main/div/div/cc-dynamic-actions/div/cc-button[1]/p-button/button")
    
    # Table locators
    TABLE = (By.XPATH, "//*[@id=\"pn_id_7-table\"]")
    COLUMN_TOGGLE = (By.XPATH, "//*[@id='pn_id_10']/div[3]")
    TABLE_ROWS = (By.XPATH, "//table//tbody/tr")
    EMPTY_TABLE_MESSAGE = (By.XPATH, "//*[@id=\"pn_id_7-table\"]/tbody/tr/td")

    # Add popup locators
    ADD_POPUP = (By.XPATH, "/html/body/app-root/div/div[2]/cc-main-page/div/div/cc-main/cc-dynamic-popup/p-dialog/div/div")
    ADD_POPUP_TYPE = [
        (By.XPATH, "(//cc-dynamic-popup//p-dropdown)[1]/div"),
        (By.XPATH, "(//cc-dynamic-popup//*[@role='combobox'])[1]"),
        (By.XPATH, "(//p-dialog//p-dropdown)[1]/div"),
        (By.XPATH, "(//p-dialog//*[@role='combobox'])[1]"),
    ]
    ADD_POPUP_TRANSPORT_TYPE = [
        (By.XPATH, "(//cc-dynamic-popup//p-dropdown)[2]/div"),
        (By.XPATH, "(//cc-dynamic-popup//*[@role='combobox'])[2]"),
        (By.XPATH, "(//p-dialog//p-dropdown)[2]/div"),
        (By.XPATH, "(//p-dialog//*[@role='combobox'])[2]"),
    ]
    ADD_POPUP_START_INPUT = (By.XPATH, "//*[@id='rangeStart']/span/input")
    ADD_POPUP_END_INPUT = (By.XPATH, "//*[@id='rangeEnd']/span/input")
    ADD_POPUP_GENERATE_PASSWORDS = (By.XPATH, "//*[@id='generatePasswords']/div/div[2]")
    ADD_POPUP_PASSWORD = (By.XPATH, "/html/body/app-root/div/div[2]/cc-main-page/div/div/cc-main/cc-dynamic-popup/p-dialog/div/div/div[3]/div/div[1]/cc-dynamic-form/form/div[7]/div/div/cc-text-control/div/div/span/input")
    ADD_POPUP_SUBMIT = (By.XPATH, "//p-dialog//cc-button[2]//button")
    ADD_POPUP_CANCEL = (By.XPATH, "/html/body/app-root/div/div[2]/cc-main-page/div/div/cc-main/cc-dynamic-popup/p-dialog/div/div/div[3]/div/div[2]/cc-button[1]/p-button/button")

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
    
    def search_for_extension_number(self, extension_number):
        search_input = self.wait.until(ec.element_to_be_clickable(self.SEARCH_INPUT))
        search_input.clear()
        search_input.send_keys(str(extension_number))
        self.wait.until(ec.element_to_be_clickable(self.SEARCH_BUTTON)).click()
        return self  # Return the page object to allow for method chaining in tests
    
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
    
    def open_add_popup(self):
        self.wait.until(ec.element_to_be_clickable(self.ADD_BUTTON)).click()
        self.wait.until(ec.visibility_of_element_located(self.ADD_POPUP))
        return self

    def fill_add_popup(self, start, end, password=None):
        self.click_add_popup_start_button(start)
        self.click_add_popup_end_button(end)

        if password:
            self.driver.find_element(*self.ADD_POPUP_PASSWORD).send_keys(password)

    def click_first_available(self, locators):
        for locator in locators:
            try:
                element = self.wait.until(ec.element_to_be_clickable(locator))
                element.click()
                return element
            except TimeoutException:
                continue

        raise TimeoutException(f"None of these locators became clickable: {locators}")

    def choose_dropdown_option(self, dropdown_locators, option_text):
        self.click_first_available(dropdown_locators)
        lower_option_text = option_text.lower()
        option_locator = (
            By.XPATH,
            "//*[@role='option' or self::li or self::div]"
            f"[translate(normalize-space(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz')='{lower_option_text}']",
        )
        self.wait.until(ec.element_to_be_clickable(option_locator)).click()
        return self

    def choose_extension_type(self, extension_type="pjsip"):
        return self.choose_dropdown_option(self.ADD_POPUP_TYPE, extension_type)

    def choose_transport_type(self, transport_type="udp"):
        return self.choose_dropdown_option(self.ADD_POPUP_TRANSPORT_TYPE, transport_type)

    def click_generate_passwords(self):
        self.driver.find_element(*self.ADD_POPUP_GENERATE_PASSWORDS).click()

    def click_add_popup_start_button(self, start):
        self.driver.find_element(*self.ADD_POPUP_START_INPUT).send_keys(start)

    def click_add_popup_end_button(self, end):
        self.driver.find_element(*self.ADD_POPUP_END_INPUT).send_keys(end)
    
    def submit_add_popup(self):
        submit_button = self.driver.find_element(*self.ADD_POPUP_SUBMIT)
        submit_button.click()
