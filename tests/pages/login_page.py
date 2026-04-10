from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec


class LoginPage:
    # Flexible login selectors are useful while the UI is still changing.
    USERNAME = (
        By.XPATH,
        "//input[@name='username' or @id='username' or @autocomplete='username' or @type='text']",
    )
    PASSWORD = (By.XPATH, "//input[@name='password' or @id='password' or @type='password']")
    LOGIN_BUTTON = (
        By.XPATH,
        "//button[@type='submit' or normalize-space()='Login' or normalize-space()='Sign in']",
    )

    def __init__(self, driver, wait, base_url: str):
        self.driver = driver
        self.wait = wait
        self.base_url = base_url.rstrip("/")

    def open(self):
        # Open the login page directly and wait for the form to become usable.
        self.driver.get(f"{self.base_url}/login/")
        self.wait.until(ec.visibility_of_element_located(self.USERNAME))
        self.wait.until(ec.visibility_of_element_located(self.PASSWORD))

    def login(self, username: str, password: str):
        # Fill the login form and submit it.
        user_input = self.driver.find_element(*self.USERNAME)
        password_input = self.driver.find_element(*self.PASSWORD)
        user_input.clear()
        user_input.send_keys(username)
        password_input.clear()
        password_input.send_keys(password)
        self.driver.find_element(*self.LOGIN_BUTTON).click()
