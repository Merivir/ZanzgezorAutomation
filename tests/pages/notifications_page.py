import re

from selenium.common.exceptions import ElementClickInterceptedException, StaleElementReferenceException, TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as ec

from tests.helpers.selenium_waits import wait_for_ui_idle


class NotificationsPage:
    TABLE_DATA_HEADERS = ["Category", "Theme", "Type", "Persist", "Active", "Show Time (s)", "Expire Time (h)"]

    PAGE_ROOT = (
        "(//cc-notification-types"
        " | //*[self::cc-main-page or self::cc-main or contains(@class, 'pageContainer')]"
        "[.//h1[normalize-space()='Notifications']])[last()]"
    )
    LABEL_LOWER = "translate(normalize-space(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz')"
    ARIA_LOWER = "translate(@aria-label, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz')"

    HEADER = (By.XPATH, PAGE_ROOT + "//h1[normalize-space()='Notifications']")
    CATEGORY_FILTER = (
        By.XPATH,
        PAGE_ROOT + "//cc-text-control[.//label[contains(" + LABEL_LOWER + ", 'category')]]//input",
    )
    TYPE_FILTER = (
        By.XPATH,
        PAGE_ROOT
        + "//cc-dropdown-control[.//label[contains("
        + LABEL_LOWER
        + ", 'type')]]//*[@role='combobox' or contains(@class, 'p-dropdown')][1]",
    )
    THEME_FILTER = (
        By.XPATH,
        PAGE_ROOT
        + "//cc-dropdown-control[.//label[contains("
        + LABEL_LOWER
        + ", 'theme')]]//*[@role='combobox' or contains(@class, 'p-dropdown')][1]",
    )
    ACTIVE_FILTER = (
        By.XPATH,
        PAGE_ROOT
        + "//cc-dropdown-control[.//label[contains("
        + LABEL_LOWER
        + ", 'active')]]//*[@role='combobox' or contains(@class, 'p-dropdown')][1]",
    )
    SEARCH_BUTTON = (
        By.XPATH,
        PAGE_ROOT
        + "//cc-dynamic-filter//button[.//span[normalize-space()='Search'] or .//i[normalize-space()='search'] or contains("
        + ARIA_LOWER
        + ", 'search')]",
    )
    CLEAR_FILTERS_BUTTON = (
        By.XPATH,
        PAGE_ROOT
        + "//cc-dynamic-filter//button[.//span[normalize-space()='Clear filters'] or contains("
        + ARIA_LOWER
        + ", 'clear')]",
    )
    RESULTS_COUNT = (By.XPATH, PAGE_ROOT + "//*[contains(@class, 'countResults')]")
    TABLE = (By.XPATH, PAGE_ROOT + "//table")
    TABLE_HEADERS = (By.XPATH, PAGE_ROOT + "//table//thead//th")
    TABLE_ROWS = (By.XPATH, PAGE_ROOT + "//table//tbody/tr[not(contains(@class, 'p-datatable-emptymessage'))]")
    EMPTY_TABLE_MESSAGE = (
        By.XPATH,
        PAGE_ROOT + "//table//tbody/tr/td[contains(normalize-space(), 'No data')]",
    )
    COLUMN_TOGGLE = (
        By.XPATH,
        PAGE_ROOT
        + "//p-multiselect//*[@role='combobox' or contains(@class, 'p-multiselect-trigger') or contains(@class, 'p-multiselect-label')][1]",
    )
    COLUMN_PANEL = (By.XPATH, "//div[contains(@class, 'p-multiselect-panel')]")
    COLUMN_OPTIONS = (By.XPATH, "//div[contains(@class, 'p-multiselect-panel')]//li[@role='option']")
    DROPDOWN_PANEL = (By.XPATH, "//div[contains(@class, 'p-dropdown-panel')]")
    DROPDOWN_OPTIONS = (By.XPATH, "//*[@role='option']")
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
    POPUP = (By.XPATH, "//p-dialog//div[contains(@class, 'p-dialog') or @role='dialog'] | //div[@role='dialog']")
    POPUP_CANCEL = (
        By.XPATH,
        "(//p-dialog//button[.//span[normalize-space()='Cancel'] or contains(normalize-space(), 'Cancel')]"
        " | //div[@role='dialog']//button[.//span[normalize-space()='Cancel'] or contains(normalize-space(), 'Cancel')])[last()]",
    )
    POPUP_SUBMIT = (
        By.XPATH,
        "(//p-dialog//button[contains(normalize-space(), 'Submit') or contains(normalize-space(), 'Save')]"
        " | //div[@role='dialog']//button[contains(normalize-space(), 'Submit') or contains(normalize-space(), 'Save')])[last()]",
    )
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
    ROW_EDIT_BUTTON = (By.XPATH, ".//button[.//i[normalize-space()='edit'] or contains(@aria-label, 'Edit')]")
    ROW_DELETE_BUTTON = (By.XPATH, ".//button[.//i[normalize-space()='delete'] or contains(@aria-label, 'Delete')]")
    ROW_TRANSLATE_BUTTON = (
        By.XPATH,
        ".//button[.//i[normalize-space()='translate'] or contains(@aria-label, 'Translate')]",
    )
    FIRST_PAGE_BUTTON = (By.XPATH, PAGE_ROOT + "//button[@aria-label='First Page']")
    PREVIOUS_PAGE_BUTTON = (By.XPATH, PAGE_ROOT + "//button[@aria-label='Previous Page']")
    NEXT_PAGE_BUTTON = (By.XPATH, PAGE_ROOT + "//button[@aria-label='Next Page']")
    LAST_PAGE_BUTTON = (By.XPATH, PAGE_ROOT + "//button[@aria-label='Last Page']")
    ROWS_PER_PAGE = (
        By.XPATH,
        PAGE_ROOT + "//p-paginator//*[@role='combobox' and @aria-label='Rows per page']",
    )

    def __init__(self, driver, wait):
        self.driver = driver
        self.wait = wait

    def wait_for_ui_idle(self):
        wait_for_ui_idle(self.driver, self.wait)
        return self

    def log_action(self, message):
        print(f"[Notifications] {message}", flush=True)

    def wait_until_loaded(self):
        self.log_action("Wait until Notifications page is loaded")
        self.wait.until(ec.visibility_of_element_located(self.HEADER))
        self.wait.until(ec.visibility_of_element_located(self.TABLE))
        self.wait_for_table_ready()
        return self

    def has_visible_element(self, locator):
        return any(element.is_displayed() for element in self.driver.find_elements(*locator))

    def is_loaded(self):
        return self.has_visible_element(self.HEADER) and self.has_visible_element(self.TABLE)

    def has_main_controls(self):
        locators = [
            self.HEADER,
            self.CATEGORY_FILTER,
            self.TYPE_FILTER,
            self.THEME_FILTER,
            self.ACTIVE_FILTER,
            self.SEARCH_BUTTON,
            self.CLEAR_FILTERS_BUTTON,
            self.RESULTS_COUNT,
            self.COLUMN_TOGGLE,
            self.TABLE,
            self.EXPORT_BUTTON,
            self.ADD_BUTTON,
        ]
        return all(self.has_visible_element(locator) for locator in locators)

    def click_element(self, element):
        try:
            element.click()
        except ElementClickInterceptedException:
            self.driver.execute_script("arguments[0].click();", element)
        return self

    def wait_for_table_ready(self):
        self.wait.until(ec.visibility_of_element_located(self.TABLE))
        self.wait.until(lambda _: self.visible_table_rows() or self.has_visible_element(self.EMPTY_TABLE_MESSAGE))
        return self

    def visible_table_rows(self):
        return [row for row in self.driver.find_elements(*self.TABLE_ROWS) if row.is_displayed()]

    def visible_table_headers(self):
        return [
            re.sub(r"\s+", " ", header.text).strip()
            for header in self.driver.find_elements(*self.TABLE_HEADERS)
            if header.is_displayed() and header.text.strip()
        ]

    def visible_table_column_count(self):
        return len(self.visible_table_headers())

    def visible_table_records(self):
        headers = [header for header in self.visible_table_headers() if header in self.TABLE_DATA_HEADERS]
        data_headers = headers or self.TABLE_DATA_HEADERS
        records = []

        for row in self.visible_table_rows():
            cells = [
                re.sub(r"\s+", " ", cell.text).strip()
                for cell in row.find_elements(By.XPATH, "./td")
                if cell.is_displayed() and cell.text.strip()
            ]
            cells = [cell for cell in cells if cell not in {"edit", "delete", "translate"}]
            if not cells or cells[0] == "No data to display!":
                continue
            records.append(dict(zip(data_headers, cells[: len(data_headers)])))

        return records

    def first_visible_record(self):
        records = self.visible_table_records()
        return records[0] if records else None

    def first_record_with_value_or_none(self, field):
        for record in self.visible_table_records():
            if record.get(field):
                return record
        return None

    def result_count(self):
        text = self.wait.until(ec.visibility_of_element_located(self.RESULTS_COUNT)).text
        match = re.search(r"\((\d+)\)", text)
        return int(match.group(1)) if match else None

    def visible_record_count(self):
        return len(self.visible_table_records())

    def row_action_icons_exist(self):
        rows = self.visible_table_rows()
        if not rows:
            return False
        row = rows[0]
        return (
            bool(row.find_elements(*self.ROW_EDIT_BUTTON))
            and bool(row.find_elements(*self.ROW_DELETE_BUTTON))
            and bool(row.find_elements(*self.ROW_TRANSLATE_BUTTON))
        )

    def set_category_filter(self, category):
        self.log_action(f"Set category filter: {category}")
        category_input = self.wait.until(ec.element_to_be_clickable(self.CATEGORY_FILTER))
        category_input.send_keys(Keys.CONTROL, "a")
        category_input.send_keys(Keys.BACKSPACE)
        category_input.send_keys(str(category))
        return self

    def click_search(self):
        self.log_action("Click Search")
        self.click_element(self.wait.until(ec.element_to_be_clickable(self.SEARCH_BUTTON)))
        self.wait_for_table_ready()
        return self

    def search_by_category(self, category):
        self.set_category_filter(category)
        return self.click_search()

    def clear_filters(self):
        self.log_action("Click Clear filters")
        self.click_element(self.wait.until(ec.element_to_be_clickable(self.CLEAR_FILTERS_BUTTON)))
        self.wait.until(lambda _: self.current_category_filter_value() == "")
        empty_message = next(
            (element for element in self.driver.find_elements(*self.EMPTY_TABLE_MESSAGE) if element.is_displayed()),
            None,
        )
        self.click_element(self.wait.until(ec.element_to_be_clickable(self.SEARCH_BUTTON)))
        if empty_message is not None:
            self.wait.until(lambda _: ec.staleness_of(empty_message)(self.driver) or bool(self.visible_table_records()))
        self.wait_for_table_ready()
        return self

    def current_category_filter_value(self):
        return self.driver.find_element(*self.CATEGORY_FILTER).get_attribute("value")

    def current_dropdown_text(self, locator):
        return re.sub(r"\s+", " ", self.driver.find_element(*locator).text).strip()

    def choose_dropdown_filter(self, locator, option_text):
        normalized = self.normalize(option_text)
        normalized_literal = self.xpath_literal(normalized)
        self.log_action(f"Choose dropdown option: {option_text}")
        self.click_element(self.wait.until(ec.element_to_be_clickable(locator)))
        option_locator = (
            By.XPATH,
            "//*[@role='option' and ("
            "translate(normalize-space(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz')="
            + normalized_literal
            + " or translate(@aria-label, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz')="
            + normalized_literal
            + ")]",
        )
        self.click_element(self.wait.until(ec.element_to_be_clickable(option_locator)))
        try:
            self.wait.until(ec.invisibility_of_element_located(self.DROPDOWN_PANEL))
        except TimeoutException:
            pass
        self.wait_for_table_ready()
        return self

    def choose_type_filter(self, notification_type):
        return self.choose_dropdown_filter(self.TYPE_FILTER, notification_type)

    def choose_theme_filter(self, theme):
        return self.choose_dropdown_filter(self.THEME_FILTER, theme)

    def choose_active_filter(self, active):
        normalized = self.normalize(active)
        truthy_values = {"true", "yes", "active", "enabled", "1"}
        falsy_values = {"false", "no", "inactive", "disabled", "0"}
        accepted_values = truthy_values if normalized in truthy_values else falsy_values

        self.log_action(f"Choose Active dropdown option: {active}")
        self.click_element(self.wait.until(ec.element_to_be_clickable(self.ACTIVE_FILTER)))
        options = self.wait.until(
            lambda _: [
                option
                for option in self.driver.find_elements(By.XPATH, "//*[@role='option']")
                if option.is_displayed()
            ]
        )

        for option in options:
            label = self.normalize(option.text or option.get_attribute("aria-label"))
            if label in accepted_values:
                self.click_element(option)
                self.wait_for_table_ready()
                return self

        available = [self.normalize(option.text or option.get_attribute("aria-label")) for option in options]
        raise AssertionError(f"No Active option matching {active!r}. Available options: {available}")

    def clear_dropdown_filter(self, locator):
        clear_icon = (
            By.XPATH,
            locator[1] + "//*[contains(@class, 'p-dropdown-clear-icon') or @data-pc-section='clearicon']",
        )
        self.log_action("Clear dropdown filter")
        self.click_element(self.wait.until(ec.element_to_be_clickable(clear_icon)))
        self.wait_for_table_ready()
        return self

    def records_match_field(self, field, value):
        expected = self.normalize(value)
        return all(self.normalize(record.get(field)) == expected for record in self.visible_table_records())

    def records_contain_category(self, category):
        expected = self.normalize(category)
        return all(expected in self.normalize(record.get("Category")) for record in self.visible_table_records())

    def records_match_all(self, expected_values):
        return all(
            self.normalize(record.get(field)) == self.normalize(value)
            for record in self.visible_table_records()
            for field, value in expected_values.items()
        )

    def open_column_visibility_dropdown(self):
        if self.is_column_visibility_dropdown_open():
            return self
        self.log_action("Open column visibility dropdown")
        self.click_element(self.wait.until(ec.element_to_be_clickable(self.COLUMN_TOGGLE)))
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
            self.click_element(self.wait.until(ec.element_to_be_clickable(self.COLUMN_TOGGLE)))
            self.wait.until(ec.invisibility_of_element_located(self.COLUMN_PANEL))
        return self

    def is_column_visibility_dropdown_open(self):
        return any(panel.is_displayed() for panel in self.driver.find_elements(*self.COLUMN_PANEL))

    def column_visibility_options(self):
        return [option for option in self.driver.find_elements(*self.COLUMN_OPTIONS) if option.is_displayed()]

    def column_visibility_option_labels(self):
        try:
            return [option.get_attribute("aria-label") or option.text.strip() for option in self.column_visibility_options()]
        except StaleElementReferenceException:
            return [option.get_attribute("aria-label") or option.text.strip() for option in self.column_visibility_options()]

    def is_column_option_selected(self, option):
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
            self.wait.until(lambda _: self.driver.find_element(*option_locator).get_attribute("aria-checked") == str(visible).lower())
        return self

    def export_notifications(self):
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

    def open_add_form(self):
        self.log_action("Click Add")
        self.click_element(self.wait.until(ec.element_to_be_clickable(self.ADD_BUTTON)))
        self.wait.until(ec.visibility_of_element_located(self.POPUP))
        return self

    def open_first_row_edit_form(self):
        self.log_action("Click row Edit")
        row = self.wait.until(lambda _: self.visible_table_rows()[0] if self.visible_table_rows() else False)
        edit_button = row.find_element(*self.ROW_EDIT_BUTTON)
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", edit_button)
        self.click_element(edit_button)
        self.wait.until(ec.visibility_of_element_located(self.POPUP))
        return self

    def open_first_row_translate_form(self):
        self.log_action("Click row Translate")
        row = self.wait.until(lambda _: self.visible_table_rows()[0] if self.visible_table_rows() else False)
        translate_button = row.find_element(*self.ROW_TRANSLATE_BUTTON)
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", translate_button)
        self.click_element(translate_button)
        self.wait.until(ec.visibility_of_element_located(self.POPUP))
        return self

    def open_first_row_delete_confirmation(self):
        self.log_action("Click row Delete")
        row = self.wait.until(lambda _: self.visible_table_rows()[0] if self.visible_table_rows() else False)
        delete_button = row.find_element(*self.ROW_DELETE_BUTTON)
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", delete_button)
        self.click_element(delete_button)
        self.wait.until(ec.visibility_of_element_located(self.CONFIRM_DIALOG))
        return self

    def is_popup_open(self):
        return self.has_visible_element(self.POPUP)

    def is_delete_confirmation_open(self):
        return self.has_visible_element(self.CONFIRM_DIALOG)

    def close_popup(self):
        if self.has_visible_element(self.POPUP_CANCEL):
            self.click_element(self.wait.until(ec.element_to_be_clickable(self.POPUP_CANCEL)))
            try:
                self.wait.until(ec.invisibility_of_element_located(self.POPUP))
            except TimeoutException:
                pass
        elif self.is_popup_open():
            ActionChains(self.driver).send_keys(Keys.ESCAPE).perform()
            try:
                self.wait.until(ec.invisibility_of_element_located(self.POPUP))
            except TimeoutException:
                pass
        return self

    def cancel_delete_confirmation(self):
        if self.has_visible_element(self.CONFIRM_CANCEL):
            self.click_element(self.wait.until(ec.element_to_be_clickable(self.CONFIRM_CANCEL)))
            self.wait.until(ec.invisibility_of_element_located(self.CONFIRM_DIALOG))
        return self

    def click_sort_header(self, header_text):
        header_literal = self.xpath_literal(header_text)
        header_locator = (
            By.XPATH,
            self.PAGE_ROOT + "//table//thead//th[.//span[normalize-space()=" + header_literal + "] or normalize-space()=" + header_literal + "]",
        )
        self.log_action(f"Click sort header: {header_text}")
        self.click_element(self.wait.until(ec.element_to_be_clickable(header_locator)))
        self.wait_for_table_ready()
        return self

    def can_use_pagination(self):
        return self.has_visible_element(self.ROWS_PER_PAGE)

    @staticmethod
    def xpath_literal(value):
        value = str(value)
        if "'" not in value:
            return f"'{value}'"
        if '"' not in value:
            return f'"{value}"'
        parts = value.split("'")
        return "concat(" + ', "\'", '.join(f"'{part}'" for part in parts) + ")"

    @staticmethod
    def normalize(value):
        return str(value or "").strip().lower()
