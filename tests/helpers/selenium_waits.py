from selenium.webdriver.support import expected_conditions as ec


LOADING_INDICATORS = (
    "[aria-busy='true'], "
    ".p-progress-spinner, .p-progressbar-indeterminate, "
    ".ngx-spinner-overlay, mat-progress-spinner, mat-spinner"
)


def wait_for_ui_idle(driver, wait):
    """Wait until the browser and observable application loading state are idle."""
    wait.until(lambda current_driver: current_driver.execute_script("return document.readyState") == "complete")
    wait.until(ec.invisibility_of_element_located(("css selector", LOADING_INDICATORS)))
