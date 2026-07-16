import os
import re
import subprocess
import time
from pathlib import Path

from tests.helpers.softphones.base import SoftphoneClient


DEFAULT_MICROSIP_DIR = Path(__file__).resolve().parent / "helper_tool" / "MicroSIP"
DEFAULT_CALL_NUMBER = "099452011"


class MicroSIPHelper(SoftphoneClient):
    provider_name = "MicroSIP"

    def __init__(
        self,
        microsip_dir=DEFAULT_MICROSIP_DIR,
        server="10.100.121.30",
        account_label="Kube-dev",
        call_number=DEFAULT_CALL_NUMBER,
        check_command=None,
        decline_command=None,
        call_control_mode=None,
    ):
        self.microsip_dir = Path(microsip_dir).resolve()
        self.exe_path = self.microsip_dir / "MicroSIP.exe"
        self.config_path = self.microsip_dir / "microsip.ini"
        self.server = server
        self.account_label = account_label
        self.call_number = call_number
        self.check_command = check_command
        self.decline_command = decline_command or os.getenv("MICROSIP_DECLINE_COMMAND")
        self.call_control_mode = (call_control_mode or os.getenv("MICROSIP_CALL_CONTROL", "normal")).strip().lower()

    def log_action(self, message):
        print(f"[MicroSIP] {message}", flush=True)

    def configure_call_control(self, mode=None):
        mode = (mode or self.call_control_mode or "normal").strip().lower()
        modes = {
            "normal": {"AA": "0", "DND": "0", "autoHangUpTime": "0"},
            "dnd": {"AA": "0", "DND": "1", "autoHangUpTime": "0"},
            "auto_answer": {"AA": "1", "DND": "0", "autoHangUpTime": os.getenv("MICROSIP_AUTO_HANGUP_SECONDS", "3")},
            "aa": {"AA": "1", "DND": "0", "autoHangUpTime": os.getenv("MICROSIP_AUTO_HANGUP_SECONDS", "3")},
        }
        if mode not in modes:
            raise AssertionError(f"Unsupported MicroSIP call-control mode: {mode}. Use normal, dnd, or auto_answer.")

        self.ensure_local_config_exists()
        encoding = self._detect_config_encoding()
        content = self.config_path.read_text(encoding=encoding, errors="ignore")
        for key, value in modes[mode].items():
            content = self._set_key(content, key, value)

        self.config_path.write_text(content, encoding=encoding)
        self.log_action(f"Call control mode configured: {mode}")
        return self

    def configure_account(self, extension, password):
        extension = str(extension)
        password = str(password)
        if not password:
            raise AssertionError("MicroSIP password cannot be empty; it must match the password used when adding the extension.")

        self.stop()
        self.ensure_local_config_exists()
        self.configure_call_control()
        encoding = self._detect_config_encoding()
        content = self.config_path.read_text(encoding=encoding, errors="ignore")
        section_match = self._find_account_section(content)
        if section_match is None:
            raise AssertionError(f"MicroSIP account with label '{self.account_label}' was not found.")

        self.log_action(f"Local folder: {self.microsip_dir}")
        self.log_action(f"Config path: {self.config_path}")
        self.log_action(f"Exe path: {self.exe_path}")
        self.log_action(f"Configure account {self.account_label}: extension={extension}, password=<same as created extension>")
        section_name = section_match.group(1)
        self.log_action(f"Editing active local account section: [{section_name}]")
        section = section_match.group(0)
        section = self._set_key(section, "label", self.account_label)
        section = self._set_key(section, "server", self.server)
        section = self._set_key(section, "domain", self.server)
        section = self._set_key(section, "username", extension)
        section = self._set_key(section, "authID", extension)
        section = self._set_key(section, "password", password)

        updated_content = content[:section_match.start()] + section + content[section_match.end():]
        backup_path = self.config_path.with_suffix(f"{self.config_path.suffix}.bak")
        if not backup_path.exists():
            backup_path.write_text(content, encoding=encoding)
        self.config_path.write_text(updated_content, encoding=encoding)
        self.assert_account_credentials(extension=extension, password=password)
        return self

    def restore_config_backup(self):
        self.stop()
        backup_path = self.config_path.with_suffix(f"{self.config_path.suffix}.bak")
        if backup_path.exists():
            self.config_path.write_bytes(backup_path.read_bytes())
        return self

    def ensure_local_config_exists(self):
        if not self.config_path.exists():
            raise AssertionError(f"MicroSIP config is missing: {self.config_path}.")
        return self

    def configured_account_values(self):
        self.ensure_local_config_exists()
        encoding = self._detect_config_encoding()
        content = self.config_path.read_text(encoding=encoding, errors="ignore")
        section_match = self._find_account_section(content)
        if section_match is None:
            raise AssertionError(f"MicroSIP account with label '{self.account_label}' was not found.")
        return self._section_values(section_match.group(0))

    def assert_account_credentials(self, extension, password):
        values = self.configured_account_values()
        expected = {
            "username": str(extension),
            "authid": str(extension),
        }
        mismatches = [
            f"{key}: expected {expected_value!r}, got {values.get(key, '')!r}"
            for key, expected_value in expected.items()
            if values.get(key, "") != expected_value
        ]
        stored_password = values.get("password", "")
        assert stored_password, "MicroSIP config password is empty after writing created extension credentials."
        assert not mismatches, "MicroSIP config does not match created extension credentials. " + "; ".join(mismatches)
        return self

    def missing_setup_reason(self):
        if not self.exe_path.exists():
            return f"MicroSIP executable is missing: {self.exe_path}."
        if not self.config_path.exists():
            return f"MicroSIP config is missing: {self.config_path}."
        return ""

    def stop(self):
        subprocess.run(["taskkill", "/IM", "microsip.exe", "/F"], capture_output=True, text=True)
        time.sleep(1)
        return self

    def restart(self):
        self.stop()
        subprocess.Popen([str(self.exe_path)], cwd=str(self.microsip_dir))
        time.sleep(8)
        self.assert_running_from_expected_folder()
        return self


    def running_process_paths(self):
        command = [
            "powershell",
            "-NoProfile",
            "-Command",
            "Get-Process MicroSIP -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Path",
        ]
        result = subprocess.run(command, capture_output=True, text=True)
        return [line.strip() for line in result.stdout.splitlines() if line.strip()]

    def assert_running_from_expected_folder(self):
        expected_path = str(self.exe_path.resolve()).lower()
        process_paths = [path.lower() for path in self.running_process_paths()]
        self.log_action(f"Running process paths: {process_paths}")
        assert expected_path in process_paths, (
            f"MicroSIP is not running from expected folder. Expected: {self.exe_path}; running: {process_paths}"
        )
        return self

    def log_path(self):
        return self.microsip_dir / "MicroSIP_log.txt"

    def log_marker(self):
        log_path = self.log_path()
        return log_path.stat().st_size if log_path.exists() else 0

    def read_log_since(self, marker):
        log_path = self.log_path()
        if not log_path.exists():
            return ""

        with log_path.open("rb") as log_file:
            try:
                log_file.seek(marker)
            except OSError:
                log_file.seek(0)
            return log_file.read().decode("utf-8", errors="ignore")

    def wait_for_incoming_call(self, marker=None, timeout=30):
        marker = self.log_marker() if marker is None else marker
        deadline = time.time() + timeout
        incoming_patterns = ("REQUEST MSG INVITE", "INVITE SIP:", "INCOMING CALL")
        while time.time() < deadline:
            content = self.read_log_since(marker)
            upper_content = content.upper()
            if any(pattern in upper_content for pattern in incoming_patterns):
                self.log_action("Incoming call reached MicroSIP.")
                return self
            time.sleep(1)

        tail = "\n".join(self.read_log_since(marker).splitlines()[-30:])
        raise AssertionError(f"Incoming call did not reach MicroSIP within {timeout}s. Log tail:\n{tail}")

    def decline_incoming_call(self):
        self.log_action("Decline incoming call in MicroSIP")
        if self.decline_command:
            result = subprocess.run(self.decline_command, shell=True, capture_output=True, text=True, timeout=15)
            print(result.stdout, flush=True)
            print(result.stderr, flush=True)
            if result.returncode != 0:
                raise AssertionError(f"MICROSIP_DECLINE_COMMAND failed with exit code {result.returncode}.")
            return self

        if self._send_escape_to_microsip_window():
            time.sleep(2)
            return self

        self.log_action("Could not send decline key to MicroSIP window; stopping MicroSIP to end the call.")
        return self.stop()

    def _send_escape_to_microsip_window(self):
        command = r'''
$signature = '[DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr hWnd);'
Add-Type -MemberDefinition $signature -Name WindowApi -Namespace MicroSIPTest -ErrorAction SilentlyContinue
$process = Get-Process MicroSIP -ErrorAction SilentlyContinue | Where-Object { $_.MainWindowHandle -ne 0 } | Select-Object -First 1
if (-not $process) { exit 2 }
[MicroSIPTest.WindowApi]::SetForegroundWindow($process.MainWindowHandle) | Out-Null
Start-Sleep -Milliseconds 300
$shell = New-Object -ComObject WScript.Shell
$shell.SendKeys('{ESC}')
Start-Sleep -Milliseconds 500
'''
        result = subprocess.run(["powershell", "-NoProfile", "-Command", command], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            return True

        self.log_action(f"MicroSIP Escape decline failed: exit={result.returncode}; stderr={result.stderr.strip()}")
        return False

    def assert_account_loaded_in_log(self, extension):
        log_path = self.log_path()
        if not log_path.exists():
            raise AssertionError(f"MicroSIP log was not created: {log_path}")

        expected = f'<sip:{extension}@{self.server}>'
        content = log_path.read_text(encoding="utf-8", errors="ignore")
        if expected not in content:
            tail = "\n".join(content.splitlines()[-40:])
            raise AssertionError(
                f"MicroSIP started, but account {expected} was not found in MicroSIP log. Log tail:\n{tail}"
            )

        if "REGISTER" not in content.upper():
            self.log_action(
                "Account is loaded in MicroSIP, but no REGISTER line appeared in MicroSIP_log.txt. "
                "This does not prove ONLINE status."
            )
        else:
            self.log_action("MicroSIP log contains REGISTER activity.")
        return self

    def call(self, number=None):
        number = str(number or self.call_number)
        subprocess.Popen([str(self.exe_path), number], cwd=str(self.microsip_dir))
        time.sleep(5)
        return self

    def call_succeeds(self, number=None, extension=None, password=None):
        number = str(number or self.call_number)
        if self.check_command:
            return self._run_check_command(number, extension=extension, password=password)

        self.call(number)
        raise AssertionError(
            "MicroSIP call was started, but automatic call-status verification is not configured. "
            "Set MICROSIP_CHECK_COMMAND to return 0 for success and non-zero for declined/failed calls."
        )

    def call_is_declined(self, number=None, extension=None, password=None):
        return not self.call_succeeds(number=number, extension=extension, password=password)

    def can_call(self, number=None, extension=None, password=None):
        return self.call_succeeds(number=number, extension=extension, password=password)

    def _run_check_command(self, number, extension=None, password=None):
        command = self.check_command.format(
            extension=extension or "",
            password=password or "",
            server=self.server,
            number=number,
            microsip_dir=str(self.microsip_dir),
        )
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
        print(result.stdout, flush=True)
        print(result.stderr, flush=True)
        return result.returncode == 0

    def _find_account_section(self, content):
        active_account_id = self._active_account_id(content)
        account_pattern = re.compile(r"(?ms)^\[(Account\d+)\]\s.*?(?=^\[|\Z)")
        matches = list(account_pattern.finditer(content))

        if active_account_id is not None:
            active_section_name = f"Account{active_account_id}"
            for match in matches:
                if match.group(1).lower() == active_section_name.lower():
                    return match

        expected_label = f"label={self.account_label}".lower()
        for match in matches:
            section_lines = [line.strip().lower() for line in match.group(0).splitlines()]
            if expected_label in section_lines:
                return match
        return None

    @staticmethod
    def _active_account_id(content):
        match = re.search(r"(?mi)^accountId=(\d+)\s*$", content)
        if match:
            return match.group(1)
        return None

    @staticmethod
    def _set_key(section, key, value):
        value = str(value)
        pattern = re.compile(rf"(?mi)^{re.escape(key)}=.*$")
        if pattern.search(section):
            return pattern.sub(f"{key}={value}", section, count=1)

        return section.rstrip() + f"\n{key}={value}\n"


    @staticmethod
    def _section_values(section):
        values = {}
        for line in section.splitlines():
            if "=" not in line:
                continue
            key, value = line.split("=", 1)
            values[key.strip().lower()] = value.strip()
        return values

    def _detect_config_encoding(self):
        header = self.config_path.read_bytes()[:2]
        if header == b"\xff\xfe":
            return "utf-16"
        if header == b"\xfe\xff":
            return "utf-16-be"
        return "utf-8"
