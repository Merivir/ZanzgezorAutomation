# Test Config Guide

This folder contains the configuration used by the automation tests.

## Files

- `test_config.example.json`: safe configuration template committed to Git
- `test_config.json`: ignored local configuration created from the template
- `automation_config.py`: helpers for reading config values
- `start_testing.py`: simple runner that reads active modules and sections

## How To Configure

Create your ignored local configuration from the safe template:

```powershell
Copy-Item tests/config/test_config.example.json tests/config/test_config.json
```

Keep credentials out of JSON when possible and set them for the current PowerShell session:

```powershell
$env:TEST_USERNAME="your-user"
$env:TEST_PASSWORD="your-password"
$env:DB_HOST="database-host"
$env:DB_PORT="3306"
$env:DB_NAME="database-name"
$env:DB_USER="database-user"
$env:DB_PASSWORD="database-password"
```

Role-specific credentials can use names such as `TEST_ADMIN_USERNAME`,
`TEST_ADMIN_PASSWORD`, `TEST_AGENT_USERNAME`, and `TEST_AGENT_PASSWORD`.

### Active Client

Set which client should be used:

```json
"active_client": "kube1"
```

The value must exist under `clients`.

### Run Settings

```json
"run": {
  "headless": false,
  "chromedriver_path": "",
  "chrome_binary_path": "",
  "selenium_remote_url": "",
  "softphone_provider": "pjsua"
}
```

- `headless`: run browser without UI when `true`
- `chromedriver_path`: optional custom ChromeDriver path
- `chrome_binary_path`: optional custom Chrome path
- `selenium_remote_url`: optional Selenium Grid / remote driver URL
- `softphone_provider`: `pjsua` by default; `microsip` is also supported

### Users

Each client can have multiple users:

```json
"users": {
  "default": {
    "username": "",
    "password": "",
    "enabled": true
  }
}
```

The tests currently use the `default` user in several places.

### Modules And Sections

Modules can be turned on or off with `enabled`.
Complex modules can also enable only selected sections.

Example:

```json
"modules": {
  "dashboard": {
    "enabled": true,
    "sections": {}
  },
  "administration": {
    "enabled": true,
    "sections": {
      "extensions": true,
      "users": false,
      "roles": true
    }
  }
}
```

Behavior:

- if module `enabled` is `false`, that module is skipped
- if module `enabled` is `true`, that module is included
- inside `sections`, `true` means that section should run
- inside `sections`, `false` means that section should be skipped

## How The Runner Works

`automation_config.py` currently provides helpers to:

- load the JSON config
- get the active client
- get user credentials
- get active modules
- get active sections for a module

`start_testing.py`:

1. loads the config
2. finds active modules
3. finds active sections for each module
4. sets `ACTIVE_SECTIONS` environment variable
5. runs the selected section files through one pytest process

For example, if `administration` is enabled, it runs:

```text
tests/modules/administration/test_administration.py
```

## How To Run

Run the config-based module runner from the project root:

```powershell
python tests/config/start_testing.py
```

## Running A Specific Pytest File

You can also run one pytest file directly:

```powershell
pytest -s tests/modules/administration/test_extensions.py
```

Run one specific test function:

```powershell
pytest -s tests/modules/administration/test_extensions.py::test_extensions_page_opens_correctly
```

## Notes

- `-s` shows `print()` output in the terminal
- page objects live under `tests/pages`
- test files should usually be named `test_*.py`
- test functions should usually be named `test_*`

## Test Tiers

Every pytest run honors the active client's module and section `enabled` flags
from `test_config.json`. Normal runs preserve all original cases in those sections.

```powershell
python -m pytest -v -s
python -m pytest --suite focused -v -s
python -m pytest --suite smoke -v -s
python -m pytest --suite extended -v -s
python -m pytest --suite destructive -v -s
python -m pytest --suite integration -v -s
python -m pytest --suite microsip -v -s
python -m pytest --suite all -v -s
```

Destructive, integration, and MicroSIP tests are opt-in because they can change
external state or require additional services.

Use `--all-modules` to ignore config enablement temporarily. A direct `-m`
expression is also supported and takes precedence over `--suite`:

```powershell
python -m pytest --all-modules --suite smoke -v -s
python -m pytest --all-modules -m notifications -v -s
```

Running `python tests/config/start_testing.py` preserves the original workflow:
it executes all cases from the sections enabled in `test_config.json`.
