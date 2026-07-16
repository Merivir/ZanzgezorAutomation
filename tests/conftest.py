import os
import re
import shutil
import tempfile
import time
from datetime import datetime
from pathlib import Path

import pytest
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

from tests.config.automation_config import get_active_client, get_client_config, get_extensions_config, load_config
from tests.helpers.log_colors import cyan_text, green_text, red_text, yellow_text
from tests.helpers.softphones.factory import create_softphone_client


LOG_FILE = Path(__file__).parent / "logs" / "test_run.log"
DOWNLOAD_DIR = Path(__file__).parent / "downloads"
FAILURE_DIR = DOWNLOAD_DIR / "failures"
DEFAULT_CHROME_BINARY_PATHS = (
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
)

SUITE_MARKERS = {
    "focused": "not destructive and not integration and not requires_microsip and not not_automated and not extended",
    "smoke": "smoke and not destructive and not integration and not requires_microsip",
    "all": "",
    "extended": "extended and not destructive",
    "destructive": "destructive and not requires_microsip",
    "integration": "integration",
    "microsip": "requires_microsip",
}
SECTION_MARKERS = ("extensions", "notifications", "special_numbers")


def _write_log(message):
    print(message, flush=True)


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



def _safe_filename(value):
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", value).strip("_")[:180]


def _clean_failure_line(line):
    line = re.sub(r"^E\s+", "", line.strip())
    line = line.replace("tests.helpers.exceptions.", "")
    step_match = re.search(r"TestStepError: Step failed: (.*)\. ([A-Za-z_][\w.]*): (.*)", line)
    if step_match:
        return f"{step_match.group(2)}: {step_match.group(3)}"
    return line


def _redact_sensitive_text(text):
    text = re.sub(
        r"(?i)(password\s*[=:]\s*)(['\"]?)[^,'\";|}\]]+\2",
        r"\1<hidden>",
        str(text),
    )
    text = re.sub(
        r"(?i)(Password(?: value)?(?: was not updated.*?Expected )?)(['\"])[^'\"]+\2",
        r"\1'<hidden>'",
        text,
    )
    return text
def _short_failure_text(report):
    text = str(report.longreprtext or report.longrepr or "").strip()
    if not text:
        return "No failure details were reported."

    lines = [line.strip() for line in text.splitlines() if line.strip()]
    exception_lines = []
    for line in lines:
        clean_line = _clean_failure_line(line)
        if re.match(r"^(selenium\.common\.exceptions\.)?[A-Za-z_][\w.]*(?:Error|Exception|TimeoutException):", clean_line):
            exception_lines.append(clean_line)

    for line in exception_lines:
        if not line.startswith("TestStepError:"):
            return _redact_sensitive_text(line)[:240]

    if exception_lines:
        return _redact_sensitive_text(exception_lines[0])[:240]

    crash = getattr(getattr(report, "longrepr", None), "reprcrash", None)
    if crash and getattr(crash, "message", None):
        return _redact_sensitive_text(_clean_failure_line(crash.message))[:240]

    return _redact_sensitive_text(_clean_failure_line(lines[-1]))[:240]


def _driver_from_item(item):
    for fixture_name in (
        "driver",
        "opened_extensions_page",
        "opened_notifications_page",
        "opened_special_numbers_page",
    ):
        value = item.funcargs.get(fixture_name)
        if value is None:
            continue
        return getattr(value, "driver", value)
    return None


def _save_failure_artifacts(item):
    driver = _driver_from_item(item)
    if driver is None:
        return []

    artifact_dir = FAILURE_DIR
    artifact_dir.mkdir(parents=True, exist_ok=True)
    name = _safe_filename(item.nodeid)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base = artifact_dir / f"{timestamp}_{name}"
    artifacts = []

    try:
        _write_log(f"Browser URL: {driver.current_url}")
        _write_log(f"Browser title: {driver.title}")
    except Exception as error:
        _write_log(f"Browser state unavailable: {error}")

    try:
        screenshot_path = base.with_suffix(".png")
        driver.save_screenshot(str(screenshot_path))
        artifacts.append(screenshot_path)
    except Exception as error:
        _write_log(f"Screenshot unavailable: {error}")

    try:
        html_path = base.with_suffix(".html")
        html_path.write_text(driver.page_source, encoding="utf-8")
        artifacts.append(html_path)
    except Exception as error:
        _write_log(f"Page source unavailable: {error}")

    return artifacts


