import re

from selenium.common.exceptions import ElementClickInterceptedException, StaleElementReferenceException, TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as ec

from tests.helpers.selenium_waits import wait_for_ui_idle


class SpecialNumbersPage:
    TABLE_DATA_HEADERS = ["Number", "Description", "Created By", "Creation Date", "Start Date", "End Date", "Number Type"]

    PAGE_ROOT = (
        "(//cc-special-numbers"
        " | //*[self::cc-main-page or self::cc-main or contains(@class, 'pageContainer')]"
        "[.//h1[normalize-space()='Special numbers']])[last()]"
    )
    LABEL_LOWER = "translate(normalize-space(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz')"
    ARIA_LOWER = "translate(@aria-label, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz')"

    HEADER = (By.XPATH, PAGE_ROOT + "//h1[normalize-space()='Special numbers']")
    TYPE_FILTER = (
        By.XPATH,
        PAGE_ROOT
        + "//cc-dropdown-control[.//label[contains("
        + LABEL_LOWER
        + ", 'type')]]//*[@role='combobox' or contains(@class, 'p-dropdown')][1]",
    )
    NUMBER_FILTER = (
        By.XPATH,
        PAGE_ROOT + "//cc-text-control[.//label[contains(" + LABEL_LOWER + ", 'number')]]//input",
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
    ROW_EDIT_BUTTON = (By.XPATH, ".//button[.//i[normalize-space()='edit'] or contains(@aria-label, 'Edit')]")
    ROW_DELETE_BUTTON = (By.XPATH, ".//button[.//i[normalize-space()='delete'] or contains(@aria-label, 'Delete')]")
    COLUMN_TOGGLE = (
        By.XPATH,
        PAGE_ROOT
        + "//p-multiselect//*[@role='combobox' or contains(@class, 'p-multiselect-trigger') or contains(@class, 'p-multiselect-label')][1]",
    )
    COLUMN_PANEL = (By.XPATH, "//div[contains(@class, 'p-multiselect-panel')]")
    COLUMN_OPTIONS = (By.XPATH, "//div[contains(@class, 'p-multiselect-panel')]//li[@role='option']")
    DROPDOWN_PANEL = (By.XPATH, "//div[contains(@class, 'p-dropdown-panel')]")
    DROPDOWN_OPTIONS = (By.XPATH, "//*[@role='option']")
    ADD_BUTTON = (
        By.XPATH,
        PAGE_ROOT
        + "//cc-dynamic-actions//button[.//span[normalize-space()='Add'] or .//i[normalize-space()='add'] or contains("
        + ARIA_LOWER
        + ", 'add')]",
    )
    PUBLISH_BUTTON = (
        By.XPATH,
        PAGE_ROOT
        + "//cc-dynamic-actions//button[.//span[normalize-space()='Publish'] or .//i[normalize-space()='publish'] or contains("
        + ARIA_LOWER
        + ", 'publish')]",
    )

    def __init__(self, driver, wait):
        self.driver = driver
        self.wait = wait

    def wait_for_ui_idle(self):
        wait_for_ui_idle(self.driver, self.wait)
        return self

    def log_action(self, message):
        print(f"[Special Numbers] {message}", flush=True)

    def wait_until_loaded(self):
        self.log_action("Wait until Special Numbers page is loaded")
        self.wait.until(ec.visibility_of_element_located(self.HEADER))
        self.wait.until(ec.visibility_of_element_located(self.TABLE))
        return self

    def has_visible_element(self, locator):
        return any(element.is_displayed() for element in self.driver.find_elements(*locator))

    def is_loaded(self):
        return self.has_visible_element(self.HEADER) and self.has_visible_element(self.TABLE)

    def has_main_controls(self):
        locators = [
            self.HEADER,
            self.TYPE_FILTER,
            self.NUMBER_FILTER,
            self.SEARCH_BUTTON,
            self.CLEAR_FILTERS_BUTTON,
            self.RESULTS_COUNT,
            self.COLUMN_TOGGLE,
            self.TABLE,
            self.ADD_BUTTON,
            self.PUBLISH_BUTTON,
        ]
        return all(self.has_visible_element(locator) for locator in locators)

    def click_element(self, element):
        try:
            element.click()
        except ElementClickInterceptedException:
            self.driver.execute_script("arguments[0].click();", element)
        return self

    def visible_table_rows(self):
        return [row for row in self.driver.find_elements(*self.TABLE_ROWS) if row.is_displayed()]

    def visible_table_headers(self):
        return [
            header.text.strip()
            for header in self.driver.find_elements(*self.TABLE_HEADERS)
            if header.is_displayed() and header.text.strip()
        ]

    def visible_table_records(self):
        headers = [header for header in self.visible_table_headers() if header in self.TABLE_DATA_HEADERS]
        records = []
        for row in self.visible_table_rows():
            cells = [
                cell.text.strip()
                for cell in row.find_elements(By.XPATH, "./td")
                if cell.is_displayed() and cell.text.strip() and cell.text.strip() not in {"edit", "delete"}
            ]
            if not cells or cells[0] == "No data to display!":
                continue
            data_headers = headers or self.TABLE_DATA_HEADERS
            records.append(dict(zip(data_headers, cells[: len(data_headers)])))
        return records

    def first_visible_record(self):
        records = self.visible_table_records()
        return records[0] if records else None

    def row_action_icons_exist(self):
        rows = self.visible_table_rows()
        if not rows:
            return False
        return bool(rows[0].find_elements(*self.ROW_EDIT_BUTTON)) and bool(rows[0].find_elements(*self.ROW_DELETE_BUTTON))

    def choose_type_filter(self, number_type):
        self.log_action(f"Choose type filter: {number_type}")
        self.click_element(self.wait.until(ec.element_to_be_clickable(self.TYPE_FILTER)))
        self.choose_open_dropdown_option(number_type)
        return self

    def search_by_number(self, number):
        self.log_action(f"Search by number: {number}")
        number_input = self.wait.until(ec.element_to_be_clickable(self.NUMBER_FILTER))
        number_input.send_keys(Keys.CONTROL, "a")
        number_input.send_keys(Keys.BACKSPACE)
        number_input.send_keys(str(number))
        return self.click_search()

    def click_search(self):
        self.log_action("Click Search")
        self.click_element(self.wait.until(ec.element_to_be_clickable(self.SEARCH_BUTTON)))
        self.wait_for_table_ready()
        return self

    def clear_filters(self):
        self.log_action("Click Clear filters")
        self.click_element(self.wait.until(ec.element_to_be_clickable(self.CLEAR_FILTERS_BUTTON)))
        self.wait_for_table_ready()
        return self

    def wait_for_table_ready(self):
        self.wait.until(ec.visibility_of_element_located(self.TABLE))
        return self

    def choose_open_dropdown_option(self, option_text):
        normalized = self.normalize_type(option_text)
        aliases = {
            "white": ["white", "white list", "whitelist"],
            "black": ["black", "black list", "blacklist"],
        }
        option_values = aliases.get(normalized, [normalized])
        xpath_conditions = [
            "translate(normalize-space(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz')="
            + self.xpath_literal(value)
            + " or translate(@aria-label, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz')="
            + self.xpath_literal(value)
            for value in option_values
        ]
        option_locator = (By.XPATH, "//*[@role='option'][" + " or ".join(xpath_conditions) + "]")
        self.log_action(f"Choose dropdown option: {option_text}")
        self.click_element(self.wait.until(ec.element_to_be_clickable(option_locator)))
        self.wait.until(ec.invisibility_of_element_located(self.DROPDOWN_PANEL))
        return self

    def current_type_filter_text(self):
        label = self.driver.find_element(*self.TYPE_FILTER).text.strip()
        return label

    def filter_by_type_and_search(self, number_type):
        self.choose_type_filter(number_type)
        self.click_search()
        return self

    def records_match_type(self, number_type):
        expected = self.normalize_type(number_type)
        return all(self.normalize_type(record.get("Number Type")) == expected for record in self.visible_table_records())

    def records_match_number(self, number):
        number = str(number)
        return all(record.get("Number") == number for record in self.visible_table_records())

    def result_count(self):
        text = self.wait.until(ec.visibility_of_element_located(self.RESULTS_COUNT)).text
        match = re.search(r"\((\d+)\)", text)
        return int(match.group(1)) if match else None

    def visible_record_count(self):
        return len(self.visible_table_records())

    def visible_table_column_count(self):
        return len(self.visible_table_headers())

    def open_column_visibility_dropdown(self):
        if self.is_column_visibility_dropdown_open():
            return self
        self.log_action("Open column visibility dropdown")
        self.click_element(self.wait.until(ec.element_to_be_clickable(self.COLUMN_TOGGLE)))
        self.wait.until(ec.visibility_of_element_located(self.COLUMN_PANEL))
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
    def normalize_type(value):
        value = str(value or "").strip().lower()
        if "white" in value:
            return "white"
        if "black" in value:
            return "black"
        return value
