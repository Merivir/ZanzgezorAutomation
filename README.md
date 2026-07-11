# automation-api

Python Selenium automation skeleton.

## Setup
1) Install Python 3.10+
2) Create and activate a virtual environment:
   - PowerShell:
     `python -m venv .venv`
     `.venv\Scripts\Activate.ps1`
3) Install dependencies:
   `pip install -r requirements.txt`
4) Create local config file:
   `Copy-Item config/test_config.example.json config/test_config.json`

## One-place client config
Copy `tests/config/test_config.example.json` to the ignored local
`tests/config/test_config.json`, then select the active client there. Supply
credentials through `TEST_USERNAME`, `TEST_PASSWORD`, `DB_HOST`, `DB_PORT`,
`DB_NAME`, `DB_USER`, and `DB_PASSWORD` environment variables.
- `active_client`: which client to run now
- `clients.<client>.base_url`: target URL
- `clients.<client>.users`: login accounts (default/admin/supervisor/agent)
- `clients.<client>.modules`: enable/disable module checks with `true` / `false`
- `run.headless`: `true` or `false`
- `run.chromedriver_path`: optional absolute path to local `chromedriver` binary
- `run.chrome_binary_path`: optional absolute path to Chrome/Chromium binary
- `run.selenium_remote_url`: optional Selenium Grid URL (for CI/distributed runs)

To add more clients, copy the `kube1` block and change URL/users.

## Run regression tests
`pytest`

Pytest honors enabled modules/sections from `tests/config/test_config.json` and
runs all their original cases by default.
Use `--suite focused|smoke|extended|destructive|integration|microsip|all` to
choose the test tier, or run `python tests/config/start_testing.py` to execute
all cases from configured enabled sections.

## ReaBe API smoke test
Set these environment variables before running the API smoke test:
- `REABE_BASE_URL` — base URL of the ReaBe API
- `REABE_API_TOKEN` — optional bearer token
- `REABE_API_ENDPOINT` — optional endpoint to call, default `/`
- `REABE_TIMEOUT` — optional request timeout in seconds, default `10`

Example:
`$env:REABE_BASE_URL="https://example.test/api"; $env:REABE_API_ENDPOINT="/health"; pytest tests/modules/test_reabe_api.py`

Optional overrides:
- `TEST_CLIENT` to switch client without editing file:
  `$env:TEST_CLIENT="kube1"; pytest`
- `HEADLESS` to force headless for one run:
  `$env:HEADLESS="true"; pytest`
- `CHROMEDRIVER_PATH` to force local driver binary:
  `$env:CHROMEDRIVER_PATH="C:\tools\chromedriver.exe"; pytest`
- `CHROME_BINARY_PATH` to force browser binary:
  `$env:CHROME_BINARY_PATH="C:\Program Files\Google\Chrome\Application\chrome.exe"; pytest`
- `SELENIUM_REMOTE_URL` to use Selenium Grid:
  `$env:SELENIUM_REMOTE_URL="http://localhost:4444/wd/hub"; pytest`
- `TEST_CONFIG_PATH` to choose a different config file:
  `$env:TEST_CONFIG_PATH="config/test_config.json"; pytest`
- `TEST_MODULES` to run only selected modules for one run:
  `$env:TEST_MODULES="chat,general_info"; pytest`
- `SKIP_MODULES` to temporarily skip selected modules:
  `$env:SKIP_MODULES="chat"; pytest`

## WebDriver prerequisites
At least one of these must be true:
1) Selenium Manager can download/find a matching driver (requires internet access).
2) `chromedriver` is already installed locally and configured via `CHROMEDRIVER_PATH` or `run.chromedriver_path`.
3) Selenium Grid is available and configured via `SELENIUM_REMOTE_URL` or `run.selenium_remote_url`.

## Folder structure
- `config/`: client configs
- `tests/pages/`: page objects
- `tests/modules/`: module-based checks (controlled by config flags)
- `tests/modules/<module_name>/`: tests grouped by module, for example `tests/modules/chat/`
- `tests/test_auth_regression.py`: auth + permissions regression

## How to manage modules
Keep module defaults in `config/test_config.json` and organize tests by module folder.

Suggested pattern:
- `tests/modules/chat/`: all Chatbot / Chat tests
- `tests/modules/general_info/`: General Info tests
- `tests/modules/crm/`: CRM tests

Recommended workflow:
- Use `config/test_config.json` for normal default on/off behavior per client
- Use `TEST_MODULES` when you want to focus on only one or two modules in a run
- Use `SKIP_MODULES` when one module is unstable and you want the rest to run

Examples:
- Run only chat tests:
  `$env:TEST_MODULES="chat"; pytest`
- Run chat and general info only:
  `$env:TEST_MODULES="chat,general_info"; pytest`
- Run everything except chat:
  `$env:SKIP_MODULES="chat"; pytest`

## Included automated coverage (from TestLink XML)
- TC-1: Login page opens with required elements
- TC-2: Invalid login validation
- TC-3: Valid login
- TC-73 / TC-609 / TC-74: Role-based menu access (admin/supervisor/agent)
- TC-86: Agent cannot open restricted URLs
- TC-87: Logout flow
- Module checks: enabled sidebar modules are validated from config
