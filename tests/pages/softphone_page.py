from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

from tests.helpers.selenium_waits import wait_for_ui_idle


class SoftphonePage:
    ONLINE_EXTENSION_OPTION = (
        By.XPATH,
        "//div[contains(@class, 'p-dropdown-panel')]"
        "//div[contains(@class, 'extensions-items')]//div[contains(normalize-space(), %s) "
        "and contains(translate(normalize-space(), 'abcdefghijklmnopqrstuvwxyz', 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'), 'ONLINE')]",
    )
    EXTENSION_OPTION = (
        By.XPATH,
        "//div[contains(@class, 'p-dropdown-panel')]"
        "//div[contains(@class, 'extensions-items')]//div[contains(normalize-space(), %s)]",
    )
    EXTENSION_OPTIONS = (
        By.XPATH,
        "//div[contains(@class, 'p-dropdown-panel')]//div[contains(@class, 'extensions-items')]//div",
    )
    DROPDOWN_TRIGGERS = (
        By.XPATH,
        "//*[@role='button' and @aria-haspopup='listbox' and contains(@class, 'p-dropdown-trigger')]",
    )
    OPEN_DROPDOWN_PANEL = (By.XPATH, "//div[contains(@class, 'p-dropdown-panel') and not(contains(@style, 'display: none'))]")
    NUMBER_INPUT = (
        By.XPATH,
        "//input[@placeholder='Type or paste a number' or contains(@placeholder, 'number')]",
    )
    CALL_BUTTON = (
        By.XPATH,
        "//button[not(@disabled) and (.//span[contains(@class, 'callButton') and contains(normalize-space(), 'Call')]"
        " or .//i[normalize-space()='phone'])]",
    )

    def __init__(self, driver, wait=None):
        self.driver = driver
        self.wait = wait or WebDriverWait(driver, 60)

    def switch_to_call_tab(self):
        current_handle = self.driver.current_window_handle
        handles = list(self.driver.window_handles)

        for handle in handles:
            self.driver.switch_to.window(handle)
            if "/admin-ui" not in self.driver.current_url and self._has_softphone_shell():
                return self

        for handle in handles:
            self.driver.switch_to.window(handle)
            if "/admin-ui" not in self.driver.current_url:
                return self.wait_until_loaded()

        self.driver.switch_to.window(current_handle)
        origin = self.driver.execute_script("return window.location.origin")
        self.driver.get(f"{origin}/")
        return self.wait_until_loaded()

    def wait_until_loaded(self):
        self.wait.until(ec.presence_of_element_located(self.NUMBER_INPUT))
        return self

    def select_online_extension(self, extension_number):
        option_locator = (
            self.ONLINE_EXTENSION_OPTION[0],
            self.ONLINE_EXTENSION_OPTION[1] % self.xpath_literal(extension_number),
        )

        self.wait_until_loaded()
        self.wait.until(
            lambda _: self._click_trigger_that_contains_option(option_locator),
            f"Extension '{extension_number}' did not appear ONLINE in the softphone dropdown. "
            f"Visible options: {self.visible_extension_options()}",
        )
        return self

    def visible_extension_options(self):
        options = []
        for trigger in self._visible_dropdown_triggers():
            try:
                trigger.click()
                WebDriverWait(self.driver, 3).until(ec.presence_of_element_located(self.OPEN_DROPDOWN_PANEL))
                options = [
                    option.text.strip()
                    for option in self.driver.find_elements(*self.EXTENSION_OPTIONS)
                    if option.is_displayed() and option.text.strip()
                ]
                self._close_open_dropdown()
                if options:
                    return options
            except (StaleElementReferenceException, TimeoutException):
                self._close_open_dropdown()

        return options

    def call_number(self, number):
        input_element = self.wait.until(ec.element_to_be_clickable(self.NUMBER_INPUT))
        input_element.send_keys(Keys.CONTROL, "a")
        input_element.send_keys(str(number))
        self._wait_briefly_for_idle()

        call_button = self.wait.until(ec.element_to_be_clickable(self.CALL_BUTTON))
        call_button.click()
        self._wait_briefly_for_idle()
        return self

    def _has_softphone_shell(self):
        try:
            return bool(self.driver.find_elements(*self.NUMBER_INPUT))
        except StaleElementReferenceException:
            return False

    def _click_trigger_that_contains_option(self, option_locator):
        for trigger in self._visible_dropdown_triggers():
            try:
                trigger.click()
                option = WebDriverWait(self.driver, 3).until(ec.element_to_be_clickable(option_locator))
                option.click()
                self.wait.until(ec.invisibility_of_element_located(self.OPEN_DROPDOWN_PANEL))
                return True
            except (StaleElementReferenceException, TimeoutException):
                self._close_open_dropdown()

        return False

    def _visible_dropdown_triggers(self):
        triggers = []
        for trigger in self.driver.find_elements(*self.DROPDOWN_TRIGGERS):
            try:
                if trigger.is_displayed() and trigger.is_enabled():
                    triggers.append(trigger)
            except StaleElementReferenceException:
                continue
        return triggers

    def _close_open_dropdown(self):
        self.driver.switch_to.active_element.send_keys(Keys.ESCAPE)

    def _wait_briefly_for_idle(self):
        try:
            wait_for_ui_idle(self.driver, WebDriverWait(self.driver, 5))
        except TimeoutException:
            pass

    @staticmethod
    def xpath_literal(value):
        value = str(value)
        if "'" not in value:
            return f"'{value}'"
        if '"' not in value:
            return f'"{value}"'
        parts = value.split("'")
        return "concat(" + ', "\'", '.join(f"'{part}'" for part in parts) + ")"
