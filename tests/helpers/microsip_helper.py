import re
import subprocess
import time
from pathlib import Path


DEFAULT_MICROSIP_DIR = Path(__file__).resolve().parent / "helper_tool" / "MicroSIP"
DEFAULT_ACTIVE_CONFIG_PATH = Path.home() / "AppData" / "Roaming" / "MicroSIP" / "MicroSIP.ini"
DEFAULT_CALL_NUMBER = "099452011"


class MicroSIPHelper:
    def __init__(
        self,
        microsip_dir=DEFAULT_MICROSIP_DIR,
        server="10.100.121.30",
        account_label="Kube-dev",
        call_number=DEFAULT_CALL_NUMBER,
        check_command=None,
    ):
        self.microsip_dir = Path(microsip_dir)
        self.exe_path = self.microsip_dir / "microsip.exe"
        local_config_path = self.microsip_dir / "MicroSIP.ini"
        self.config_path = DEFAULT_ACTIVE_CONFIG_PATH if DEFAULT_ACTIVE_CONFIG_PATH.exists() else local_config_path
        self.local_config_path = local_config_path
        self.server = server
        self.account_label = account_label
        self.call_number = call_number
        self.check_command = check_command

    def configure_account(self, extension, password):
        self.ensure_local_config_exists()
        encoding = self._detect_config_encoding()
        content = self.config_path.read_text(encoding=encoding, errors="ignore")
        section_match = self._find_account_section(content)
        if section_match is None:
            raise AssertionError(f"MicroSIP account with label '{self.account_label}' was not found.")

        section = section_match.group(0)
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
        return self

    def restore_config_backup(self):
        backup_path = self.config_path.with_suffix(f"{self.config_path.suffix}.bak")
        if backup_path.exists():
            self.config_path.write_bytes(backup_path.read_bytes())
        return self

    def ensure_local_config_exists(self):
        if self.config_path.exists():
            return self

        if not self.local_config_path.exists():
            raise AssertionError(
                f"Local MicroSIP config is missing: {self.local_config_path}. "
                f"Active config was also not found: {DEFAULT_ACTIVE_CONFIG_PATH}."
            )

        DEFAULT_ACTIVE_CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
        DEFAULT_ACTIVE_CONFIG_PATH.write_bytes(self.local_config_path.read_bytes())
        self.config_path = DEFAULT_ACTIVE_CONFIG_PATH
        return self

    def missing_setup_reason(self):
        if not self.exe_path.exists():
            return f"MicroSIP executable is missing: {self.exe_path}."
        if not self.config_path.exists() and not self.local_config_path.exists():
            return (
                f"MicroSIP config is missing: {self.local_config_path}. "
                f"Active config was also not found: {DEFAULT_ACTIVE_CONFIG_PATH}."
            )
        return ""

    def restart(self):
        subprocess.run(["taskkill", "/IM", "microsip.exe", "/F"], capture_output=True, text=True)
        subprocess.Popen([str(self.exe_path)], cwd=str(self.microsip_dir))
        time.sleep(5)
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
        pattern = re.compile(r"(?ms)^\[Account\d+\]\s.*?(?=^\[|\Z)")
        for match in pattern.finditer(content):
            expected_label = f"label={self.account_label}".lower()
            section_lines = [line.strip().lower() for line in match.group(0).splitlines()]
            if expected_label in section_lines:
                return match
        return None

    @staticmethod
    def _set_key(section, key, value):
        value = str(value)
        pattern = re.compile(rf"(?mi)^{re.escape(key)}=.*$")
        if pattern.search(section):
            return pattern.sub(f"{key}={value}", section, count=1)

        return section.rstrip() + f"\n{key}={value}\n"

    def _detect_config_encoding(self):
        header = self.config_path.read_bytes()[:2]
        if header == b"\xff\xfe":
            return "utf-16"
        if header == b"\xfe\xff":
            return "utf-16-be"
        return "utf-8"