def _short_value(value):
    text = repr(value)
    return text if len(text) <= 220 else text[:217] + "..."


def _friendly_wait_name(name):
    friendly_names = {
        "element_to_be_clickable": "element is clickable",
        "visibility_of_element_located": "element is visible",
        "presence_of_element_located": "element is present",
        "invisibility_of_element_located": "element is hidden",
        "text_to_be_present_in_element": "expected text is visible",
        "staleness_of": "previous element is gone",
    }
    for raw_name, friendly_name in friendly_names.items():
        if raw_name in name:
            return friendly_name
    return name


def _verbose_wait_locators_enabled():
    return os.getenv("VERBOSE_WAIT_LOCATORS", "").strip().lower() in {"1", "true", "yes", "on"}


def _describe_wait_condition(method, message=""):
    if message:
        return message

    name = getattr(method, "__qualname__", None) or getattr(method, "__name__", None) or method.__class__.__name__
    friendly_name = _friendly_wait_name(name)
    if not _verbose_wait_locators_enabled():
        return friendly_name

    details = []
    closure = getattr(method, "__closure__", None) or []
    for cell in closure:
        try:
            value = cell.cell_contents
        except ValueError:
            continue
        if isinstance(value, tuple) and len(value) == 2:
            details.append(_short_value(value))
        elif isinstance(value, str) and value:
            details.append(value)

    if details:
        return f"{friendly_name}: {', '.join(details[:2])}"
    return friendly_name


def _condition_name(method):
    return getattr(method, "__qualname__", None) or getattr(method, "__name__", None) or method.__class__.__name__


def _condition_locator(method):
    closure = getattr(method, "__closure__", None) or []
    for cell in closure:
        try:
            value = cell.cell_contents
        except ValueError:
            continue
        if isinstance(value, tuple) and len(value) == 2:
            return value
    return None


def _locator_label(locator):
    if not locator:
        return ""
    if _verbose_wait_locators_enabled():
        return f" Locator: {_short_value(locator)}"
    return " Set VERBOSE_WAIT_LOCATORS=1 to print the locator."


def _wait_timeout_reason(driver, method):
    locator = _condition_locator(method)
    if not locator:
        return "Condition did not become true before timeout."

    name = _condition_name(method)
    locator_text = _locator_label(locator)
    try:
        elements = driver.find_elements(*locator)
    except Exception as error:
        return f"Could not check element state after timeout: {error.__class__.__name__}: {error}{locator_text}"

    if "presence_of_element_located" in name:
        if not elements:
            return f"Element missing from DOM.{locator_text}"
        return f"Element is present now, but wait still timed out.{locator_text}"

    if "visibility_of_element_located" in name:
        if not elements:
            return f"Element missing from DOM.{locator_text}"
        if not any(element.is_displayed() for element in elements):
            return f"Element exists in DOM but is not visible.{locator_text}"
        return f"Element is visible now, but wait still timed out.{locator_text}"

    if "element_to_be_clickable" in name:
        if not elements:
            return f"Element missing from DOM.{locator_text}"
        visible = [element for element in elements if element.is_displayed()]
        if not visible:
            return f"Element exists in DOM but is not visible.{locator_text}"
        if not any(element.is_enabled() for element in visible):
            return f"Element is visible but disabled, so it is not clickable.{locator_text}"
        return f"Element is visible and enabled now, but Selenium did not mark it clickable before timeout. It may be covered or unstable.{locator_text}"

    if "invisibility_of_element_located" in name:
        if not elements:
            return f"Element is missing from DOM, so it is hidden now.{locator_text}"
        if any(element.is_displayed() for element in elements):
            return f"Element is still visible.{locator_text}"
        return f"Element exists but is hidden now.{locator_text}"

    return f"Condition did not become true before timeout.{locator_text}"


def _click_with_fallback(driver, element):
    try:
        element.click()
    except Exception:
        driver.execute_script("arguments[0].click();", element)


