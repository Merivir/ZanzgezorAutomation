import json
import os
from pathlib import Path

import pytest
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait

from tests.config.modules import get_effective_module_flags


def _env(name: str, default: str = "") -> str:
    return os.getenv(name, default).strip()


def _truthy(value: str) -> bool:
    return value.lower() in {"1", "true", "yes", "on"}


@pytest.fixture(scope="session")
def test_config() -> dict:
    config_path = Path(_env("TEST_CONFIG_PATH", "config/test_config.json"))
    if not config_path.exists():
        raise pytest.UsageError(
            f"Config file '{config_path}' was not found. Create it from config/test_config.example.json."
        )

    with config_path.open("r", encoding="utf-8") as file:
        raw_config = json.load(file)

    clients = raw_config.get("clients", {})
    active_client = _env("TEST_CLIENT", raw_config.get("active_client", ""))
    if not active_client:
        raise pytest.UsageError("No active client is configured.")
    if active_client not in clients:
        raise pytest.UsageError(f"Client '{active_client}' was not found in '{config_path}'.")

    return {
        "active_client": active_client,
        "client": clients[active_client],
        "raw": raw_config,
    }


@pytest.fixture(scope="session")
def base_url(test_config) -> str:
    return test_config["client"].get("base_url", "").rstrip("/")


@pytest.fixture(scope="session")
def credentials(test_config) -> dict:
    return test_config["client"].get("users", {})


@pytest.fixture(scope="session")
def module_flags(test_config) -> dict:
    raw_flags = test_config["client"].get("modules", {})
    only_modules = _env("TEST_MODULES")
    skip_modules = _env("SKIP_MODULES")
    return get_effective_module_flags(raw_flags, only_modules, skip_modules)


@pytest.fixture
def driver(test_config):
    options = Options()
    run_cfg = test_config["raw"].get("run", {})

    if _truthy(_env("HEADLESS", str(run_cfg.get("headless", True)).lower())):
        options.add_argument("--headless=new")

    options.add_argument("--window-size=1440,900")
    options.add_argument("--disable-notifications")

    browser_binary = _env("CHROME_BINARY_PATH", str(run_cfg.get("chrome_binary_path", "")))
    if browser_binary:
        browser_path = Path(browser_binary)
        if not browser_path.exists():
            raise pytest.UsageError(f"Chrome binary was not found at '{browser_path}'.")
        options.binary_location = str(browser_path)

    remote_url = _env("SELENIUM_REMOTE_URL", str(run_cfg.get("selenium_remote_url", "")))
    try:
        if remote_url:
            drv = webdriver.Remote(command_executor=remote_url, options=options)
        else:
            driver_path = _env("CHROMEDRIVER_PATH", str(run_cfg.get("chromedriver_path", "")))
            if driver_path:
                driver_bin = Path(driver_path)
                if not driver_bin.exists():
                    raise pytest.UsageError(f"ChromeDriver was not found at '{driver_bin}'.")
                drv = webdriver.Chrome(service=Service(str(driver_bin)), options=options)
            else:
                drv = webdriver.Chrome(options=options)
    except WebDriverException as err:
        raise pytest.UsageError(
            "Unable to start Chrome WebDriver. Configure CHROMEDRIVER_PATH, "
            "SELENIUM_REMOTE_URL, or allow Selenium Manager to resolve it."
        ) from err

    drv.implicitly_wait(2)
    yield drv
    drv.quit()


@pytest.fixture
def wait(driver):
    return WebDriverWait(driver, 15)
