from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import ElementClickInterceptedException, StaleElementReferenceException, TimeoutException


class ExtensionsPage:
    TABLE_DATA_HEADERS = ["Extension", "Real Extension", "Type", "Transport type", "Password", "Status"]

    # Main page locators
    EXTENSIONS_HEADER = (By.XPATH, "/html/body/app-root/div/div[2]/cc-main-page/div/div/cc-main/div/h1")
    SEARCH_INPUT = (By.XPATH, "/html/body/app-root/div/div[2]/cc-main-page/div/div/cc-main/div/div/cc-dynamic-filter/div/div[2]/cc-dynamic-form/form/div[2]/div/div/cc-text-control/div/div/span/input")
    SEARCH_BUTTON = (By.XPATH, "/html/body/app-root/div/div[2]/cc-main-page/div/div/cc-main/div/div/cc-dynamic-filter/div/div[2]/div/div[2]/cc-button/p-button/button")
    CLEAR_FILTERS = (By.XPATH, "/html/body/app-root/div/div[2]/cc-main-page/div/div/cc-main/div/div/cc-dynamic-filter/div/div[2]/div/div[1]/cc-button/p-button/button")
    EXPORT_BUTTON = (By.XPATH, "//*[@id='pn_id_7']/div[1]/div/div[2]/div/cc-button/p-button/button")
    EXPORT_CSV_OPTION = (By.XPATH, "//div[contains(@class, 'export-table-items')]//*[normalize-space()='CSV']")
    ADD_BUTTON = (By.XPATH, "//cc-dynamic-actions//button[.//span[normalize-space()='Add'] or .//i[normalize-space()='add']]")
    DELETE_BUTTON = (By.XPATH, "//cc-dynamic-actions//button[.//span[normalize-space()='Delete'] or .//i[normalize-space()='delete']]")
    PUBLISH_BUTTON = (By.XPATH, "/html/body/app-root/div/div[2]/cc-main-page/div/div/cc-main/div/div/cc-dynamic-actions/div/cc-button[1]/p-button/button")
    
    # Table locators
    TABLE = (By.XPATH, "//*[@id=\"pn_id_7-table\"]")
    COLUMN_TOGGLE = (By.XPATH, "//*[@id='pn_id_10']/div[3]")
    COLUMN_OPTIONS = (By.XPATH, "//div[contains(@class, 'p-multiselect-panel')]//li[@role='option']")
    COLUMN_PANEL = (By.XPATH, "//div[contains(@class, 'p-multiselect-panel')]")
    TABLE_HEADERS = (By.XPATH, "//table//thead//th")
    TABLE_ROWS = (By.XPATH, "//table//tbody/tr")
    ROW_EDIT_BUTTON = (By.XPATH, ".//button[.//i[normalize-space()='edit']]")
    ROW_MOBILE_BUTTON = (By.XPATH, ".//button[.//i[normalize-space()='phone']]")
    ROW_DELETE_BUTTON = (By.XPATH, ".//button[.//i[normalize-space()='delete']]")
    EMPTY_TABLE_MESSAGE = (By.XPATH, "//*[@id=\"pn_id_7-table\"]/tbody/tr/td")
    FIRST_PAGE_BUTTON = (By.XPATH, "//button[@aria-label='First Page']")
    NEXT_PAGE_BUTTON = (By.XPATH, "//button[@aria-label='Next Page']")
    LAST_PAGE_BUTTON = (By.XPATH, "//button[@aria-label='Last Page']")
    CURRENT_PAGE_BUTTON = (By.XPATH, "//button[contains(@class, 'p-paginator-page') and contains(@class, 'p-highlight')]")
    PREVIOUS_PAGE_BUTTON = (By.XPATH, "//button[@aria-label='Previous Page']")
    DROPDOWN_PANEL = (By.XPATH, "//div[contains(@class, 'p-dropdown-panel')]")

    # Confirmation dialog locators
    CONFIRM_DIALOG = (
        By.XPATH,
        "//div[(@role='alertdialog' or contains(@class, 'p-confirm-dialog')) and contains(@class, 'p-dialog')]",
    )
    CONFIRM_CANCEL = (
        By.XPATH,
        "(//div[(@role='alertdialog' or contains(@class, 'p-confirm-dialog')) and contains(@class, 'p-dialog')]"
        "//button[contains(normalize-space(), 'Cancel') or contains(normalize-space(), 'No') "
        "or contains(normalize-space(), 'Reject')])[last()]",
    )
    CONFIRM_ACCEPT = (
        By.XPATH,
        "(//div[(@role='alertdialog' or contains(@class, 'p-confirm-dialog')) and contains(@class, 'p-dialog')]"
        "//button[contains(normalize-space(), 'Submit') or contains(normalize-space(), 'Yes') "
        "or contains(normalize-space(), 'Ok') or contains(normalize-space(), 'Delete') "
        "or contains(normalize-space(), 'Accept')])[last()]",
    )

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
    POPUP_INPUTS = (By.XPATH, "//p-dialog//input")
    POPUP = (By.XPATH, "//p-dialog")
    POPUP_DROPDOWN_LABELS = (By.XPATH, "//p-dialog//*[contains(@class, 'p-dropdown-label') or contains(@class, 'p-multiselect-label')]")

    # Mobile popup locators
    MOBILE_POPUP = (By.XPATH, "//div[@role='dialog' and .//*[normalize-space()='DYNAMIC.ACTIONS.MOBILE']]")
    MOBILE_NEW_PHONE_INPUT = (
        By.XPATH,
        "//div[@role='dialog' and .//*[normalize-space()='DYNAMIC.ACTIONS.MOBILE']]"
        "//cc-text-control[.//label[contains(normalize-space(), 'New')]]//input",
    )
    MOBILE_ACTIVE_PHONE_LABEL = (
        By.XPATH,
        "//div[@role='dialog' and .//*[normalize-space()='DYNAMIC.ACTIONS.MOBILE']]"
        "//*[contains(normalize-space(), 'Active phone')]",
    )
    MOBILE_PHONE_OPTIONS = (
        By.XPATH,
        "//div[@role='dialog' and .//*[normalize-space()='DYNAMIC.ACTIONS.MOBILE']]//p-radiobutton",
    )
    MOBILE_CANCEL = (
        By.XPATH,
        "//div[@role='dialog' and .//*[normalize-space()='DYNAMIC.ACTIONS.MOBILE']]"
        "//button[.//span[normalize-space()='Cancel']]",
    )
    MOBILE_SUBMIT = (
        By.XPATH,
        "//div[@role='dialog' and .//*[normalize-space()='DYNAMIC.ACTIONS.MOBILE']]"
        "//button[.//span[normalize-space()='Submit']]",
    )

    def __init__(self, driver, wait):
        self.driver = driver
        self.wait = wait

    def log_action(self, message):
        print(f"[Extensions] {message}", flush=True)

    def wait_until_loaded(self):
        self.log_action("Wait until Extensions page is loaded")
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
        self.log_action(f"Search extension: {extension_number}")
        search_input = self.wait.until(ec.element_to_be_clickable(self.SEARCH_INPUT))
        search_input.send_keys(Keys.CONTROL, "a")
        search_input.send_keys(Keys.BACKSPACE)
        search_input.send_keys(str(extension_number))
        self.log_action("Click Search")
        self.click_element(self.wait.until(ec.element_to_be_clickable(self.SEARCH_BUTTON)))
        return self  # Return the page object to allow for method chaining in tests

    def clear_search_and_submit(self):
        self.log_action("Clear search")
        search_input = self.wait.until(ec.element_to_be_clickable(self.SEARCH_INPUT))
        search_input.send_keys(Keys.CONTROL, "a")
        search_input.send_keys(Keys.BACKSPACE)
        self.log_action("Click Search with empty value")
        self.click_element(self.wait.until(ec.element_to_be_clickable(self.SEARCH_BUTTON)))
        return self

    def export_extensions(self):
        self.log_action("Click Export")
        export_button = self.wait.until(ec.presence_of_element_located(self.EXPORT_BUTTON))
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", export_button)
        self.click_element(self.wait.until(ec.element_to_be_clickable(self.EXPORT_BUTTON)))
        self.log_action("Click CSV export option")
        self.click_element(self.wait.until(ec.element_to_be_clickable(self.EXPORT_CSV_OPTION)))
        return self
    
    def visible_table_rows(self):
        # Returns only the rows that are currently visible (i.e. not filtered out or hidden).
        return self.driver.find_elements(*self.TABLE_ROWS)  

    def visible_table_column_count(self) -> int:
        return len(
            [
                header
                for header in self.driver.find_elements(*self.TABLE_HEADERS)
                if header.is_displayed() and header.text.strip()
            ]
        )

    def visible_table_headers(self):
        return [
            header.text.strip()
            for header in self.driver.find_elements(*self.TABLE_HEADERS)
            if header.is_displayed() and header.text.strip()
        ]

    def wait_for_visible_table_column_count(self, expected_count):
        self.wait.until(lambda _: self.visible_table_column_count() == expected_count)
        return self

    def open_column_visibility_dropdown(self):
        if self.is_column_visibility_dropdown_open():
            return self

        self.log_action("Open column visibility dropdown")
        self.wait.until(ec.element_to_be_clickable(self.COLUMN_TOGGLE)).click()
        self.wait.until(ec.visibility_of_element_located(self.COLUMN_PANEL))
        self.wait.until(lambda _: len(self.column_visibility_options()) > 0)
        return self

    def close_column_visibility_dropdown(self):
        if not self.is_column_visibility_dropdown_open():
            return self

        self.log_action("Close column visibility dropdown")
        ActionChains(self.driver).send_keys(Keys.ESCAPE).perform()
        try:
            self.wait.until(ec.invisibility_of_element_located(self.COLUMN_PANEL))
        except TimeoutException:
            trigger = self.wait.until(ec.element_to_be_clickable(self.COLUMN_TOGGLE))
            self.click_element(trigger)
            self.wait.until(ec.invisibility_of_element_located(self.COLUMN_PANEL))
        return self

    def is_column_visibility_dropdown_open(self) -> bool:
        return any(panel.is_displayed() for panel in self.driver.find_elements(*self.COLUMN_PANEL))

    def column_visibility_options(self):
        return [option for option in self.driver.find_elements(*self.COLUMN_OPTIONS) if option.is_displayed()]

    def column_visibility_option_labels(self):
        try:
            return [option.get_attribute("aria-label") for option in self.column_visibility_options()]
        except StaleElementReferenceException:
            return [option.get_attribute("aria-label") for option in self.column_visibility_options()]

    def column_visibility_option_count(self) -> int:
        return len(self.column_visibility_option_labels())

    def is_column_option_selected(self, option) -> bool:
        return option.get_attribute("aria-checked") == "true"

    def set_column_option_visibility(self, label, visible):
        option_locator = (
            By.XPATH,
            "//div[contains(@class, 'p-multiselect-panel')]//li[@role='option' and @aria-label="
            f"'{label}']",
        )
        option = self.wait.until(ec.element_to_be_clickable(option_locator))
        if self.is_column_option_selected(option) != visible:
            self.log_action(f"Set column '{label}' visible={visible}")
            self.click_element(option)
            self.wait.until(lambda _: self.driver.find_element(*option_locator).get_attribute("aria-checked") == str(visible).lower())
        return self

    def set_all_column_visibility(self, visible):
        self.open_column_visibility_dropdown()
        labels = self.column_visibility_option_labels()
        for label in labels:
            try:
                self.set_column_option_visibility(label, visible)
            except StaleElementReferenceException:
                self.set_column_option_visibility(label, visible)
        self.close_column_visibility_dropdown()
        return self

    def set_columns_visibility(self, labels, visible):
        self.open_column_visibility_dropdown()
        for label in labels:
            try:
                self.set_column_option_visibility(label, visible)
            except StaleElementReferenceException:
                self.set_column_option_visibility(label, visible)
        self.close_column_visibility_dropdown()
        return self
    
    def get_extension_column_value(self, row):
        # Assuming the first column contains the extension name/number, this function retrieves that value from a given row element.
        return row.find_element(By.XPATH, "./td[1]").text.strip()

    def visible_table_records(self):
        headers = self.visible_table_headers()
        records = []

        for row in self.visible_table_rows():
            cells = [
                cell.text.strip()
                for cell in row.find_elements(By.XPATH, "./td")
                if cell.is_displayed() and cell.text.strip() and cell.text.strip() != "edit"
            ]
            if not cells or cells[0] == "No data to display!":
                continue

            data_headers = [header for header in headers if header in self.TABLE_DATA_HEADERS]
            if len(cells) == 5:
                data_headers = ["Extension", "Real Extension", "Type", "Transport type", "Status"]
            elif len(cells) >= len(self.TABLE_DATA_HEADERS):
                data_headers = self.TABLE_DATA_HEADERS
                cells = cells[: len(data_headers)]
            elif "Extension" not in data_headers:
                data_headers = self.TABLE_DATA_HEADERS

            records.append(dict(zip(data_headers, cells[: len(data_headers)])))

        return records

    def first_visible_table_record(self):
        records = self.visible_table_records()
        if not records:
            return None

        return records[0]

    def first_visible_table_row_text(self):
        row = self.wait.until(lambda _: self.visible_table_rows()[0] if self.visible_table_rows() else False)
        return row.text

    def last_visible_table_record(self):
        records = self.visible_table_records()
        if not records:
            return None

        return records[-1]

    def open_first_row_edit_popup(self):
        row = self.wait.until(lambda _: self.visible_table_rows()[0] if self.visible_table_rows() else False)
        return self.open_row_edit_popup(row)

    def open_last_row_edit_popup(self):
        row = self.wait.until(lambda _: self.visible_table_rows()[-1] if self.visible_table_rows() else False)
        return self.open_row_edit_popup(row)

    def open_row_edit_popup(self, row):
        self.log_action("Click row Edit")
        edit_button = row.find_element(*self.ROW_EDIT_BUTTON)
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", edit_button)
        self.click_element(edit_button)
        self.wait.until(ec.visibility_of_element_located(self.ADD_POPUP))
        self.wait.until(lambda _: self.is_add_popup_open())
        self.log_action("Edit popup opened")
        return self

    def open_first_row_delete_confirmation(self):
        self.log_action("Click row Delete")
        row = self.wait.until(lambda _: self.visible_table_rows()[0] if self.visible_table_rows() else False)
        delete_button = row.find_element(*self.ROW_DELETE_BUTTON)
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", delete_button)
        self.click_element(delete_button)
        self.wait.until(ec.visibility_of_element_located(self.CONFIRM_DIALOG))
        self.log_action("Delete confirmation opened")
        return self

    def is_delete_confirmation_open(self):
        return (
            self.has_visible_element(self.CONFIRM_DIALOG)
            and self.has_visible_element(self.CONFIRM_CANCEL)
            and self.has_visible_element(self.CONFIRM_ACCEPT)
        )

    def cancel_delete_confirmation(self):
        self.log_action("Click confirmation Reject/Cancel")
        self.click_element(self.wait.until(ec.element_to_be_clickable(self.CONFIRM_CANCEL)))
        self.wait.until(ec.invisibility_of_element_located(self.CONFIRM_DIALOG))
        return self

    def confirm_delete_confirmation(self):
        self.log_action("Click confirmation Accept")
        self.click_element(self.wait.until(ec.element_to_be_clickable(self.CONFIRM_ACCEPT)))
        self.wait.until(ec.invisibility_of_element_located(self.CONFIRM_DIALOG))
        return self

    def open_first_row_mobile_popup(self):
        self.log_action("Click row Mobile")
        row = self.wait.until(lambda _: self.visible_table_rows()[0] if self.visible_table_rows() else False)
        mobile_button = row.find_element(*self.ROW_MOBILE_BUTTON)
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", mobile_button)
        self.click_element(mobile_button)
        self.wait.until(ec.visibility_of_element_located(self.MOBILE_POPUP))
        self.wait.until(lambda _: self.is_mobile_popup_open())
        self.log_action("Mobile popup opened")
        return self

    def is_mobile_popup_open(self):
        return (
            self.has_visible_element(self.MOBILE_POPUP)
            and self.has_visible_element(self.MOBILE_CANCEL)
            and self.has_visible_element(self.MOBILE_SUBMIT)
        )

    def has_mobile_popup_controls(self):
        return (
            self.has_visible_element(self.MOBILE_POPUP)
            and self.has_visible_element(self.MOBILE_NEW_PHONE_INPUT)
            and self.has_visible_element(self.MOBILE_ACTIVE_PHONE_LABEL)
            and self.has_visible_element(self.MOBILE_CANCEL)
            and self.has_visible_element(self.MOBILE_SUBMIT)
        )

    def visible_mobile_phone_option_count(self):
        return len(
            [
                option
                for option in self.driver.find_elements(*self.MOBILE_PHONE_OPTIONS)
                if option.is_displayed()
            ]
        )

    def close_mobile_popup(self):
        if not self.is_mobile_popup_open():
            return self

        self.log_action("Click Mobile popup Cancel")
        self.click_element(self.wait.until(ec.element_to_be_clickable(self.MOBILE_CANCEL)))
        try:
            self.wait.until(ec.invisibility_of_element_located(self.MOBILE_POPUP))
        except TimeoutException:
            ActionChains(self.driver).send_keys(Keys.ESCAPE).perform()
            self.wait.until(ec.invisibility_of_element_located(self.MOBILE_POPUP))
        return self

    def popup_field_values(self):
        values = []

        for input_element in self.driver.find_elements(*self.POPUP_INPUTS):
            value = input_element.get_attribute("value")
            if value:
                values.append(value.strip())

        for label in self.driver.find_elements(*self.POPUP_DROPDOWN_LABELS):
            text = label.text.strip()
            if text:
                values.append(text)

        for popup in self.driver.find_elements(*self.POPUP):
            for line in popup.text.splitlines():
                line = line.strip()
                if line:
                    values.append(line)

        return values

    def edit_popup_password_value(self):
        password_locators = [
            (
                By.XPATH,
                "//p-dialog//*[self::cc-text-control or self::div]"
                "[.//label[contains(normalize-space(), 'Password')]]//input",
            ),
            self.ADD_POPUP_PASSWORD,
        ]

        for locator in password_locators:
            for input_element in self.driver.find_elements(*locator):
                if input_element.is_displayed():
                    value = input_element.get_attribute("value")
                    if value:
                        return value.strip()

        input_values = [
            input_element.get_attribute("value").strip()
            for input_element in self.driver.find_elements(*self.POPUP_INPUTS)
            if input_element.is_displayed() and input_element.get_attribute("value")
        ]
        return input_values[-1] if input_values else ""

    def set_edit_popup_password(self, password):
        self.log_action("Set Edit popup password")
        password_locators = [
            (
                By.XPATH,
                "//p-dialog//*[self::cc-text-control or self::div]"
                "[.//label[contains(normalize-space(), 'Password')]]//input",
            ),
            self.ADD_POPUP_PASSWORD,
        ]

        password_input = self.first_available_clickable(password_locators)
        if password_input is None:
            visible_inputs = [
                input_element
                for input_element in self.driver.find_elements(*self.POPUP_INPUTS)
                if input_element.is_displayed() and input_element.is_enabled()
            ]
            if not visible_inputs:
                raise TimeoutException("No visible password input was found in the Edit popup.")
            password_input = visible_inputs[-1]

        password_input.send_keys(Keys.CONTROL, "a")
        password_input.send_keys(Keys.BACKSPACE)
        password_input.send_keys(password)
        return self

    def is_edit_popup_password_visible(self):
        password_locators = [
            (
                By.XPATH,
                "//p-dialog//*[self::cc-text-control or self::div]"
                "[.//label[contains(normalize-space(), 'Password')]]//input",
            ),
            self.ADD_POPUP_PASSWORD,
        ]

        for locator in password_locators:
            if any(input_element.is_displayed() for input_element in self.driver.find_elements(*locator)):
                return True

        return False

    def toggle_edit_popup_generate_password(self):
        self.log_action("Click Edit popup Generate Password checkbox")
        checkbox_locator = (
            By.XPATH,
            "//p-dialog//*[contains(normalize-space(), 'Generate Password')]"
            "/ancestor::*[self::cc-checkbox-control or self::div][1]//*[contains(@class, 'p-checkbox-box')]",
        )
        checkbox = self.wait.until(ec.element_to_be_clickable(checkbox_locator))
        self.click_element(checkbox)
        return self

    def is_add_popup_password_visible(self):
        password_locator = (
            By.XPATH,
            "//p-dialog//cc-text-control[.//label[contains(normalize-space(), 'Password')]]//input",
        )
        return any(input_element.is_displayed() for input_element in self.driver.find_elements(*password_locator))

    def toggle_add_popup_generate_password(self):
        self.log_action("Click Add popup Generate Password checkbox")
        checkbox_locator = (By.XPATH, "//*[@id='generatePasswords']//*[contains(@class, 'p-checkbox-box')]")
        checkbox = self.wait.until(ec.element_to_be_clickable(checkbox_locator))
        self.driver.execute_script("arguments[0].click();", checkbox)
        self.wait.until(lambda _: "p-highlight" in self.driver.find_element(*checkbox_locator).get_attribute("class"))
        return self

    def edit_popup_dropdown_values(self):
        return [
            label.text.strip()
            for label in self.driver.find_elements(*self.POPUP_DROPDOWN_LABELS)
            if label.is_displayed() and label.text.strip()
        ]

    def edit_popup_type_value(self):
        dropdown_values = self.edit_popup_dropdown_values()
        return dropdown_values[0] if dropdown_values else ""

    def edit_popup_transport_type_value(self):
        dropdown_values = self.edit_popup_dropdown_values()
        return dropdown_values[1] if len(dropdown_values) > 1 else ""

    def dropdown_option_labels(self):
        options = self.wait.until(
            lambda _: [
                option
                for option in self.driver.find_elements(By.XPATH, "//*[@role='option']")
                if option.is_displayed()
            ]
        )
        return [
            (option.get_attribute("aria-label") or option.text).strip()
            for option in options
            if (option.get_attribute("aria-label") or option.text).strip()
        ]

    def choose_first_different_dropdown_option(self, dropdown_locators, current_value):
        self.log_action(f"Open dropdown to choose value different from '{current_value}'")
        self.click_first_available(dropdown_locators)
        current_value = str(current_value or "").strip().lower()
        option_labels = self.dropdown_option_labels()
        new_value = next((label for label in option_labels if label.lower() != current_value), None)
        if new_value is None:
            ActionChains(self.driver).send_keys(Keys.ESCAPE).perform()
            raise AssertionError(f"Expected a different dropdown option, but only found: {option_labels}")

        self.choose_open_dropdown_option(new_value)
        return new_value

    def choose_open_dropdown_option(self, option_text):
        self.log_action(f"Choose dropdown option: {option_text}")
        lower_option_text = option_text.lower()
        option_locator = (
            By.XPATH,
            "//*[@role='option']"
            f"[translate(normalize-space(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz')='{lower_option_text}' "
            f"or translate(@aria-label, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz')='{lower_option_text}']",
        )
        self.click_element(self.wait.until(ec.element_to_be_clickable(option_locator)))
        self.wait.until(ec.invisibility_of_element_located(self.DROPDOWN_PANEL))
        return self

    def choose_different_extension_type(self):
        return self.choose_first_different_dropdown_option(self.ADD_POPUP_TYPE, self.edit_popup_type_value())

    def choose_different_transport_type(self):
        return self.choose_first_different_dropdown_option(
            self.ADD_POPUP_TRANSPORT_TYPE,
            self.edit_popup_transport_type_value(),
        )

    def popup_contains_value(self, expected_value) -> bool:
        expected_value = str(expected_value or "").strip()
        if not expected_value:
            return True

        return any(expected_value == value or expected_value in value for value in self.popup_field_values())

    def is_paginator_button_disabled(self, locator):
        button = self.wait.until(ec.presence_of_element_located(locator))
        classes = button.get_attribute("class") or ""
        return bool(button.get_attribute("disabled")) or "p-disabled" in classes

    def current_page_number(self):
        buttons = self.driver.find_elements(*self.CURRENT_PAGE_BUTTON)
        if not buttons:
            return None

        text = buttons[0].text.strip()
        return int(text) if text.isdigit() else text

    def go_to_first_page(self):
        self.log_action("Click paginator First Page")
        first_page_button = self.wait.until(ec.presence_of_element_located(self.FIRST_PAGE_BUTTON))
        if self.is_paginator_button_disabled(self.FIRST_PAGE_BUTTON):
            self.log_action("First Page is disabled")
            return self

        first_row = self.visible_table_rows()[0] if self.visible_table_rows() else None
        first_page_button.click()
        if first_row:
            self.wait.until(ec.staleness_of(first_row))
        return self

    def go_to_next_page(self):
        self.log_action("Click paginator Next Page")
        next_page_button = self.wait.until(ec.presence_of_element_located(self.NEXT_PAGE_BUTTON))
        if self.is_paginator_button_disabled(self.NEXT_PAGE_BUTTON):
            self.log_action("Next Page is disabled")
            return False

        first_row = self.visible_table_rows()[0] if self.visible_table_rows() else None
        next_page_button.click()
        if first_row:
            self.wait.until(ec.staleness_of(first_row))
        return True

    def go_to_previous_page(self):
        self.log_action("Click paginator Previous Page")
        previous_page_button = self.wait.until(ec.presence_of_element_located(self.PREVIOUS_PAGE_BUTTON))
        if self.is_paginator_button_disabled(self.PREVIOUS_PAGE_BUTTON):
            self.log_action("Previous Page is disabled")
            return False

        first_row = self.visible_table_rows()[0] if self.visible_table_rows() else None
        previous_page_button.click()
        if first_row:
            self.wait.until(ec.staleness_of(first_row))
        return True

    def all_visible_table_records(self):
        self.go_to_first_page()
        records = []

        while True:
            records.extend(self.visible_table_records())
            if not self.go_to_next_page():
                break

        return records

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

        self.log_action("Click Add")
        self.wait.until(ec.element_to_be_clickable(self.ADD_BUTTON)).click()
        self.wait.until(ec.visibility_of_element_located(self.ADD_POPUP))
        self.wait.until(lambda _: self.is_add_popup_open())
        self.wait.until(lambda _: self.has_add_popup_controls())
        self.log_action("Add popup opened")
        return self

    def open_bottom_delete_popup(self):
        self.log_action("Click bottom Delete")
        self.click_element(self.wait.until(ec.element_to_be_clickable(self.DELETE_BUTTON)))
        self.wait.until(ec.visibility_of_element_located(self.CONFIRM_DIALOG))
        self.wait.until(lambda _: self.is_delete_confirmation_open())
        self.confirm_delete_confirmation()
        self.wait.until(ec.visibility_of_element_located(self.ADD_POPUP))
        self.wait.until(lambda _: self.is_add_popup_open())
        self.log_action("Bottom delete range popup opened")
        return self

    def close_add_popup(self):
        if not self.is_add_popup_open():
            return self

        self.log_action("Click popup Cancel")
        self.wait.until(ec.element_to_be_clickable(self.ADD_POPUP_CANCEL)).click()
        try:
            self.wait.until(ec.invisibility_of_element_located(self.ADD_POPUP))
        except TimeoutException:
            ActionChains(self.driver).send_keys(Keys.ESCAPE).perform()
            try:
                self.wait.until(ec.invisibility_of_element_located(self.ADD_POPUP))
            except TimeoutException:
                pass
        return self

    def fill_add_popup(self, start, end, password=None):
        self.log_action(f"Fill popup range start={start}, end={end}")
        self.click_add_popup_start_button(start)
        self.click_add_popup_end_button(end)

        if password:
            self.log_action("Fill popup password")
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

        self.log_action("Click first available matching control")
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
        self.log_action(f"Open dropdown for option: {option_text}")
        self.click_first_available(dropdown_locators)
        self.choose_open_dropdown_option(option_text)
        return self


    def choose_extension_type(self, extension_type="pjsip"):
        return self.choose_dropdown_option(self.ADD_POPUP_TYPE, extension_type)

    def choose_transport_type(self, transport_type="transport-udp"):
        if transport_type in ("udp", "tcp"):
            transport_type = f"transport-{transport_type}"

        return self.choose_dropdown_option(self.ADD_POPUP_TRANSPORT_TYPE, transport_type)

    def click_generate_passwords(self):
        self.log_action("Click Generate Passwords checkbox")
        self.driver.find_element(*self.ADD_POPUP_GENERATE_PASSWORDS).click()

    def click_add_popup_start_button(self, start):
        self.log_action(f"Type range start: {start}")
        start_input = self.wait.until(ec.element_to_be_clickable(self.ADD_POPUP_START_INPUT))
        start_input.send_keys(Keys.CONTROL, "a")
        start_input.send_keys(Keys.BACKSPACE)
        start_input.send_keys(str(start))
        start_input.send_keys(Keys.TAB)

    def click_add_popup_end_button(self, end):
        self.log_action(f"Type range end: {end}")
        end_input = self.wait.until(ec.element_to_be_clickable(self.ADD_POPUP_END_INPUT))
        end_input.send_keys(Keys.CONTROL, "a")
        end_input.send_keys(Keys.BACKSPACE)
        end_input.send_keys(str(end))
        end_input.send_keys(Keys.TAB)
    
    def submit_add_popup(self):
        self.log_action("Click popup Submit")
        submit_button = self.driver.find_element(*self.ADD_POPUP_SUBMIT)
        self.click_element(submit_button)

    def submit_edit_popup(self):
        self.submit_add_popup()
        self.wait.until(ec.invisibility_of_element_located(self.ADD_POPUP))
        return self

    def submit_popup_and_wait_closed(self):
        self.log_action("Submit popup and wait until it closes")
        self.submit_add_popup()
        self.wait.until(ec.invisibility_of_element_located(self.ADD_POPUP))
        return self

    def click_publish(self):
        self.log_action("Click Publish")
        publish_button = self.wait.until(ec.element_to_be_clickable(self.PUBLISH_BUTTON))
        self.click_element(publish_button)
        return self

    def go_to_last_page(self):
        self.log_action("Click paginator Last Page")
        last_page_button = self.wait.until(ec.presence_of_element_located(self.LAST_PAGE_BUTTON))
        if last_page_button.get_attribute("disabled") or "p-disabled" in last_page_button.get_attribute("class"):
            self.log_action("Last Page is disabled")
            return self

        first_row = self.visible_table_rows()[0] if self.visible_table_rows() else None
        self.wait.until(ec.element_to_be_clickable(self.LAST_PAGE_BUTTON)).click()
        if first_row:
            self.wait.until(ec.staleness_of(first_row))
        return self