def _logout_if_logged_in(driver):
    try:
        if driver.window_handles:
            driver.switch_to.window(driver.window_handles[0])

        short_wait = WebDriverWait(driver, 3)
        profile_button = short_wait.until(
            lambda active_driver: next(
                (
                    element
                    for element in active_driver.find_elements(By.CSS_SELECTOR, ".headerUsername")
                    if element.is_displayed()
                ),
                None,
            )
        )
        _write_log("Logout: open user profile menu")
        _click_with_fallback(driver, profile_button)

        logout_button = short_wait.until(
            lambda active_driver: next(
                (
                    element
                    for element in active_driver.find_elements(
                        By.XPATH,
                        "//button[.//i[normalize-space()='logout'] or .//span[contains(normalize-space(), 'Log out')]]",
                    )
                    if element.is_displayed() and element.is_enabled()
                ),
                None,
            )
        )
        _write_log("Logout: click Log out")
        _click_with_fallback(driver, logout_button)
        try:
            _write_log("Logout: wait until UI shows logged-out state")
            WebDriverWait(driver, 8).until(
                lambda active_driver: (
                    "login" in active_driver.current_url.lower()
                    or any(
                        element.is_displayed()
                        for element in active_driver.find_elements(By.XPATH, "//input[@type='password']")
                    )
                    or not any(
                        element.is_displayed()
                        for element in active_driver.find_elements(By.CSS_SELECTOR, ".headerUsername")
                    )
                )
            )
            _write_log("Logout: UI shows logged-out state")
        except TimeoutException:
            _write_log("Logout: UI did not show logged-out state before timeout")

        pause_seconds = float(os.getenv("LOGOUT_UI_PAUSE_SECONDS", "5"))
        if pause_seconds > 0:
            _write_log(f"Logout: keep browser open {pause_seconds:.1f}s before session cleanup")
            time.sleep(pause_seconds)
    except Exception as error:
        _write_log(f"Logout skipped: {error.__class__.__name__}: {error}")


def _clear_browser_session(driver):
    try:
        if driver.window_handles:
            driver.switch_to.window(driver.window_handles[0])

        _write_log("Session cleanup: clear cookies and browser storage")
        try:
            driver.delete_all_cookies()
        except Exception as error:
            _write_log(f"Cookie cleanup skipped: {error.__class__.__name__}: {error}")

        try:
            driver.execute_script("window.localStorage && window.localStorage.clear();")
            driver.execute_script("window.sessionStorage && window.sessionStorage.clear();")
        except Exception as error:
            _write_log(f"Storage cleanup skipped: {error.__class__.__name__}: {error}")
    except Exception as error:
        _write_log(f"Session cleanup skipped: {error.__class__.__name__}: {error}")

class LoggingWebDriverWait(WebDriverWait):
    def until(self, method, message=""):
        description = _describe_wait_condition(method, message)
        _write_log(f"WAITING ({self._timeout}s): {description}")
        started_at = time.perf_counter()
        try:
            result = super().until(method, message)
        except TimeoutException:
            _write_log(red_text(f"WAIT TIMEOUT ({self._timeout}s): {description}"))
            try:
                wait_reason = _wait_timeout_reason(self._driver, method)
            except Exception as reason_error:
                wait_reason = f"Could not inspect wait reason: {reason_error.__class__.__name__}: {reason_error}"
            _write_log(red_text(f"WAIT REASON: {wait_reason}"))
            raise
        _write_log(green_text(f"WAIT OK ({time.perf_counter() - started_at:.2f}s): {description}"))
        return result

    def until_not(self, method, message=""):
        description = _describe_wait_condition(method, message)
        _write_log(f"WAITING NOT ({self._timeout}s): {description}")
        started_at = time.perf_counter()
        try:
            result = super().until_not(method, message)
        except TimeoutException:
            _write_log(red_text(f"WAIT NOT TIMEOUT ({self._timeout}s): {description}"))
            try:
                wait_reason = _wait_timeout_reason(self._driver, method)
            except Exception as reason_error:
                wait_reason = f"Could not inspect wait reason: {reason_error.__class__.__name__}: {reason_error}"
            _write_log(red_text(f"WAIT REASON: {wait_reason}"))
            raise
        _write_log(green_text(f"WAIT NOT OK ({time.perf_counter() - started_at:.2f}s): {description}"))
        return result

def pytest_addoption(parser):
    parser.addoption(
        "--suite",
        choices=tuple(SUITE_MARKERS),
        default="all",
        help="Test tier to run. The default preserves all original cases in enabled sections.",
    )
    parser.addoption(
        "--all-modules",
        action="store_true",
        help="Ignore module and section enabled flags from test_config.json.",
    )


def _explicit_mark_expression(config):
    args = tuple(str(arg) for arg in config.invocation_params.args)
    return "-m" in args or any(arg.startswith("--markexpr") for arg in args)


