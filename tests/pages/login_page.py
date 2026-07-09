from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait


UPPERCASE = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
LOWERCASE = "abcdefghijklmnopqrstuvwxyz"


class LoginPage:
    # Flexible login selectors are useful because each env can expose a slightly different login shell.
    USERNAME = (
        By.XPATH,
        "("
        f"//input[not(@type='hidden') and not(@type='password') and ("
        f"contains(translate(@placeholder, '{UPPERCASE}', '{LOWERCASE}'), 'user') or "
        f"contains(translate(@name, '{UPPERCASE}', '{LOWERCASE}'), 'user') or "
        f"contains(translate(@id, '{UPPERCASE}', '{LOWERCASE}'), 'user') or "
        f"contains(translate(@autocomplete, '{UPPERCASE}', '{LOWERCASE}'), 'user') or "
        f"contains(translate(@formcontrolname, '{UPPERCASE}', '{LOWERCASE}'), 'user') or "
        f"contains(translate(@ng-reflect-name, '{UPPERCASE}', '{LOWERCASE}'), 'user') or "
        f"ancestor::*[contains(translate(@ng-reflect-label, '{UPPERCASE}', '{LOWERCASE}'), 'user')]"
        ")] | (//form//input[not(@type='hidden') and not(@type='password')])[1]"
        ")[1]",
    )
    PASSWORD = (
        By.XPATH,
        "("
        f"//input[not(@type='hidden') and (@type='password' or "
        f"contains(translate(@placeholder, '{UPPERCASE}', '{LOWERCASE}'), 'pass') or "
        f"contains(translate(@name, '{UPPERCASE}', '{LOWERCASE}'), 'pass') or "
        f"contains(translate(@id, '{UPPERCASE}', '{LOWERCASE}'), 'pass') or "
        f"contains(translate(@autocomplete, '{UPPERCASE}', '{LOWERCASE}'), 'pass') or "
        f"contains(translate(@formcontrolname, '{UPPERCASE}', '{LOWERCASE}'), 'pass') or "
        f"contains(translate(@ng-reflect-name, '{UPPERCASE}', '{LOWERCASE}'), 'pass') or "
        f"ancestor::*[contains(translate(@ng-reflect-label, '{UPPERCASE}', '{LOWERCASE}'), 'pass')]"
        ")] | (//form//input[@type='password'])[1]"
        ")[1]",
    )
    LOGIN_BUTTON = (
        By.XPATH,
        "//button[@type='submit' or "
        f"contains(translate(normalize-space(.), '{UPPERCASE}', '{LOWERCASE}'), 'login') or "
        f"contains(translate(normalize-space(.), '{UPPERCASE}', '{LOWERCASE}'), 'log in') or "
        f"contains(translate(normalize-space(.), '{UPPERCASE}', '{LOWERCASE}'), 'sign in') or "
        f"contains(translate(normalize-space(.), '{UPPERCASE}', '{LOWERCASE}'), 'continue')]",
    )
    APP_SHELL = (
        By.XPATH,
        "//cc-header | //cc-sidebar | //cc-dashboard | //app-root//*[not(self::cc-login-page)]",
    )

    def __init__(self, driver, wait, base_url: str):
        self.driver = driver
        self.wait = wait
        self.base_url = base_url.rstrip("/")

    def open(self):
        # Different envs either serve login from the base URL or from /login.
        candidate_urls = (
            self.base_url,
            f"{self.base_url}/login",
            f"{self.base_url}/login/",
        )
        last_error = None

        for url in candidate_urls:
            self.driver.get(url)
            try:
                short_wait = WebDriverWait(self.driver, 5)
                short_wait.until(ec.visibility_of_element_located(self.USERNAME))
                short_wait.until(ec.visibility_of_element_located(self.PASSWORD))
                return
            except TimeoutException as error:
                last_error = error

        self.driver.save_screenshot("tests/downloads/debug_login_page.png")
        with open("tests/downloads/debug_login_page.html", "w", encoding="utf-8") as debug_file:
            debug_file.write(self.driver.page_source)
        raise last_error or TimeoutException("Login form was not found.")

    def login(self, username: str, password: str):
        # Fill the login form and wait until the post-login UI is actually rendered.
        user_input = self.wait.until(ec.element_to_be_clickable(self.USERNAME))
        password_input = self.wait.until(ec.element_to_be_clickable(self.PASSWORD))

        user_input.send_keys(Keys.CONTROL, "a")
        user_input.send_keys(Keys.BACKSPACE)
        user_input.send_keys(username)

        password_input.send_keys(Keys.CONTROL, "a")
        password_input.send_keys(Keys.BACKSPACE)
        password_input.send_keys(password)

        self.wait.until(ec.element_to_be_clickable(self.LOGIN_BUTTON)).click()
        self.wait_until_logged_in()

    def wait_until_logged_in(self):
        self.wait.until(lambda driver: driver.execute_script("return document.readyState") == "complete")
        self.wait.until(lambda driver: not self._has_visible_element(self.USERNAME))
        self.wait.until(lambda driver: self._has_visible_element(self.APP_SHELL))

    def _has_visible_element(self, locator):
        try:
            return any(element.is_displayed() for element in self.driver.find_elements(*locator))
        except StaleElementReferenceException:
            return False