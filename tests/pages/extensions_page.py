from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import ElementClickInterceptedException, StaleElementReferenceException, TimeoutException


class ExtensionsPage:
    # Main page locators
    EXTENSIONS_HEADER = (By.XPATH, "/html/body/app-root/div/div[2]/cc-main-page/div/div/cc-main/div/h1")
    SEARCH_INPUT = (By.XPATH, "/html/body/app-root/div/div[2]/cc-main-page/div/div/cc-main/div/div/cc-dynamic-filter/div/div[2]/cc-dynamic-form/form/div[2]/div/div/cc-text-control/div/div/span/input")
    SEARCH_BUTTON = (By.XPATH, "/html/body/app-root/div/div[2]/cc-main-page/div/div/cc-main/div/div/cc-dynamic-filter/div/div[2]/div/div[2]/cc-button/p-button/button")
    CLEAR_FILTERS = (By.XPATH, "/html/body/app-root/div/div[2]/cc-main-page/div/div/cc-main/div/div/cc-dynamic-filter/div/div[2]/div/div[1]/cc-button/p-button/button")
    EXPORT_BUTTON = (By.XPATH, "//*[@id='pn_id_7']/div[1]/div/div[2]/div/cc-button/p-button/button")
    ADD_BUTTON = (By.XPATH, "//cc-dynamic-actions//button[.//span[normalize-space()='Add'] or .//i[normalize-space()='add']]")
    DELETE_BUTTON = (By.XPATH, "/html/body/app-root/div/div[2]/cc-main-page/div/div/cc-main/div/div/cc-dynamic-actions/div/cc-button[3]/p-button/button")
    PUBLISH_BUTTON = (By.XPATH, "/html/body/app-root/div/div[2]/cc-main-page/div/div/cc-main/div/div/cc-dynamic-actions/div/cc-button[1]/p-button/button")
    
    # Table locators
    TABLE = (By.XPATH, "//*[@id=\"pn_id_7-table\"]")
    COLUMN_TOGGLE = (By.XPATH, "//*[@id='pn_id_10']/div[3]")
    TABLE_ROWS = (By.XPATH, "//table//tbody/tr")
    EMPTY_TABLE_MESSAGE = (By.XPATH, "//*[@id=\"pn_id_7-table\"]/tbody/tr/td")
    LAST_PAGE_BUTTON = (By.XPATH, "//button[@aria-label='Last Page']")
    DROPDOWN_PANEL = (By.XPATH, "//div[contains(@class, 'p-dropdown-panel')]")

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
    ADD_POPUP_REQUIRED_ERRORS = (By.XPATH, "//p-dialog//*[contains(@class, 'cc-control-error') and normalize-space()='Required field']")

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

    def has_any_element(self, locators) -> bool:
        return any(self.driver.find_elements(*locator) for locator in locators)

    def has_add_popup_controls(self) -> bool:
        required_locators = [
            self.ADD_POPUP,
            self.ADD_POPUP_START_INPUT,
            self.ADD_POPUP_END_INPUT,
            self.ADD_POPUP_GENERATE_PASSWORDS,
            self.ADD_POPUP_PASSWORD,
            self.ADD_POPUP_SUBMIT,
            self.ADD_POPUP_CANCEL,
        ]
        return (
            all(self.driver.find_elements(*locator) for locator in required_locators)
            and self.has_any_element(self.ADD_POPUP_TYPE)
            and self.has_any_element(self.ADD_POPUP_TRANSPORT_TYPE)
        )

    def has_visible_element(self, locator) -> bool:
        return any(element.is_displayed() for element in self.driver.find_elements(*locator))

    def is_add_popup_submit_disabled(self) -> bool:
        submit_button = self.driver.find_element(*self.ADD_POPUP_SUBMIT)
        parent_classes = submit_button.find_element(By.XPATH, "./ancestor::p-button[1]").get_attribute("class")
        return bool(submit_button.get_attribute("disabled")) or "p-disabled" in parent_classes

    def is_add_popup_submit_enabled(self) -> bool:
        return not self.is_add_popup_submit_disabled()

    def add_popup_required_error_count(self) -> int:
        return len(self.driver.find_elements(*self.ADD_POPUP_REQUIRED_ERRORS))

    def has_required_error_for_label(self, label_text) -> bool:
        error_locator = (
            By.XPATH,
            "//p-dialog//*[self::cc-dropdown-control or self::cc-number-control or self::cc-text-control]"
            f"[.//label[contains(normalize-space(), '{label_text}')]]"
            "//*[contains(@class, 'cc-control-error') and normalize-space()='Required field']",
        )
        return bool(self.driver.find_elements(*error_locator))

    def has_add_popup_required_errors_for(self, labels) -> bool:
        return all(self.has_required_error_for_label(label) for label in labels)

    def wait_for_add_popup_required_errors_for(self, labels):
        self.wait.until(lambda _: self.has_add_popup_required_errors_for(labels))

    def add_popup_number_fields_are_empty(self) -> bool:
        start_value = self.driver.find_element(*self.ADD_POPUP_START_INPUT).get_attribute("value")
        end_value = self.driver.find_element(*self.ADD_POPUP_END_INPUT).get_attribute("value")
        return start_value == "" and end_value == ""

    def has_invalid_state_for_label(self, label_text) -> bool:
        invalid_locator = (
            By.XPATH,
            "//p-dialog//*[self::cc-dropdown-control or self::cc-number-control or self::cc-text-control]"
            f"[.//label[contains(normalize-space(), '{label_text}')]]"
            "[contains(@class, 'ng-invalid') or .//*[contains(@class, 'ng-invalid')]]"
            "[contains(@class, 'ng-touched') or .//*[contains(@class, 'ng-touched')]"
            " or .//*[contains(@class, 'ng-dirty')]]",
        )
        return bool(self.driver.find_elements(*invalid_locator))

    def has_add_popup_invalid_state_for(self, labels) -> bool:
        return all(self.has_invalid_state_for_label(label) for label in labels)

    def has_required_validation_for_label(self, label_text) -> bool:
        return self.has_invalid_state_for_label(label_text) or self.has_required_error_for_label(label_text)

    def has_add_popup_required_validation_for(self, labels) -> bool:
        return all(self.has_required_validation_for_label(label) for label in labels)

    def wait_for_add_popup_required_validation_for(self, labels):
        self.wait.until(lambda _: self.has_add_popup_required_validation_for(labels))

    def wait_for_invalid_state_for_label(self, label_text):
        self.wait.until(lambda _: self.has_invalid_state_for_label(label_text))

    def is_add_popup_open(self) -> bool:
        return (
            self.has_visible_element(self.ADD_POPUP)
            and self.has_visible_element(self.ADD_POPUP_SUBMIT)
            and self.has_visible_element(self.ADD_POPUP_CANCEL)
        )
    
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

    def has_visible_extension(self, expected_extension):
        expected_extension = str(expected_extension)
        for row in self.visible_table_rows():
            try:
                if self.get_extension_column_value(row) == expected_extension:
                    return True
            except StaleElementReferenceException:
                return self.has_visible_extension(expected_extension)

        return False
    
    def open_add_popup(self):
        if self.is_add_popup_open():
            return self

        self.wait.until(ec.element_to_be_clickable(self.ADD_BUTTON)).click()
        self.wait.until(ec.visibility_of_element_located(self.ADD_POPUP))
        self.wait.until(lambda _: self.is_add_popup_open())
        self.wait.until(lambda _: self.has_add_popup_controls())
        return self

    def close_add_popup(self):
        if not self.is_add_popup_open():
            return self

        self.wait.until(ec.element_to_be_clickable(self.ADD_POPUP_CANCEL)).click()
        self.wait.until(ec.invisibility_of_element_located(self.ADD_POPUP))
        return self

    def fill_add_popup(self, start, end, password=None):
        self.click_add_popup_start_button(start)
        self.click_add_popup_end_button(end)

        if password:
            self.driver.find_element(*self.ADD_POPUP_PASSWORD).send_keys(password)

    def touch_and_blur(self, locator, clear=False):
        element = self.wait.until(ec.element_to_be_clickable(locator))
        element.click()
        if clear:
            element.send_keys(Keys.CONTROL, "a")
            element.send_keys(Keys.BACKSPACE)
        element.send_keys(Keys.TAB)
        return self

    def click_add_popup_blank_area(self):
        popup = self.wait.until(ec.visibility_of_element_located(self.ADD_POPUP))
        ActionChains(self.driver).move_to_element_with_offset(popup, 20, 20).click().perform()
        return self

    def close_open_dropdown_panel(self):
        ActionChains(self.driver).send_keys(Keys.ESCAPE).perform()
        try:
            self.wait.until(ec.invisibility_of_element_located(self.DROPDOWN_PANEL))
        except TimeoutException:
            ActionChains(self.driver).send_keys(Keys.ESCAPE).perform()
        return self

    def focus_and_blur_add_popup_field(self, locator, label_text, clear=False):
        element = self.wait.until(ec.element_to_be_clickable(locator))
        element.click()
        if clear:
            element.send_keys(Keys.CONTROL, "a")
            element.send_keys(Keys.BACKSPACE)
        element.send_keys(Keys.TAB)
        return self

    def focus_and_blur_first_available_add_popup_field(self, locators, label_text):
        element = self.first_available_clickable(locators)
        if element is None:
            return self

        self.click_element(element)
        ActionChains(self.driver).send_keys(Keys.TAB).perform()
        return self

    def touch_add_popup_required_fields(self):
        self.focus_and_blur_add_popup_field(self.ADD_POPUP_PASSWORD, "Password", clear=True)
        self.focus_and_blur_first_available_add_popup_field(self.ADD_POPUP_TYPE, "Type")
        self.focus_and_blur_first_available_add_popup_field(self.ADD_POPUP_TRANSPORT_TYPE, "Transport type")
        return self

    def click_first_available(self, locators):
        element = self.first_available_clickable(locators)
        if element is None:
            raise TimeoutException(f"None of these locators became clickable: {locators}")

        self.click_element(element)
        return element

    def first_available_clickable(self, locators):
        for locator in locators:
            try:
                return self.wait.until(ec.element_to_be_clickable(locator))
            except TimeoutException:
                continue

        return None

    def click_element(self, element):
        try:
            element.click()
        except ElementClickInterceptedException:
            self.driver.execute_script("arguments[0].click();", element)

    def choose_dropdown_option(self, dropdown_locators, option_text):
        self.click_first_available(dropdown_locators)
        lower_option_text = option_text.lower()
        option_locator = (
            By.XPATH,
            "//*[@role='option']"
            f"[translate(normalize-space(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz')='{lower_option_text}' "
            f"or translate(@aria-label, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz')='{lower_option_text}']",
        )
        self.wait.until(ec.element_to_be_clickable(option_locator)).click()
        return self


    def choose_extension_type(self, extension_type="pjsip"):
        return self.choose_dropdown_option(self.ADD_POPUP_TYPE, extension_type)

    def choose_transport_type(self, transport_type="transport-udp"):
        if transport_type in ("udp", "tcp"):
            transport_type = f"transport-{transport_type}"

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

    def go_to_last_page(self):
        last_page_button = self.wait.until(ec.presence_of_element_located(self.LAST_PAGE_BUTTON))
        if last_page_button.get_attribute("disabled") or "p-disabled" in last_page_button.get_attribute("class"):
            return self

        first_row = self.visible_table_rows()[0] if self.visible_table_rows() else None
        self.wait.until(ec.element_to_be_clickable(self.LAST_PAGE_BUTTON)).click()
        if first_row:
            self.wait.until(ec.staleness_of(first_row))
        return self