def _reset_failure_artifacts():
    if FAILURE_DIR.exists():
        shutil.rmtree(FAILURE_DIR, ignore_errors=True)
    FAILURE_DIR.mkdir(parents=True, exist_ok=True)

def pytest_configure(config):
    _reset_failure_artifacts()

    if not _explicit_mark_expression(config):
        config.option.markexpr = SUITE_MARKERS[config.getoption("--suite")]

    config.test_run_results = []
    config.failure_summaries = []
    config.skipped_summaries = []

    started_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    args = " ".join(str(arg) for arg in config.invocation_params.args)

    _write_log("TEST RUN STARTED")
    _write_log(f"Started at: {started_at}")
    _write_log(f"Command: pytest {args}".strip())
    _write_log("")


def pytest_collection_modifyitems(config, items):
    automation_config = load_config()
    active_client = get_active_client(automation_config)
    client_config = get_client_config(automation_config, active_client)
    extensions_config = get_extensions_config(automation_config)

    if not extensions_config["cloud_related"]:
        skip_non_cloud = pytest.mark.skip(
            reason=f"Cloud-related test does not apply to non-cloud client '{active_client}'."
        )
        for item in items:
            if item.get_closest_marker("cloud_related"):
                item.add_marker(skip_non_cloud)

    if config.getoption("--all-modules"):
        return
    modules = client_config.get("modules", {})
    administration = modules.get("administration", {})
    administration_enabled = administration.get("enabled", False)
    enabled_sections = administration.get("sections", {})

    selected = []
    deselected = []
    for item in items:
        if extensions_config["cloud_related"] and item.get_closest_marker("cloud_related"):
            selected.append(item)
            continue

        section = next((name for name in SECTION_MARKERS if item.get_closest_marker(name)), None)
        item_path = Path(str(item.fspath))
        if section is None and item_path.parent.name == "administration" and item_path.stem.startswith("test_"):
            candidate = item_path.stem.removeprefix("test_")
            section = candidate if candidate in SECTION_MARKERS else None

        if section is not None and administration_enabled and enabled_sections.get(section, False):
            selected.append(item)
        elif section is not None:
            deselected.append(item)
        elif item_path.parent.name == "modules" and item_path.stem.startswith("test_"):
            module_name = item_path.stem.removeprefix("test_")
            if modules.get(module_name, {}).get("enabled", False):
                selected.append(item)
            else:
                deselected.append(item)
        else:
            selected.append(item)

    if deselected:
        config.hook.pytest_deselected(items=deselected)
        items[:] = selected


def pytest_runtest_setup(item):
    testlink_id, title = _testlink_details(item)
    _write_log(f"RUNNING: {item.nodeid}")
    _write_log(f"TestLink: {testlink_id}")
    _write_log(f"Title: {title}")

    if item.get_closest_marker("requires_microsip"):
        run_config = load_config().get("run", {})
        provider = os.getenv("SOFTPHONE_PROVIDER") or run_config.get("softphone_provider")
        softphone_client = create_softphone_client(provider)
        missing_setup_reason = softphone_client.missing_setup_reason()
        if missing_setup_reason:
            pytest.skip(missing_setup_reason)


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

    result_line = f"RESULT: {status} ({report.when}, {duration})"
    if report.failed:
        _write_log(red_text("-" * 100))
        _write_log(red_text(result_line))
    else:
        _write_log(result_line)
    _write_log(f"Test: {item.nodeid}")
    _write_log(f"TestLink: {testlink_id}")
    _write_log(f"Title: {title}")

    if report.failed:
        failure_summary = _short_failure_text(report)
        item.config.failure_summaries.append(
            {
                "nodeid": item.nodeid,
                "when": report.when,
                "title": title,
                "summary": failure_summary,
            }
        )
        _write_log(red_text("FAILED TEST"))
        _write_log(yellow_text("Failure summary:"))
        _write_log(red_text(failure_summary))
        artifacts = _save_failure_artifacts(item)
        if artifacts:
            _write_log(yellow_text("Failure artifacts:"))
            for artifact in artifacts:
                _write_log(str(artifact))
        if os.getenv("FULL_TRACEBACK_ON_FAILURE", "").strip().lower() in {"1", "true", "yes", "on"}:
            _write_log(red_text("Full traceback follows:"))
            _write_log(red_text(report.longreprtext))
        else:
            _write_log(yellow_text("Full traceback hidden. Set FULL_TRACEBACK_ON_FAILURE=1 to print it."))
    elif report.skipped:
        reason = _skip_reason(report)
        item.config.skipped_summaries.append(
            {
                "nodeid": item.nodeid,
                "when": report.when,
                "title": title,
                "reason": reason,
            }
        )
        _write_log(yellow_text(f"Skip reason: {reason}"))
    _write_log(red_text("-" * 100) if report.failed else "-" * 100)
    _write_log("")


