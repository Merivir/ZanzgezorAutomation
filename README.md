# Zangezor Automation

Python automation framework for browser, API, database-assisted verification,
and SIP call scenarios. Tests are organized by business module and support
multiple client environments through configuration.

## Documentation

- [Client adaptation guide](docs/CLIENT_ADAPTATION_GUIDE.md): architecture,
  client onboarding, test-catalogue migration, SIP integration, and acceptance
  criteria.
- [Client adaptation guide for Word](docs/Client_Adaptation_Guide.docx):
  formatted client-facing handover document.
- [Windows PC setup](docs/WINDOWS_SETUP.md): complete workstation setup,
  including Python, Chrome, database access, and PJSUA.
- [Extensions test guide](docs/EXTENSIONS_TEST_GUIDE.md): Extensions scenarios,
  data selection, Publish behavior, cleanup, and troubleshooting.
- [Configuration reference](tests/config/README.md): supported local settings
  and environment-variable overrides.

## Setup

For complete instructions for preparing a new Windows PC, including Chrome,
Python, credentials, database access, and PJSUA, see
[Windows PC setup](docs/WINDOWS_SETUP.md).

Quick setup from PowerShell:

```powershell
git clone https://github.com/Merivir/ZanzgezorAutomation.git
Set-Location ZanzgezorAutomation
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
Copy-Item tests\config\test_config.example.json tests\config\test_config.json
```

## One-place client config

Copy `tests/config/test_config.example.json` to the ignored local
`tests/config/test_config.json`, then select the active client there. Supply
credentials through `TEST_USERNAME`, `TEST_PASSWORD`, `DB_HOST`, `DB_PORT`,
`DB_NAME`, `DB_USER`, and `DB_PASSWORD` environment variables.

- `active_client`: which client to run now
- `clients.<client>.base_url`: target URL
- `clients.<client>.users`: login accounts (default/admin/supervisor/agent)
- `clients.<client>.modules`: enable or disable module checks
- `clients.<client>.extensions.company_name`: exact company name used to scope extension data
- `clients.<client>.extensions.cloud_related`: enables cloud-only scenarios
- `clients.<client>.extensions.sip_check_enabled`: enables SIP integration checks
- `clients.<client>.extensions.pjsip_supported`: enables existing PJSIP extension scenarios
- `clients.<client>.extensions.webrtc_supported`: enables WebRTC extension creation and user-attachment scenarios
- `clients.<client>.telephony.sip_server`: SIP server used by PJSUA/MicroSIP
- `clients.<client>.telephony.call_number`: destination number used by SIP call checks
- `clients.<client>.telephony.local_port`: local PJSUA SIP port
- `run.headless`: `true` or `false`
- `run.softphone_provider`: softphone adapter; `pjsua` is the default
- `run.chromedriver_path`: optional absolute path to a local `chromedriver`
- `run.chrome_binary_path`: optional absolute path to Chrome/Chromium
- `run.selenium_remote_url`: optional Selenium Grid URL

To add another client, copy an existing client block and update its URL, users,
company name, modules, and local database connection. Do not add client names,
URL checks, credentials, or extension prefixes to test code.

### Extension identity

The Administration page and web softphone use the normal `extension` value.
The external SIP client uses `real_extension` when the saved database row has
one; otherwise it uses `extension`. A non-empty `real_extension` also means
the Add or Delete change must be published before SIP verification. No SIP
prefix is calculated in configuration.

Extension type is selected by each workflow: current PJSIP helpers pass `pjsip`, and future WebRTC helpers pass `webrtc`.

### Configured client capabilities

| Client key | Base URL | Company name | PJSIP | WebRTC |
| --- | --- | --- | --- | --- |
| `kube1` | `https://kube1.teamsolutions.am` | `kube1` | Yes | No |
| `newhzor` | `https://new-hzor.teamsolutions.am/` | `new-hzor` | Yes | Yes |
| `ameria` | `https://ameria.teamsolutions.am/` | `Ameria` | Yes | Yes |

## Run regression tests

```powershell
python -m pytest -v -s
```

Pytest honors enabled modules and sections from
`tests/config/test_config.json`. Use
`--suite focused|smoke|extended|destructive|integration|microsip|all` to
choose a test tier, or run `python tests/config/start_testing.py` to execute
all cases from configured enabled sections.

Useful focused commands:

```powershell
# Validate collection without opening a browser
python -m pytest --collect-only -q

# Run Extensions only
python -m pytest tests\modules\administration\test_extensions.py -v -s

# Temporarily select another client
$env:TEST_CLIENT = "newhzor"
python -m pytest -v -s
Remove-Item Env:TEST_CLIENT
```

### Optional run overrides

- `TEST_CLIENT`: switch client without editing the file
- `HEADLESS`: force headless mode for one run
- `CHROMEDRIVER_PATH`: force a local driver binary
- `CHROME_BINARY_PATH`: force a browser binary
- `SELENIUM_REMOTE_URL`: use Selenium Grid
- `TEST_CONFIG_PATH`: choose a different configuration file
- `TEST_MODULES`: run only selected modules
- `SKIP_MODULES`: temporarily skip selected modules

Examples:

```powershell
$env:TEST_MODULES = "chat,general_info"
python -m pytest -v -s

$env:SKIP_MODULES = "chat"
python -m pytest -v -s
```

