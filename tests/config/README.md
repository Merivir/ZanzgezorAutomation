# Test Config Guide

This folder contains the configuration used by the automation tests.

## Files

- `test_config.json`: main test configuration
- `automation_config.py`: helpers for reading config values
- `start_testing.py`: simple runner that reads active modules and sections

## How To Configure

Edit [`test_config.json`](/c:/Users/meri.virabyan/Desktop/automation-api/tests/config/test_config.json).

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
  "selenium_remote_url": ""
}
```

- `headless`: run browser without UI when `true`
- `chromedriver_path`: optional custom ChromeDriver path
- `chrome_binary_path`: optional custom Chrome path
- `selenium_remote_url`: optional Selenium Grid / remote driver URL

### Users

Each client can have multiple users:

```json
"users": {
  "default": {
    "username": "meri_admin",
    "password": "Test12345",
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
5. runs `tests/modules/{module_name}/test_{module_name}.py`

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

## Current Limitation

`start_testing.py` currently runs module files with:

```python
os.system(f"python {test_file}")
```

That means it behaves like a custom Python runner.
As the project grows, it will be better to run the tests with `pytest` directly instead of launching test files with plain `python`.
