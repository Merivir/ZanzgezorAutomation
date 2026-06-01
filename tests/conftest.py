import os
from datetime import datetime
from pathlib import Path

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support.ui import WebDriverWait

from tests.config.automation_config import load_config


LOG_FILE = Path(__file__).parent / "logs" / "test_run.log"
DEFAULT_CHROME_BINARY_PATHS = (
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
)
CACHED_CHROMEDRIVER_DIR = Path.home() / ".cache" / "selenium" / "chromedriver" / "win64"


def _write_log(message):
    with LOG_FILE.open("a", encoding="utf-8") as log_file:
        log_file.write(message + "\n")


def _testlink_details(item):
    marker = item.get_closest_marker("testlink")
    if not marker:
        return "N/A", "No TestLink title"

    testlink_id = marker.args[0] if len(marker.args) > 0 else "N/A"
    title = marker.args[1] if len(marker.args) > 1 else "No TestLink title"
    return testlink_id, title


def _skip_reason(report):
    if isinstance(report.longrepr, tuple) and len(report.longrepr) >= 3:
        return str(report.longrepr[2]).replace("Skipped: ", "")

    return str(report.longrepr).replace("Skipped: ", "")


def pytest_configure(config):
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    LOG_FILE.write_text("", encoding="utf-8")
    config.test_run_results = []

    started_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    args = " ".join(str(arg) for arg in config.invocation_params.args)

    _write_log("TEST RUN STARTED")
    _write_log(f"Started at: {started_at}")
    _write_log(f"Command: pytest {args}".strip())
    _write_log("")


def pytest_runtest_setup(item):
    testlink_id, title = _testlink_details(item)
    _write_log(f"RUNNING: {item.nodeid}")
    _write_log(f"TestLink: {testlink_id}")
    _write_log(f"Title: {title}")


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()

    should_log = report.when == "call" or report.failed or report.skipped
    if not should_log:
        return

    testlink_id, title = _testlink_details(item)
    status = report.outcome.upper()
    duration = f"{report.duration:.2f}s"

    item.config.test_run_results.append(status)

    _write_log(f"RESULT: {status} ({report.when}, {duration})")
    _write_log(f"Test: {item.nodeid}")
    _write_log(f"TestLink: {testlink_id}")
    _write_log(f"Title: {title}")

    if report.failed:
        _write_log("Failure reason:")
        _write_log(report.longreprtext)
    elif report.skipped:
        _write_log(f"Skip reason: {_skip_reason(report)}")

    _write_log("-" * 100)
    _write_log("")


def pytest_terminal_summary(terminalreporter, exitstatus, config):
    results = config.test_run_results
    passed = results.count("PASSED")
    failed = results.count("FAILED")
    skipped = results.count("SKIPPED")

    _write_log("TEST RUN FINISHED")
    _write_log(f"Finished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    _write_log(f"Passed: {passed}")
    _write_log(f"Failed: {failed}")
    _write_log(f"Skipped: {skipped}")
    _write_log(f"Exit status: {exitstatus}")
    terminalreporter.write_line(f"Detailed test log: {LOG_FILE}")


def _config_value(run_config, env_name, config_name):
    return os.getenv(env_name) or run_config.get(config_name) or ""


def _is_enabled(value):
    if isinstance(value, bool):
        return value

    return str(value).strip().lower() in {"1", "true", "yes", "y", "on"}


def _default_chrome_binary_path():
    local_appdata = os.getenv("LOCALAPPDATA")
    paths = list(DEFAULT_CHROME_BINARY_PATHS)

    if local_appdata:
        paths.append(str(Path(local_appdata) / "Google" / "Chrome" / "Application" / "chrome.exe"))

    for path in paths:
        if Path(path).is_file():
            return path

    return ""


def _version_parts(path):
    version = path.parent.name
    return tuple(int(part) for part in version.split(".") if part.isdigit())


def _cached_chromedriver_path():
    if not CACHED_CHROMEDRIVER_DIR.exists():
        return ""

    drivers = sorted(
        CACHED_CHROMEDRIVER_DIR.glob("*/chromedriver.exe"),
        key=_version_parts,
        reverse=True,
    )
    return str(drivers[0]) if drivers else ""


def _build_chrome_options(run_config):
    options = ChromeOptions()

    chrome_binary_path = _config_value(run_config, "CHROME_BINARY_PATH", "chrome_binary_path")
    chrome_binary_path = chrome_binary_path or _default_chrome_binary_path()
    if chrome_binary_path:
        options.binary_location = chrome_binary_path

    headless = os.getenv("HEADLESS")
    if headless is None:
        headless = run_config.get("headless", False)

    if _is_enabled(headless):
        options.add_argument("--headless=new")
        options.add_argument("--window-size=1920,1080")

    return options


@pytest.fixture(scope="module")
def driver():
    run_config = load_config().get("run", {})
    options = _build_chrome_options(run_config)
    selenium_remote_url = _config_value(run_config, "SELENIUM_REMOTE_URL", "selenium_remote_url")

    if selenium_remote_url:
        driver = webdriver.Remote(command_executor=selenium_remote_url, options=options)
    else:
        chromedriver_path = _config_value(run_config, "CHROMEDRIVER_PATH", "chromedriver_path")
        chromedriver_path = chromedriver_path or _cached_chromedriver_path()
        service = ChromeService(executable_path=chromedriver_path) if chromedriver_path else None
        driver = webdriver.Chrome(service=service, options=options)

    driver.maximize_window()
    yield driver
    driver.quit()


@pytest.fixture(scope="module")
def wait(driver):
    return WebDriverWait(driver, 10)
