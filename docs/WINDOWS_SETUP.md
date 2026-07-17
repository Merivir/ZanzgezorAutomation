# Windows PC Setup

Use this guide to prepare a new Windows PC to run the automation project.

## 1. Install Required Software

Install:

- Git for Windows
- Python 3.10 or newer (Python 3.12 is currently used successfully)
- Google Chrome
- A code editor such as Visual Studio Code or PyCharm
- The company VPN or network access required to reach the test application,
  SIP server, and database

During Python installation, enable **Add Python to PATH**.

Verify the installations in a new PowerShell window:

```powershell
git --version
py --version
python --version
```

If PowerShell prevents virtual-environment activation, run this once for the
current Windows user:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

## 2. Clone The Project

```powershell
Set-Location $HOME\Desktop
git clone https://github.com/Merivir/ZanzgezorAutomation.git
Set-Location ZanzgezorAutomation
```

## 3. Create The Python Environment

Run these commands from the project root:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

The terminal prompt should begin with `(.venv)`. Activate this environment
again whenever you open a new terminal.

## 4. Create The Local Configuration

The real configuration is ignored by Git. Create it from the safe template:

```powershell
Copy-Item tests\config\test_config.example.json tests\config\test_config.json
```

In `tests/config/test_config.json`:

1. Set `active_client` to the environment being tested.
2. Enable the required modules and administration sections.
3. Keep `run.softphone_provider` as `pjsua` for extension call tests.
4. Use `headless: false` while setting up or debugging the PC.

Environment behavior is configured per client under `extensions`:

- `cloud_related`: whether cloud-only tests apply
- `sip_check_enabled`: whether SIP checks should run
- `pjsip_supported`: whether PJSIP extension scenarios are available
- `webrtc_supported`: whether WebRTC extension creation and user attachment are available
- Publish behavior is derived from `real_extension`; non-empty values require Publish
- `company_name`: exact database company used to scope extension data

Do not change permission fields as part of environment setup.

## 5. Supply Credentials Safely

Set credentials in the PowerShell session instead of committing them:

```powershell
$env:TEST_USERNAME="your-username"
$env:TEST_PASSWORD="your-password"
$env:DB_HOST="database-host"
$env:DB_PORT="3306"
$env:DB_NAME="database-name"
$env:DB_USER="database-user"
$env:DB_PASSWORD="database-password"
```

To select a client without editing JSON:

```powershell
$env:TEST_CLIENT="kube1"
```

These values last for the current PowerShell window. This is intentional and
reduces the chance of committing secrets.

## 6. Verify Chrome And WebDriver

Selenium Manager normally finds Chrome and obtains a compatible driver. Run:

```powershell
python -m pytest --collect-only -q
```

If automatic driver discovery is unavailable, download the ChromeDriver version
matching Chrome and set:

```powershell
$env:CHROMEDRIVER_PATH="C:\tools\chromedriver.exe"
```

Chrome and ChromeDriver major versions must match.

## 7. Verify PJSUA

The tested Windows PJSUA executable is included at:

```text
tools\pjsua\pjsua.exe
```

No MicroSIP account needs to be created manually when `softphone_provider` is
`pjsua`. The test creates the SIP account configuration from the extension and
password used in that test.

On the first run, Windows Firewall may ask for permission. Allow PJSUA on the
network used to access the SIP server. Ensure UDP traffic to the configured SIP
server is allowed and that local SIP port `5062` is available.

An alternative executable can be selected with:

```powershell
$env:PJSUA_EXE="C:\tools\pjsua.exe"
```

## 8. Run A First Test

Start with test collection:

```powershell
python -m pytest --collect-only -q
```

Run all configured sections:

```powershell
python tests\config\start_testing.py
```

Run the verified extension and PJSUA scenario:

```powershell
python -m pytest -v -s tests\modules\administration\test_extensions.py::test_single_extension_can_make_call_from_ui
```

The scenario should log in, add an extension, register PJSUA, receive and end
the call, delete the extension, verify database cleanup, and log out.

## 9. Common Problems

- `ModuleNotFoundError`: activate `.venv` and reinstall `requirements.txt`.
- Login rejected: verify `TEST_USERNAME`, `TEST_PASSWORD`, and `TEST_CLIENT`.
- Application does not open: connect to the required VPN/network and verify the
  configured base URL.
- Database connection fails: verify VPN access, DB environment variables, and
  that the database port is reachable.
- ChromeDriver error: update ChromeDriver or let Selenium Manager obtain it.
- PJSUA does not register: verify the SIP server route, firewall, UDP access,
  extension password, and that port `5062` is free.
- Test is skipped as cloud-related: the selected client has
  `extensions.cloud_related` set to `false`.

## 10. Daily Start

For later sessions, the short routine is:

```powershell
Set-Location $HOME\Desktop\ZanzgezorAutomation
.\.venv\Scripts\Activate.ps1
$env:TEST_USERNAME="your-username"
$env:TEST_PASSWORD="your-password"
python tests\config\start_testing.py
```