def pytest_sessionfinish(session, exitstatus):
    results = session.config.test_run_results
    passed = results.count("PASSED")
    failed = results.count("FAILED")
    skipped = results.count("SKIPPED")

    _write_log("TEST RUN FINISHED")
    _write_log(f"Finished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    _write_log(f"Passed: {passed}")
    _write_log(f"Failed: {failed}")
    _write_log(f"Skipped: {skipped}")
    _write_log(f"Exit status: {exitstatus}")

    if session.config.failure_summaries:
        _write_log("")
        _write_log(red_text("=" * 100))
        _write_log(red_text("FAILED TEST SUMMARIES"))
        _write_log(red_text("=" * 100))
        for index, failure in enumerate(session.config.failure_summaries, start=1):
            title = failure["title"]
            _write_log(red_text(f"[{index}] {failure['nodeid']}"))
            _write_log(yellow_text(f"Phase: {failure['when']}"))
            if title and title != "No TestLink title":
                _write_log(f"Title: {title}")
            _write_log(red_text(f"Problem: {failure['summary']}"))
            _write_log(red_text("-" * 100))

    if session.config.skipped_summaries:
        _write_log("")
        _write_log(yellow_text("=" * 100))
        _write_log(yellow_text("SKIPPED TEST SUMMARIES"))
        _write_log(yellow_text("=" * 100))
        for index, skipped_test in enumerate(session.config.skipped_summaries, start=1):
            title = skipped_test["title"]
            _write_log(yellow_text(f"[{index}] {skipped_test['nodeid']}"))
            _write_log(yellow_text(f"Phase: {skipped_test['when']}"))
            if title and title != "No TestLink title":
                _write_log(f"Title: {title}")
            reason = skipped_test.get("reason") or "No skip reason reported."
            _write_log(yellow_text(f"Reason: {reason}"))
            _write_log(yellow_text("-" * 100))

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


def _build_chrome_options(run_config, user_data_dir):
    options = ChromeOptions()
    options.add_argument(f"--user-data-dir={user_data_dir}")
    options.add_argument("--disable-application-cache")
    options.add_argument("--disk-cache-size=0")
    options.add_argument("--media-cache-size=0")
    DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)
    options.add_experimental_option(
        "prefs",
        {
            "download.default_directory": str(DOWNLOAD_DIR.resolve()),
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True,
        },
    )

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
    user_data_dir = Path(tempfile.mkdtemp(prefix="automation-chrome-"))
    options = _build_chrome_options(run_config, user_data_dir)
    selenium_remote_url = _config_value(run_config, "SELENIUM_REMOTE_URL", "selenium_remote_url")

    if selenium_remote_url:
        driver = webdriver.Remote(command_executor=selenium_remote_url, options=options)
    else:
        chromedriver_path = _config_value(run_config, "CHROMEDRIVER_PATH", "chromedriver_path")
        service = ChromeService(executable_path=chromedriver_path) if chromedriver_path else None
        driver = webdriver.Chrome(service=service, options=options)

    driver.execute_cdp_cmd(
        "Page.setDownloadBehavior",
        {"behavior": "allow", "downloadPath": str(DOWNLOAD_DIR.resolve())},
    )
    driver.maximize_window()
    try:
        yield driver
    finally:
        _logout_if_logged_in(driver)
        _clear_browser_session(driver)
        driver.quit()
        shutil.rmtree(user_data_dir, ignore_errors=True)


@pytest.fixture(scope="module")
def wait(driver):
    return LoggingWebDriverWait(driver, 20)


@pytest.fixture
def softphone_client():
    run_config = load_config().get("run", {})
    provider = os.getenv("SOFTPHONE_PROVIDER") or run_config.get("softphone_provider")
    client = create_softphone_client(provider)
    try:
        yield client
    finally:
        client.stop()


@pytest.fixture
def microsip(softphone_client):
    return softphone_client


def download_dir():
    DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)
    for path in DOWNLOAD_DIR.glob("*"):
        if path == FAILURE_DIR:
            continue
        if path.is_file():
            path.unlink()
    return DOWNLOAD_DIR