## ReaBe API smoke test

Set these environment variables before running the API smoke test:

- `REABE_BASE_URL`: base URL of the ReaBe API
- `REABE_API_TOKEN`: optional bearer token
- `REABE_API_ENDPOINT`: optional endpoint, default `/`
- `REABE_TIMEOUT`: optional request timeout in seconds, default `10`

Example:

```powershell
$env:REABE_BASE_URL = "https://example.test/api"
$env:REABE_API_ENDPOINT = "/health"
python -m pytest tests/modules/test_reabe_api.py
```

## WebDriver prerequisites

At least one of these must be true:

1. Selenium Manager can download or find a matching driver. This requires internet access.
2. `chromedriver` is installed locally and configured through `CHROMEDRIVER_PATH` or `run.chromedriver_path`.
3. Selenium Grid is configured through `SELENIUM_REMOTE_URL` or `run.selenium_remote_url`.

## Folder structure

- `tests/config/`: client profiles and run configuration
- `tests/pages/`: page objects and browser interactions
- `tests/modules/`: business-module test scenarios
- `tests/helpers/`: reusable workflows, assertions, logging, and integrations
- `tests/helpers/softphones/`: provider-neutral softphone adapters
- `tests/db/`: parameterized database queries
- `tools/pjsua/`: local PJSUA executable used by SIP integration tests
- `docs/`: setup, onboarding, and module documentation

## How to manage modules

Keep module defaults in `tests/config/test_config.json` and organize tests by
module folder.

Suggested pattern:

- `tests/modules/chat/`: Chatbot and Chat tests
- `tests/modules/general_info/`: General Info tests
- `tests/modules/crm/`: CRM tests
- `tests/modules/administration/`: Administration tests

Recommended workflow:

- Use `tests/config/test_config.json` for normal per-client module selection.
- Use `TEST_MODULES` to focus on one or two modules.
- Use `SKIP_MODULES` when one module is unstable and the rest should run.

## Included automated coverage

- TC-1: Login page opens with required elements
- TC-2: Invalid login validation
- TC-3: Valid login
- TC-73 / TC-609 / TC-74: Role-based menu access
- TC-86: Agent cannot open restricted URLs
- TC-87: Logout flow
- Enabled sidebar modules are validated from configuration
- Extensions page, search, columns, export, edit, add, mobile, delete, pagination,
  Publish, and SIP integration scenarios

The supplied Calls catalogue contains 120 manual cases across Calls, Call
Statuses, Hold/Mute, Call Resolution, and Calls Tab. These are migration inputs,
not automatically considered implemented. Preserve each TestLink ID and title
when converting a case to pytest.

## Issues observed during adaptation

| Observed problem | Cause or debugging direction | Current handling |
| --- | --- | --- |
| `ModuleNotFoundError: requests` during collection | Dependencies were not installed in the active virtual environment | Activate `.venv` and run `python -m pip install -r requirements.txt` |
| Selenium showed only an empty `TimeoutException` | Raw waits did not describe the expected UI state | Wait logs state the condition and elapsed time; failed UI tests save screenshot and HTML artifacts |
| Many later tests failed after Add setup failed | One setup failure left required data unavailable and caused cascading errors | Add Submit has an explicit enabled wait, and reusable steps report the failed business action |
| Extensions were returned as `None` while rows were visible | Headers such as `EXTENSION`, `REAL EXT`, and `NUMBER` were mapped incorrectly | Table parsing must normalize headers before converting rows into records |
| CSV values appeared under the wrong columns | Table and CSV headers used different names; CSV may also contain a UTF-8 BOM | CSV parsing normalizes BOM/header names and validates Real Extension separately |
| Cloud SIP registration failed with the short extension | Administration uses `extension`, while SIP may require `real_extension` | SIP identity comes from the saved row and uses `real_extension` when present |
| A call worked only after Publish in one environment | Publish behavior differs by stored extension identity | Publish is derived from non-empty `real_extension`, not a client flag |
| New extensions remained after a failed run | Cleanup was skipped or Delete was not published | Teardown attempts UI deletion, publishes when required, verifies absence, and logs the result |
| MicroSIP account was missing or stayed offline | Multiple INI paths, encoded passwords, and GUI state made configuration unreliable | PJSUA is the default automation provider; MicroSIP remains optional |
| SIP tests were skipped | The selected SIP executable was missing or its path was incorrect | Keep `tools/pjsua/pjsua.exe` available or set `PJSUA_EXE` |
| Logout looked successful but the session remained usable | UI logout and browser token/cookie cleanup are separate concerns | Teardown clicks Log out, waits for logged-out UI, then clears cookies and browser storage |

When a failure occurs, start with the final one-line summary, failed step,
browser URL, screenshot, and HTML artifact. Enable the full traceback only when
the concise report is not enough:

```powershell
$env:FULL_TRACEBACK_ON_FAILURE = "1"
python -m pytest -v -s
Remove-Item Env:FULL_TRACEBACK_ON_FAILURE
```

## Test-data safety

- Do not change database schema, permissions, or production data.
- Use parameterized, company-scoped, and extension-type-scoped queries.
- Create and delete disposable records through the UI by default.
- Database mutation requires explicit authorization from the client.
- Never commit credentials, SIP passwords, access tokens, or populated local
  configuration files.
