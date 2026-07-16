import os
import shutil
import subprocess
import time
from pathlib import Path

from tests.helpers.softphones.base import SoftphoneClient


DEFAULT_PJSUA_EXE = (
    Path("tools")
    / "pjsua"
    / "pjsua.exe"
)


class PjsuaClient(SoftphoneClient):
    provider_name = "PJSUA"

    def __init__(
        self,
        pjsua_exe=None,
        server="10.100.121.30",
        local_port="5062",
        call_number="099452011",
        auto_answer_code="200",
        auto_hangup_seconds="3",
        work_dir=None,
    ):
        self.pjsua_exe = pjsua_exe or os.getenv("PJSUA_EXE") or shutil.which("pjsua") or str(DEFAULT_PJSUA_EXE.resolve())
        self.server = server
        self.local_port = str(local_port)
        self.call_number = call_number
        self.auto_answer_code = str(auto_answer_code)
        self.auto_hangup_seconds = str(auto_hangup_seconds)
        self.work_dir = Path(work_dir or os.getenv("PJSUA_WORK_DIR", "tests/downloads/pjsua")).resolve()
        self.extension = ""
        self.password = ""
        self.process = None
        self.check_command = None
        self.log_file = self.work_dir / "pjsua.log"
        self.pid_file = self.work_dir / "pjsua.pid"

    def missing_setup_reason(self):
        if not self.pjsua_exe:
            return "PJSUA executable is missing. Build PJSIP or set PJSUA_EXE to pjsua.exe."
        if not Path(self.pjsua_exe).exists() and shutil.which(str(self.pjsua_exe)) is None:
            return f"PJSUA executable was not found: {self.pjsua_exe}"
        return ""

    def configure_call_control(self, mode=None):
        mode = (mode or os.getenv("PJSUA_CALL_CONTROL", "auto_answer")).strip().lower()
        modes = {
            "auto_answer": "200",
            "aa": "200",
            "normal": "200",
            "decline": "603",
            "reject": "603",
            "busy": "486",
        }
        if mode not in modes:
            raise AssertionError("PJSUA call-control mode must be auto_answer, normal, decline, reject, or busy.")
        self.auto_answer_code = os.getenv("PJSUA_AUTO_ANSWER_CODE", modes[mode])
        self.log_action(f"Call control mode configured: {mode} ({self.auto_answer_code})")
        return self

    def configure_account(self, extension, password):
        self.extension = str(extension)
        self.password = str(password)
        if not self.password:
            raise AssertionError("PJSUA password cannot be empty; it must match the created extension password.")
        self.work_dir.mkdir(parents=True, exist_ok=True)
        self.log_action(f"Configure account: extension={self.extension}, password=<same as created extension>")
        return self

    def stop(self):
        if self.process and self.process.poll() is None:
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
        elif self.pid_file.exists():
            try:
                stale_pid = int(self.pid_file.read_text(encoding="utf-8").strip())
                subprocess.run(
                    ["taskkill", "/PID", str(stale_pid), "/T", "/F"],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
            except (OSError, ValueError, subprocess.SubprocessError):
                pass
        self.process = None
        self.pid_file.unlink(missing_ok=True)
        return self

    def restart(self):
        self.stop()
        reason = self.missing_setup_reason()
        if reason:
            raise AssertionError(reason)
        if not self.extension or not self.password:
            raise AssertionError("PJSUA account is not configured before restart.")

        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        self.log_file.write_text("", encoding="utf-8")
        command = self._base_command(
            self.extension,
            self.password,
            local_port=self.local_port,
            log_file=self.log_file,
        )
        command.extend(["--auto-answer", self.auto_answer_code, "--duration", self.auto_hangup_seconds])

        self.log_action(f"Start registered PJSUA on local port {self.local_port}")
        self.process = subprocess.Popen(
            command,
            cwd=str(self.work_dir),
            stdin=subprocess.PIPE,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.STDOUT,
            text=True,
        )
        self.pid_file.write_text(str(self.process.pid), encoding="utf-8")
        time.sleep(3)
        if self.process.poll() is not None:
            output = self.process.stdout.read() if self.process.stdout else ""
            raise AssertionError(f"PJSUA stopped immediately. Output:\n{output}\nLog:\n{self._log_tail()}")
        self.wait_until_registered()
        return self

    def wait_until_registered(self, timeout=30):
        self.log_action(f"Wait up to {timeout}s for SIP registration")
        deadline = time.time() + timeout
        while time.time() < deadline:
            content = self._read_file(self.log_file)
            upper_content = content.upper()
            if "REGISTRATION SUCCESS" in upper_content or "200/REGISTER" in upper_content:
                self.log_action(f"Extension {self.extension} registered successfully")
                return self
            if any(
                marker in upper_content
                for marker in [
                    "REGISTRATION FAILED",
                    "403/REGISTER",
                    "404/REGISTER",
                    "408/REGISTER",
                ]
            ):
                raise AssertionError(
                    f"PJSUA registration was rejected for extension {self.extension}. "
                    f"Log tail:\n{self._log_tail()}"
                )
            if self.process and self.process.poll() is not None:
                output = self.process.stdout.read() if self.process.stdout else ""
                raise AssertionError(
                    f"PJSUA exited before extension {self.extension} registered. "
                    f"Output:\n{output}\nLog:\n{self._log_tail()}"
                )
            time.sleep(0.5)

        raise AssertionError(
            f"Extension {self.extension} did not register with SIP server {self.server} within {timeout}s. "
            f"Log tail:\n{self._log_tail()}"
        )

    def restore_config_backup(self):
        return self.stop()

    def log_marker(self):
        return self.log_file.stat().st_size if self.log_file.exists() else 0

    def read_log_since(self, marker):
        if not self.log_file.exists():
            return ""
        with self.log_file.open("rb") as log_file:
            try:
                log_file.seek(marker)
            except OSError:
                log_file.seek(0)
            return log_file.read().decode("utf-8", errors="ignore")

    def wait_for_incoming_call(self, marker=None, timeout=30):
        marker = self.log_marker() if marker is None else marker
        deadline = time.time() + timeout
        while time.time() < deadline:
            content = self.read_log_since(marker)
            upper_content = content.upper()
            if "INVITE" in upper_content and ("RX" in upper_content or "REQUEST" in upper_content):
                self.log_action("Incoming call reached PJSUA.")
                return self
            if "CALL" in upper_content and ("CONFIRMED" in upper_content or "INCOMING" in upper_content):
                self.log_action("Incoming call reached PJSUA.")
                return self
            if self.process and self.process.poll() is not None:
                output = self.process.stdout.read() if self.process.stdout else ""
                raise AssertionError(f"PJSUA exited before incoming call was detected. Output:\n{output}\nLog:\n{self._log_tail()}")
            time.sleep(1)

        raise AssertionError(f"Incoming call did not reach PJSUA within {timeout}s. Log tail:\n{self._log_tail(marker)}")

    def decline_incoming_call(self):
        self.log_action("End incoming call in PJSUA")
        if self.process and self.process.poll() is None and self.process.stdin:
            try:
                self.process.stdin.write("h\n")
                self.process.stdin.flush()
                time.sleep(2)
            except OSError:
                pass
        return self

    def call_succeeds(self, number=None, extension=None, password=None):
        reason = self.missing_setup_reason()
        if reason:
            raise AssertionError(reason)

        extension = str(extension or self.extension)
        password = str(password or self.password)
        number = str(number or self.call_number)
        if not extension or not password:
            raise AssertionError("PJSUA outgoing call needs extension and password.")

        self.work_dir.mkdir(parents=True, exist_ok=True)
        call_log = self.work_dir / f"pjsua_call_{extension}_{int(time.time())}.log"
        local_port = str(int(self.local_port) + 10)
        command = self._base_command(extension, password, local_port=local_port, log_file=call_log)
        command.extend(["--duration", "8"])
        self.log_action(f"Try outgoing call from extension={extension} to {number}")
        process = subprocess.Popen(
            command,
            cwd=str(self.work_dir),
            stdin=subprocess.PIPE,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.STDOUT,
            text=True,
        )
        try:
            if not self._wait_for_registration_in_log(call_log, process, extension, timeout=20):
                return False

            call_marker = call_log.stat().st_size if call_log.exists() else 0
            process.stdin.write(f"m\nsip:{number}@{self.server}\n")
            process.stdin.flush()

            deadline = time.time() + 15
            while time.time() < deadline:
                content = self._read_file_since(call_log, call_marker).upper()
                success_markers = {
                    "CONFIRMED": "call confirmed",
                    "180/INVITE": "SIP 180 Ringing",
                    "183/INVITE": "SIP 183 Session Progress",
                    "200/INVITE": "SIP 200 OK",
                }
                reached_state = next(
                    (description for marker, description in success_markers.items() if marker in content),
                    None,
                )
                if reached_state:
                    self.log_action(f"Call reached destination: {reached_state}")
                    return True
                if "DISCONNECTED" in content or "CALLING TO DISCONNECTED" in content:
                    return False
                if process.poll() is not None:
                    return False
                time.sleep(0.5)
            return False
        finally:
            if process.poll() is None and process.stdin:
                try:
                    process.stdin.write("h\nq\n")
                    process.stdin.flush()
                    process.wait(timeout=5)
                except (OSError, subprocess.SubprocessError):
                    process.kill()

    def _wait_for_registration_in_log(self, log_file, process, extension, timeout):
        deadline = time.time() + timeout
        while time.time() < deadline:
            content = self._read_file(log_file).upper()
            if "REGISTRATION SUCCESS" in content or "200/REGISTER" in content:
                return True
            if any(marker in content for marker in ["REGISTRATION FAILED", "403/REGISTER", "404/REGISTER"]):
                return False
            if process.poll() is not None:
                return False
            time.sleep(0.5)
        self.log_action(f"Extension {extension} did not register before the outgoing call check")
        return False

    @staticmethod
    def _read_file_since(path, marker):
        if not Path(path).exists():
            return ""
        with Path(path).open("rb") as log_file:
            log_file.seek(marker)
            return log_file.read().decode("utf-8", errors="ignore")
    def _base_command(self, extension, password, local_port, log_file):
        return [
            str(self.pjsua_exe),
            "--null-audio",
            "--no-color",
            "--local-port",
            str(local_port),
            "--id",
            f"sip:{extension}@{self.server}",
            "--registrar",
            f"sip:{self.server}",
            "--realm",
            "*",
            "--username",
            str(extension),
            "--password",
            str(password),
            "--log-file",
            str(log_file),
            "--log-level",
            "5",
            "--app-log-level",
            "4",
        ]

    def _log_tail(self, marker=0, line_count=40):
        content = self.read_log_since(marker)
        return "\n".join(content.splitlines()[-line_count:])

    @staticmethod
    def _read_file(path):
        if not Path(path).exists():
            return ""
        return Path(path).read_text(encoding="utf-8", errors="ignore")
