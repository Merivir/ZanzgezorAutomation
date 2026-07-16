from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import ElementClickInterceptedException, StaleElementReferenceException, TimeoutException

from tests.helpers.selenium_waits import wait_for_ui_idle


class ExtensionsPage:
    TABLE_DATA_HEADERS = ["Extension", "Real Extension", "Password", "Type", "Transport type", "Status"]
    TABLE_HEADER_ALIASES = {
        "extension": "Extension",
        "real ext": "Real Extension",
        "real extension": "Real Extension",
        "number": "Real Extension",
        "password": "Password",
        "type": "Type",
        "transport type": "Transport type",
        "transport": "Transport type",
        "status": "Status",
    }

    PAGE_ROOT = (
        "(//*[self::cc-main-page or self::cc-main or contains(@class, 'pageContainer')]"
        "[.//h1[normalize-space()='Extensions']])[last()]"
    )
    ARIA_LOWER = "translate(@aria-label, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz')"

    # Main page locators
    EXTENSIONS_HEADER = (By.XPATH, PAGE_ROOT + "//h1[normalize-space()='Extensions']")
    SEARCH_INPUT = (By.XPATH, PAGE_ROOT + "//cc-dynamic-filter//cc-text-control//input")
    SEARCH_BUTTON = (
        By.XPATH,
        PAGE_ROOT
        + "//cc-dynamic-filter//button[.//span[normalize-space()='Search'] or .//i[normalize-space()='search'] or contains("
        + ARIA_LOWER
        + ", 'search')]",
    )
    CLEAR_FILTERS = (
        By.XPATH,
        PAGE_ROOT
        + "//cc-dynamic-filter//button[.//span[normalize-space()='Clear filters'] or contains("
        + ARIA_LOWER
        + ", 'clear')]",
    )
    EXPORT_BUTTON = (
        By.XPATH,
        PAGE_ROOT
        + "//button[contains(translate(normalize-space(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'export') or .//span[contains(translate(normalize-space(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'export')] or .//i[contains(normalize-space(), 'download') or contains(normalize-space(), 'file_download') or contains(normalize-space(), 'ios_share')] or contains("
        + ARIA_LOWER
        + ", 'export')]",
    )
    EXPORT_CSV_OPTION = (By.XPATH, "//div[contains(@class, 'export-table-items')]//*[normalize-space()='CSV']")
    ADD_BUTTON = (
        By.XPATH,
        PAGE_ROOT
        + "//cc-dynamic-actions//button[.//span[normalize-space()='Add'] or .//i[normalize-space()='add'] or contains("
        + ARIA_LOWER
        + ", 'add')]",
    )
    DELETE_BUTTON = (
        By.XPATH,
        PAGE_ROOT
        + "//cc-dynamic-actions//button[.//span[normalize-space()='Delete'] or .//i[normalize-space()='delete'] or contains("
        + ARIA_LOWER
        + ", 'delete')]",
    )
    PUBLISH_BUTTON = (
        By.XPATH,
        PAGE_ROOT
        + "//cc-dynamic-actions//button[.//span[normalize-space()='Publish'] or .//i[normalize-space()='publish'] or contains("
        + ARIA_LOWER
        + ", 'publish')]",
    )
    
    # Table locators
    TABLE = (By.XPATH, PAGE_ROOT + "//table")
    COLUMN_TOGGLE = (
        By.XPATH,
        PAGE_ROOT
        + "//p-multiselect//*[@role='combobox' or contains(@class, 'p-multiselect-trigger') or contains(@class, 'p-multiselect-label')][1]",
    )
    COLUMN_OPTIONS = (By.XPATH, "//div[contains(@class, 'p-multiselect-panel')]//li[@role='option']")
    COLUMN_PANEL = (By.XPATH, "//div[contains(@class, 'p-multiselect-panel')]")
    TABLE_HEADERS = (By.XPATH, PAGE_ROOT + "//table//thead//th")
    EXTENSION_SORT_HEADER = (
        By.XPATH,
        PAGE_ROOT + "//table//thead//th[.//*[normalize-space()='Extension'] or normalize-space()='Extension'][1]",
    )
    TABLE_ROWS = (By.XPATH, PAGE_ROOT + "//table//tbody/tr[not(contains(@class, 'p-datatable-emptymessage'))]")
    ROW_EDIT_BUTTON = (By.XPATH, ".//button[.//i[normalize-space()='edit'] or contains(@aria-label, 'Edit')]")
    ROW_MOBILE_BUTTON = (By.XPATH, ".//button[.//i[normalize-space()='phone'] or contains(@aria-label, 'Mobile')]")
    ROW_DELETE_BUTTON = (By.XPATH, ".//button[.//i[normalize-space()='delete'] or contains(@aria-label, 'Delete')]")
    EMPTY_TABLE_MESSAGE = (By.XPATH, PAGE_ROOT + "//table//tbody/tr/td")
    SUCCESS_NOTIFICATION = (
        By.CSS_SELECTOR,
        ".p-toast-message-success, .p-message-success, [role='alert'][class*='success']",
    )
    FIRST_PAGE_BUTTON = (By.XPATH, PAGE_ROOT + "//button[@aria-label='First Page']")
    NEXT_PAGE_BUTTON = (By.XPATH, PAGE_ROOT + "//button[@aria-label='Next Page']")
    LAST_PAGE_BUTTON = (By.XPATH, PAGE_ROOT + "//button[@aria-label='Last Page']")
    CURRENT_PAGE_BUTTON = (By.XPATH, PAGE_ROOT + "//button[contains(@class, 'p-paginator-page') and contains(@class, 'p-highlight')]")
    PREVIOUS_PAGE_BUTTON = (By.XPATH, PAGE_ROOT + "//button[@aria-label='Previous Page']")
    DROPDOWN_PANEL = (By.XPATH, "//div[contains(@class, 'p-dropdown-panel')]")

    # Confirmation dialog locators
    CONFIRM_DIALOG = (
        By.XPATH,
        "//div[@role='alertdialog' and contains(concat(' ', normalize-space(@class), ' '), ' p-confirm-dialog ')]",
    )
    CONFIRM_MESSAGE = (By.XPATH, ".//*[contains(@class, 'p-confirm-dialog-message')]")
    CONFIRM_CANCEL = (
        By.XPATH,
        ".//button[contains(@class, 'p-confirm-dialog-reject') or "
        ".//span[normalize-space()='Reject' or normalize-space()='Cancel' or normalize-space()='No']]",
    )
    CONFIRM_ACCEPT = (
        By.XPATH,
        ".//button[contains(@class, 'p-confirm-dialog-accept') or "
        ".//span[normalize-space()='Accept' or normalize-space()='Yes' or normalize-space()='OK']]",
    )

    # Add popup locators
    ADD_POPUP = (By.XPATH, "//p-dialog//div[contains(@class, 'p-dialog') or @role='dialog'] | //div[@role='dialog']")
    ADD_POPUP_TYPE = [
        (By.XPATH, "//p-dialog//cc-dropdown-control[.//label[normalize-space()='Type']]//*[@role='combobox' or contains(@class, 'p-dropdown')][1]"),
        (By.XPATH, "(//cc-dynamic-popup//*[@role='combobox'])[1]"),
        (By.XPATH, "(//p-dialog//*[@role='combobox'])[1]"),
    ]
    ADD_POPUP_TRANSPORT_TYPE = [
        (By.XPATH, "//p-dialog//cc-dropdown-control[.//label[contains(normalize-space(), 'Transport')]]//*[@role='combobox' or contains(@class, 'p-dropdown')][1]"),
        (By.XPATH, "(//cc-dynamic-popup//*[@role='combobox'])[2]"),
        (By.XPATH, "(//p-dialog//*[@role='combobox'])[2]"),
    ]
    ADD_POPUP_START_INPUT = (
        By.XPATH,
        "//p-dialog//*[@id='rangeStart']//input | //p-dialog//cc-text-control[.//label[contains(normalize-space(), 'Start')]]//input",
    )
    ADD_POPUP_END_INPUT = (
        By.XPATH,
        "//p-dialog//*[@id='rangeEnd']//input | //p-dialog//cc-text-control[.//label[contains(normalize-space(), 'End')]]//input",
    )
    ADD_POPUP_GENERATE_PASSWORDS = (
        By.XPATH,
        "//p-dialog//*[@id='generatePasswords']//*[contains(@class, 'p-checkbox-box')]"
        " | //p-dialog//*[contains(normalize-space(), 'Generate Password')]"
        "/ancestor::*[self::cc-checkbox-control or self::div][1]//*[contains(@class, 'p-checkbox-box')]",
    )
    ADD_POPUP_PASSWORD = (By.XPATH, "//p-dialog//cc-text-control[.//label[contains(normalize-space(), 'Password')]]//input")
    ADD_POPUP_SUBMIT = (
        By.XPATH,
        "(//p-dialog//button[.//span[normalize-space()='Submit'] or contains(normalize-space(), 'Submit') or contains(normalize-space(), 'Save')])[last()]",
    )
    ADD_POPUP_CANCEL = (
        By.XPATH,
        "(//p-dialog//button[.//span[normalize-space()='Cancel'] or contains(normalize-space(), 'Cancel')])[last()]",
    )
    ADD_POPUP_REQUIRED_ERRORS = (By.XPATH, "//p-dialog//*[contains(@class, 'cc-control-error') and normalize-space()='Required field']")
    POPUP_INPUTS = (By.XPATH, "//p-dialog//input")
    POPUP = (By.XPATH, "//p-dialog")
    POPUP_DROPDOWN_LABELS = (By.XPATH, "//p-dialog//*[contains(@class, 'p-dropdown-label') or contains(@class, 'p-multiselect-label')]")

    # Mobile popup locators
    MOBILE_POPUP = (
        By.XPATH,
        "//div[@role='dialog' and (.//cc-text-control[.//label[contains(normalize-space(), 'New')]] or .//*[contains(normalize-space(), 'Active phone')] or .//*[normalize-space()='DYNAMIC.ACTIONS.MOBILE'])]",
    )
    MOBILE_NEW_PHONE_INPUT = (
        By.XPATH,
        "//div[@role='dialog']//cc-text-control[.//label[contains(normalize-space(), 'New')]]//input",
    )
    MOBILE_ACTIVE_PHONE_LABEL = (
        By.XPATH,
        "//div[@role='dialog']//*[contains(normalize-space(), 'Active phone')]",
    )
    MOBILE_PHONE_OPTIONS = (By.XPATH, "//div[@role='dialog']//p-radiobutton")
    MOBILE_CANCEL = (
        By.XPATH,
        "(//div[@role='dialog']//button[.//span[normalize-space()='Cancel'] or contains(normalize-space(), 'Cancel')])[last()]",
    )
    MOBILE_SUBMIT = (
        By.XPATH,
        "(//div[@role='dialog']//button[.//span[normalize-space()='Submit'] or contains(normalize-space(), 'Submit')])[last()]",
    )

    def __init__(self, driver, wait):
        self.driver = driver
        self.wait = wait

    def wait_for_ui_idle(self):
        wait_for_ui_idle(self.driver, self.wait)
        return self

    def log_action(self, message):
        print(f"[Extensions] {message}", flush=True)

    def wait_until_loaded(self):
        self.log_action("Wait until Extensions page is loaded")
        # the presence of the header is our signal that the page is ready for interaction.
        self.wait.until(ec.presence_of_element_located(self.EXTENSIONS_HEADER))

    def wait_for_success_notification(self):
        self.log_action("Wait for success notification")
        self.wait.until(ec.visibility_of_element_located(self.SUCCESS_NOTIFICATION))
        return self

    def reload_extensions_table(self):
        self.log_action("Reload Extensions table")
        self.driver.refresh()
        self.wait_until_loaded()
        return self

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
        # Page readiness should not depend on permission-specific action buttons.
        return any(element.is_displayed() for element in self.driver.find_elements(*self.EXTENSIONS_HEADER)) and any(
            element.is_displayed() for element in self.driver.find_elements(*self.TABLE)
        )

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

    def wait_for_add_popup_submit_enabled(self):
        self.log_action("Verify popup Submit is enabled")
        self.wait.until(lambda _: self.is_add_popup_submit_enabled(), "Popup Submit button is enabled")
        return self

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
        self.log_action(f"Verify required error messages are shown for: {', '.join(labels)}")
        self.wait.until(
            lambda _: self.has_add_popup_required_errors_for(labels),
            f"Required error messages visible for: {', '.join(labels)}",
        )
        self.log_action(f"Required error messages are shown for: {', '.join(labels)}")

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
        self.log_action(f"Verify required validation is shown for: {', '.join(labels)}")
        self.wait.until(
            lambda _: self.has_add_popup_required_validation_for(labels),
            f"Required validation visible for: {', '.join(labels)}",
        )
        self.log_action(f"Required validation is shown for: {', '.join(labels)}")

    def wait_for_invalid_state_for_label(self, label_text):
        self.log_action(f"Verify invalid state is shown for field: {label_text}")
        self.wait.until(lambda _: self.has_invalid_state_for_label(label_text), f"Invalid state visible for field: {label_text}")
        self.log_action(f"Invalid state is shown for field: {label_text}")

    def log_add_popup_required_validation_state(self, labels):
        for label in labels:
            has_required_error = self.has_required_error_for_label(label)
            has_invalid_state = self.has_invalid_state_for_label(label)
            state = "shown" if has_required_error or has_invalid_state else "not shown"
            self.log_action(
                f"Validation for {label}: {state} "
                f"(required message={has_required_error}, invalid state={has_invalid_state})"
            )
        return self

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
        try:
            self.log_action("Click CSV export option")
            self.click_element(self.wait.until(ec.element_to_be_clickable(self.EXPORT_CSV_OPTION)))
        except TimeoutException:
            self.log_action("CSV download started directly from Export button")
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

    @staticmethod
    def normalized_header_key(header_text):
        return " ".join(str(header_text or "").strip().split()).lower()

    def normalized_table_header(self, header_text):
        return self.TABLE_HEADER_ALIASES.get(self.normalized_header_key(header_text))

    def wait_for_visible_table_column_count(self, expected_count):
        self.wait.until(
            lambda _: self.visible_table_column_count() == expected_count,
            f"Visible table column count becomes {expected_count}",
        )
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
            options = self.column_visibility_options()
        except StaleElementReferenceException:
            options = self.column_visibility_options()

        labels = []
        for option in options:
            label = (option.get_attribute("aria-label") or option.text or "").strip()
            if label:
                labels.append(label)
        return labels

    def column_visibility_option_count(self) -> int:
        return len(self.column_visibility_option_labels())

    def is_column_option_selected(self, option) -> bool:
        return option.get_attribute("aria-checked") == "true"

    def set_column_option_visibility(self, label, visible):
        label_literal = self.xpath_literal(label)
        option_locator = (
            By.XPATH,
            "//div[contains(@class, 'p-multiselect-panel')]//li[@role='option' and "
            + "(@aria-label="
            + label_literal
            + " or normalize-space()="
            + label_literal
            + ")]",
        )
        option = self.wait.until(ec.element_to_be_clickable(option_locator))
        if self.is_column_option_selected(option) != visible:
            self.log_action(f"Set column '{label}' visible={visible}")
            self.click_element(option)
            try:
                self.wait.until(lambda _: self.driver.find_element(*option_locator).get_attribute("aria-checked") == str(visible).lower())
            except TimeoutException:
                pass
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

    def visible_extension_numbers(self):
        numbers = []
        for row in self.visible_table_rows():
            try:
                value = self.get_extension_column_value(row)
                if value.isdigit():
                    numbers.append(int(value))
            except StaleElementReferenceException:
                return self.visible_extension_numbers()
        return numbers

    def sort_extensions_descending(self, force_refresh=False):
        self.log_action("Sort Extension descending")
        if force_refresh and self.visible_extension_numbers() == sorted(self.visible_extension_numbers(), reverse=True):
            self.click_element(self.wait.until(ec.element_to_be_clickable(self.EXTENSION_SORT_HEADER)))

        for _ in range(3):
            numbers = self.visible_extension_numbers()
            if numbers and numbers == sorted(numbers, reverse=True):
                return self

            previous_row = self.visible_table_rows()[0] if self.visible_table_rows() else None
            self.click_element(self.wait.until(ec.element_to_be_clickable(self.EXTENSION_SORT_HEADER)))
            if previous_row is not None:
                try:
                    self.wait.until(ec.staleness_of(previous_row))
                except TimeoutException:
                    pass

        numbers = self.visible_extension_numbers()
        assert numbers == sorted(numbers, reverse=True), f"Extension column is not descending: {numbers}"
        return self

    def reveal_extensions_descending(self, extension_numbers):
        expected = {str(number) for number in extension_numbers}
        for _ in range(3):
            self.reload_extensions_table()
            for _ in range(3):
                visible = {self.get_extension_column_value(row) for row in self.visible_table_rows()}
                if expected.issubset(visible):
                    return self

                previous_row = self.visible_table_rows()[0] if self.visible_table_rows() else None
                self.click_element(self.wait.until(ec.element_to_be_clickable(self.EXTENSION_SORT_HEADER)))
                if previous_row is not None:
                    try:
                        self.wait.until(ec.staleness_of(previous_row))
                    except TimeoutException:
                        pass

        visible = {self.get_extension_column_value(row) for row in self.visible_table_rows()}
        missing = sorted(expected - visible)
        raise AssertionError(f"New extensions are not visible after reload and descending sort: {missing}")

    def visible_row_for_extension(self, extension_number):
        expected = str(extension_number)
        for row in self.visible_table_rows():
            try:
                if self.get_extension_column_value(row) == expected:
                    return row
            except StaleElementReferenceException:
                return self.visible_row_for_extension(expected)
        return None

    def wait_for_extension_row(self, extension_number):
        return self.wait.until(lambda _: self.visible_row_for_extension(extension_number) or False)

    def visible_table_records(self):
        raw_headers = self.visible_table_headers()
        normalized_headers = [self.normalized_table_header(header) for header in raw_headers]
        records = []

        for row in self.visible_table_rows():
            cells = [cell for cell in row.find_elements(By.XPATH, "./td") if cell.is_displayed()]
            if not cells or cells[0].text.strip() == "No data to display!":
                continue

            record = {}
            for index, cell in enumerate(cells):
                if index >= len(normalized_headers):
                    continue

                header = normalized_headers[index]
                if not header:
                    continue
                if cell.find_elements(By.XPATH, ".//button"):
                    continue

                value = cell.text.strip()
                existing_value = record.get(header)
                if existing_value and not value:
                    continue
                record[header] = value

            if record:
                records.append(record)

        return records

    @staticmethod
    def _is_sensitive_table_header(header):
        return ExtensionsPage.normalized_header_key(header) in {"password"}

    def sanitized_visible_table_text(self):
        headers = self.visible_table_headers()
        rows = []
        for row in self.visible_table_rows():
            values = []
            cells = row.find_elements(By.XPATH, "./td")
            for index, cell in enumerate(cells):
                if cell.find_elements(By.XPATH, ".//button"):
                    continue
                text = cell.text.strip()
                if not text:
                    continue
                header = headers[index] if index < len(headers) else ""
                if self._is_sensitive_table_header(header):
                    text = "<hidden>"
                values.append(text)
            if values:
                rows.append(" | ".join(values))

        if rows:
            return " || ".join(rows)

        return " | ".join(
            cell.text.strip()
            for cell in self.driver.find_elements(*self.EMPTY_TABLE_MESSAGE)
            if cell.is_displayed() and cell.text.strip()
        )
    def table_debug_snapshot(self):
        def safe_value(label, getter):
            try:
                value = getter()
                if isinstance(value, str):
                    return value.strip() or "<empty>"
                return value
            except Exception as error:
                return f"<{label} failed: {error.__class__.__name__}>"

        raw_headers = safe_value("headers", self.visible_table_headers)
        mapped_headers = [self.normalized_table_header(header) or f"unmapped:{header}" for header in raw_headers]
        visible_rows = safe_value("visible rows", lambda: len(self.visible_table_rows()))
        body_rows = safe_value("body rows", lambda: len(self.driver.find_elements(By.XPATH, self.PAGE_ROOT + "//table//tbody/tr")))
        empty_message = safe_value("visible table rows", self.sanitized_visible_table_text)
        search_value = safe_value("search value", lambda: self.driver.find_element(*self.SEARCH_INPUT).get_attribute("value"))

        return {
            "url": self.driver.current_url,
            "headers": raw_headers,
            "mapped_headers": mapped_headers,
            "visible_rows": visible_rows,
            "body_rows": body_rows,
            "empty_message": empty_message,
            "search": search_value,
        }

    def format_table_debug_snapshot(self):
        snapshot = self.table_debug_snapshot()
        return "; ".join(f"{key}={value!r}" for key, value in snapshot.items())
    def first_visible_table_record(self):
        records = self.visible_table_records()
        if not records:
            return None

        return records[0]

    def visible_record_for_extension(self, extension_number):
        expected = str(extension_number)
        return next((record for record in self.visible_table_records() if record.get("Extension") == expected), None)

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
        self.wait.until(
            lambda _: self.is_add_popup_open() or self.is_delete_confirmation_open(),
            "Edit popup opened or associated-mobile warning appeared",
        )
        if self.is_delete_confirmation_open():
            self.log_action("Accept associated-mobile warning before Edit")
            self.accept_visible_confirmation()
        self.wait.until(ec.visibility_of_element_located(self.ADD_POPUP))
        self.wait.until(lambda _: self.is_add_popup_open())
        self.log_action("Edit popup opened")
        return self

    def open_extension_edit_popup(self, extension_number):
        return self.open_row_edit_popup(self.wait_for_extension_row(extension_number))

    def open_first_row_delete_confirmation(self):
        self.log_action("Click row Delete")
        row = self.wait.until(lambda _: self.visible_table_rows()[0] if self.visible_table_rows() else False)
        delete_button = row.find_element(*self.ROW_DELETE_BUTTON)
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", delete_button)
        self.click_element(delete_button)
        self.wait.until(ec.visibility_of_element_located(self.CONFIRM_DIALOG))
        self.log_action("Delete confirmation opened")
        return self

    def open_extension_delete_confirmation(self, extension_number):
        self.log_action(f"Click row Delete for extension {extension_number}")
        row = self.wait_for_extension_row(extension_number)
        delete_button = row.find_element(*self.ROW_DELETE_BUTTON)
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", delete_button)
        self.click_element(delete_button)
        self.wait.until(lambda _: self.visible_confirmation_dialog() or False)
        return self

    def is_delete_confirmation_open(self):
        dialog = self.visible_confirmation_dialog()
        return bool(dialog and dialog.find_elements(*self.CONFIRM_CANCEL) and dialog.find_elements(*self.CONFIRM_ACCEPT))

    def visible_confirmation_dialog(self):
        return next(
            (dialog for dialog in reversed(self.driver.find_elements(*self.CONFIRM_DIALOG)) if dialog.is_displayed()),
            None,
        )

    def confirmation_message(self, dialog=None):
        dialog = dialog or self.visible_confirmation_dialog()
        if dialog is None:
            return ""
        messages = dialog.find_elements(*self.CONFIRM_MESSAGE)
        return messages[0].text.strip() if messages else ""

    def accept_visible_confirmation(self):
        dialog = self.wait.until(lambda _: self.visible_confirmation_dialog() or False)
        button = self.wait.until(lambda _: next((item for item in dialog.find_elements(*self.CONFIRM_ACCEPT) if item.is_displayed() and item.is_enabled()), False))
        self.click_element(button)
        self.wait.until(ec.staleness_of(dialog))
        return self

    def cancel_delete_confirmation(self):
        self.log_action("Click confirmation Reject/Cancel")
        dialog = self.wait.until(lambda _: self.visible_confirmation_dialog() or False)
        button = self.wait.until(lambda _: next((item for item in dialog.find_elements(*self.CONFIRM_CANCEL) if item.is_displayed() and item.is_enabled()), False))
        self.click_element(button)
        self.wait.until(ec.staleness_of(dialog))
        return self

    def confirm_delete_confirmation(self):
        self.log_action("Click confirmation Accept")
        first_message = self.confirmation_message()
        self.accept_visible_confirmation()

        # Some environments show a mobile-association warning first, followed
        # by the actual delete confirmation. Accept both semantic dialogs.
        if "associated mobile" in first_message.lower():
            self.wait.until(lambda _: self.visible_confirmation_dialog() or False)
            self.accept_visible_confirmation()
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
        checkbox_locator = self.ADD_POPUP_GENERATE_PASSWORDS
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
        lower_option_text = str(option_text).strip().lower()
        option_literal = self.xpath_literal(lower_option_text)
        option_locator = (
            By.XPATH,
            "//*[@role='option']"
            "[translate(normalize-space(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz')="
            + option_literal
            + " or translate(@aria-label, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz')="
            + option_literal
            + "]",
        )
        self.click_element(
            self.wait.until(
                ec.element_to_be_clickable(option_locator),
                f"Dropdown option {option_text!r} is clickable",
            )
        )
        self.wait.until(ec.invisibility_of_element_located(self.DROPDOWN_PANEL), "Dropdown panel closed")
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

    def visible_paginator_button(self, locator):
        return self.wait.until(
            lambda _: next(
                (button for button in self.driver.find_elements(*locator) if button.is_displayed()),
                False,
            )
        )

    def is_paginator_button_disabled(self, button):
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
        first_page_button = self.visible_paginator_button(self.FIRST_PAGE_BUTTON)
        if self.is_paginator_button_disabled(first_page_button):
            self.log_action("First Page is disabled")
            return self

        first_row = self.visible_table_rows()[0] if self.visible_table_rows() else None
        first_page_button.click()
        if first_row:
            self.wait.until(ec.staleness_of(first_row))
        return self

    def go_to_next_page(self):
        self.log_action("Click paginator Next Page")
        next_page_button = self.visible_paginator_button(self.NEXT_PAGE_BUTTON)
        if self.is_paginator_button_disabled(next_page_button):
            self.log_action("Next Page is disabled")
            return False

        first_row = self.visible_table_rows()[0] if self.visible_table_rows() else None
        next_page_button.click()
        if first_row:
            self.wait.until(ec.staleness_of(first_row))
        return True

    def go_to_previous_page(self):
        self.log_action("Click paginator Previous Page")
        previous_page_button = self.visible_paginator_button(self.PREVIOUS_PAGE_BUTTON)
        if self.is_paginator_button_disabled(previous_page_button):
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

    def wait_until_extension_visible(self, extension_number):
        extension_number = str(extension_number)
        self.wait.until(lambda _: self.has_visible_extension(extension_number))
        return self

    def wait_until_extension_not_visible(self, extension_number):
        extension_number = str(extension_number)
        self.wait.until(lambda _: not self.has_visible_extension(extension_number))
        return self

    def assert_extensions_exist(self, extension_numbers):
        expected = [str(number) for number in extension_numbers]
        self.reveal_extensions_descending(expected)
        visible = {self.get_extension_column_value(row) for row in self.visible_table_rows()}
        missing_extensions = [number for number in expected if number not in visible]

        assert not missing_extensions, (
            f"Expected extensions to exist, but these were missing: {missing_extensions}"
        )

        return self

    def close_blocking_dialogs_if_any(self):
        if self.is_delete_confirmation_open():
            self.cancel_delete_confirmation()

        if self.is_add_popup_open():
            self.close_add_popup()

        return self
    
    def open_add_popup(self):
        if self.is_add_popup_open():
            self.log_action("Add popup is already open")
            return self

        self.log_action("Click Add")
        self.wait.until(ec.element_to_be_clickable(self.ADD_BUTTON), "Add button is clickable").click()
        self.log_action("Wait for Add popup dialog")
        self.wait.until(ec.visibility_of_element_located(self.ADD_POPUP), "Add popup dialog is visible")
        self.log_action("Verify Add popup is open")
        self.wait.until(lambda _: self.is_add_popup_open(), "Add popup is open")
        self.log_action("Verify Add popup controls are visible")
        self.wait.until(lambda _: self.has_add_popup_controls(), "Add popup controls are visible")
        self.log_action("Add popup opened")
        return self

    def open_bottom_delete_popup(self):
        # The global action can become inert after server-side table sorting in
        # some environments; a route-preserving reload restores the action.
        self.reload_extensions_table()
        self.log_action("Click bottom Delete")
        self.click_element(self.wait.until(ec.element_to_be_clickable(self.DELETE_BUTTON), "Bottom Delete button is clickable"))
        self.wait.until(
            lambda _: self.is_add_popup_open() or self.is_delete_confirmation_open(),
            "Edit popup opened or associated-mobile warning appeared",
        )
        if self.is_delete_confirmation_open():
            self.confirm_delete_confirmation()
        self.log_action("Wait for bottom delete range popup")
        self.wait.until(ec.visibility_of_element_located(self.ADD_POPUP), "Bottom delete range popup is visible")
        self.wait.until(lambda _: self.is_add_popup_open(), "Bottom delete range popup is open")
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
            password_input = self.wait.until(ec.element_to_be_clickable(self.ADD_POPUP_PASSWORD))
            password_input.send_keys(Keys.CONTROL, "a")
            password_input.send_keys(Keys.BACKSPACE)
            password_input.send_keys(password)

        return self

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
            self.wait.until(ec.invisibility_of_element_located(self.DROPDOWN_PANEL), "Dropdown panel closed")
        except TimeoutException:
            ActionChains(self.driver).send_keys(Keys.ESCAPE).perform()
        return self

    def focus_and_blur_add_popup_field(self, locator, label_text, clear=False):
        self.log_action(f"Focus field: {label_text}")
        element = self.wait.until(ec.element_to_be_clickable(locator), f"{label_text} field is clickable")
        element.click()
        if clear:
            self.log_action(f"Clear field: {label_text}")
            element.send_keys(Keys.CONTROL, "a")
            element.send_keys(Keys.BACKSPACE)
        self.log_action(f"Leave field to trigger validation: {label_text}")
        element.send_keys(Keys.TAB)
        return self

    def focus_and_blur_first_available_add_popup_field(self, locators, label_text):
        self.log_action(f"Open/focus dropdown field: {label_text}")
        element = self.first_available_clickable(locators, description=f"{label_text} dropdown is clickable")
        if element is None:
            self.log_action(f"Skip field because it was not clickable: {label_text}")
            return self

        self.click_element(element)
        self.log_action(f"Leave dropdown to trigger validation: {label_text}")
        ActionChains(self.driver).send_keys(Keys.TAB).perform()
        return self

    def touch_add_popup_required_fields(self):
        self.log_action("Start Add popup required-fields validation check")
        self.focus_and_blur_add_popup_field(self.ADD_POPUP_PASSWORD, "Password", clear=True)
        self.focus_and_blur_first_available_add_popup_field(self.ADD_POPUP_TYPE, "Type")
        self.focus_and_blur_first_available_add_popup_field(self.ADD_POPUP_TRANSPORT_TYPE, "Transport type")
        self.log_action("Required fields were touched and left empty")
        return self

    def click_first_available(self, locators):
        element = self.first_available_clickable(locators)
        if element is None:
            raise TimeoutException(f"None of these locators became clickable: {locators}")

        self.log_action("Click first available matching control")
        self.click_element(element)
        return element

    def first_available_clickable(self, locators, description="matching control is clickable"):
        quick_wait = WebDriverWait(self.driver, 2, poll_frequency=0.2)
        total = len(locators)
        for index, locator in enumerate(locators, start=1):
            self.log_action(f"Try {description} locator {index}/{total}")
            try:
                element = quick_wait.until(ec.element_to_be_clickable(locator))
                self.log_action(f"Found {description} using locator {index}/{total}")
                return element
            except TimeoutException:
                self.log_action(f"Locator {index}/{total} not clickable for: {description}")
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
    
    def submit_add_popup(self, wait_until_closed=False):
        self.log_action("Click popup Submit")
        self.wait_for_add_popup_submit_enabled()
        submit_button = self.wait.until(ec.element_to_be_clickable(self.ADD_POPUP_SUBMIT), "Popup Submit button is clickable")
        self.click_element(submit_button)

        if wait_until_closed:
            self.wait.until(ec.invisibility_of_element_located(self.ADD_POPUP))

        return self

    def submit_edit_popup(self):
        return self.submit_add_popup(wait_until_closed=True).wait_for_success_notification()

    def submit_popup_and_wait_closed(self):
        self.log_action("Submit popup and wait until it closes")
        return self.submit_add_popup(wait_until_closed=True)

    def create_extension(
        self,
        extension_number,
        end_extension_number=None,
        extension_type="pjsip",
        transport_type="udp",
        password="Test1234",
    ):
        if end_extension_number is None:
            end_extension_number = extension_number

        return (
            self.close_blocking_dialogs_if_any()
            .clear_search_and_submit()
            .open_add_popup()
            .choose_extension_type(extension_type)
            .choose_transport_type(transport_type)
            .fill_add_popup(extension_number, end_extension_number, password=password)
            .submit_add_popup(wait_until_closed=True)
            .wait_for_success_notification()
            .reveal_extensions_descending(range(int(extension_number), int(end_extension_number) + 1))
        )

    def delete_extension_if_exists(self, extension_number):
        self.search_for_extension_number(extension_number)
        self.wait_for_ui_idle()
        if self.visible_row_for_extension(extension_number) is None:
            self.log_action(f"Extension {extension_number} is not present; no UI deletion needed")
            return self

        return (
            self.open_extension_delete_confirmation(extension_number)
            .confirm_delete_confirmation()
            .wait_until_extension_not_visible(extension_number)
        )

    def cancel_first_row_delete(self):
        return self.open_first_row_delete_confirmation().cancel_delete_confirmation()

    def click_publish(self):
        self.log_action("Click Publish")
        publish_button = self.wait.until(ec.element_to_be_clickable(self.PUBLISH_BUTTON))
        self.click_element(publish_button)
        return self

    def publish_changes(self):
        self.log_action("Publish changes")
        self.click_publish()

        if self.is_delete_confirmation_open():
            self.confirm_delete_confirmation()

        self.wait_until_loaded()
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

    @staticmethod
    def xpath_literal(value):
        value = str(value)
        if "'" not in value:
            return f"'{value}'"
        if '"' not in value:
            return f'"{value}"'
        parts = value.split("'")
        return "concat(" + ', "\'", '.join(f"'{part}'" for part in parts) + ")"

