import os
import platform
import shutil
import subprocess
import time
from pathlib import Path

from tests.helpers.softphones.base import SoftphoneClient


class SippClient(SoftphoneClient):
    provider_name = "SIPp"

    def __init__(
        self,
        sipp_exe=None,
        server="10.100.121.30",
        local_ip=None,
        local_port="5062",
        call_number="099452011",
        transport="udp",
        auto_hangup_seconds="3",
        work_dir=None,
    ):
        self.sipp_exe = sipp_exe or os.getenv("SIPP_EXE") or shutil.which("sipp") or self._local_download_path()
        self.server = server
        self.local_ip = local_ip or os.getenv("SIPP_LOCAL_IP", "")
        self.local_port = str(local_port)
        self.call_number = call_number
        self.transport = transport
        self.auto_hangup_seconds = str(auto_hangup_seconds)
        self.work_dir = Path(work_dir or os.getenv("SIPP_WORK_DIR", "tests/downloads/sipp")).resolve()
        self.extension = ""
        self.password = ""
        self.process = None
        self.log_file = self.work_dir / "sipp_messages.log"
        self.scenario_file = self.work_dir / "register_answer_hangup.xml"

    def missing_setup_reason(self):
        if not self.sipp_exe:
            return "SIPp executable is missing. Install SIPp or set SIPP_EXE to the full path of sipp.exe."
        if not Path(self.sipp_exe).exists() and shutil.which(str(self.sipp_exe)) is None:
            return f"SIPp executable was not found: {self.sipp_exe}"
        if platform.system().lower() == "windows" and self._is_elf_binary(self.sipp_exe):
            return (
                f"SIPp file is a Linux ELF binary, not a Windows executable: {self.sipp_exe}. "
                "Use a Windows sipp.exe, install WSL with a Linux distro, or switch provider back to microsip."
            )
        return ""

    @staticmethod
    def _is_elf_binary(path):
        try:
            with open(path, "rb") as binary_file:
                return binary_file.read(4) == b"\x7fELF"
        except OSError:
            return False

    @staticmethod
    def _local_download_path():
        path = Path("tools/sipp/sipp").resolve()
        return str(path) if path.exists() else None

    def configure_call_control(self, mode=None):
        mode = (mode or os.getenv("SIPP_CALL_CONTROL", "auto_answer")).strip().lower()
        if mode not in {"auto_answer", "aa", "normal"}:
            raise AssertionError("SIPp supports auto_answer/normal call-control in this helper.")
        self.log_action(f"Call control mode configured: {mode}")
        return self

    def configure_account(self, extension, password):
        self.extension = str(extension)
        self.password = str(password)
        if not self.password:
            raise AssertionError("SIPp password cannot be empty; it must match the created extension password.")
        self.work_dir.mkdir(parents=True, exist_ok=True)
        self._write_register_answer_scenario()
        self.log_action(f"Configure account: extension={self.extension}, password=<same as created extension>")
        return self

    def stop(self):
        if self.process and self.process.poll() is None:
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
        self.process = None
        return self

    def restart(self):
        self.stop()
        reason = self.missing_setup_reason()
        if reason:
            raise AssertionError(reason)
        if not self.extension or not self.password:
            raise AssertionError("SIPp account is not configured before restart.")

        command = [
            str(self.sipp_exe),
            self.server,
            "-sf",
            str(self.scenario_file),
            "-s",
            self.extension,
            "-au",
            self.extension,
            "-ap",
            self.password,
            "-p",
            self.local_port,
            "-m",
            "1",
            "-trace_msg",
            "-message_file",
            str(self.log_file),
            "-timeout",
            "60000",
        ]
        if self.local_ip:
            command.extend(["-i", self.local_ip])
        if self.transport.lower() == "tcp":
            command.extend(["-t", "t1"])

        self.log_action(f"Start SIPp on local port {self.local_port}, scenario={self.scenario_file}")
        self.process = subprocess.Popen(
            command,
            cwd=str(self.work_dir),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
        time.sleep(2)
        if self.process.poll() is not None:
            output = self.process.stdout.read() if self.process.stdout else ""
            raise AssertionError(f"SIPp stopped immediately. Output:\n{output}")
        return self

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
            content = self.read_log_since(marker).upper()
            if "INVITE SIP:" in content or "REQUEST MSG INVITE" in content:
                self.log_action("Incoming call reached SIPp.")
                return self
            if self.process and self.process.poll() is not None:
                output = self.process.stdout.read() if self.process.stdout else ""
                raise AssertionError(f"SIPp exited before incoming call was detected. Output:\n{output}")
            time.sleep(1)

        tail = "\n".join(self.read_log_since(marker).splitlines()[-30:])
        raise AssertionError(f"Incoming call did not reach SIPp within {timeout}s. SIPp log tail:\n{tail}")

    def decline_incoming_call(self):
        self.log_action("SIPp scenario auto-answers and hangs up; wait for scenario to finish.")
        if self.process:
            try:
                self.process.wait(timeout=int(self.auto_hangup_seconds) + 10)
            except subprocess.TimeoutExpired:
                self.stop()
        return self

    def call_succeeds(self, number=None, extension=None, password=None):
        raise AssertionError(
            "SIPp outgoing call verification is not implemented yet. "
            "Use this provider first for incoming-call tests from the UI."
        )

    def _write_register_answer_scenario(self):
        scenario = f"""<?xml version="1.0" encoding="ISO-8859-1" ?>
<scenario name="Register, answer incoming call, hang up">
  <send retrans="500">
    <![CDATA[
REGISTER sip:[remote_ip] SIP/2.0
Via: SIP/2.0/[transport] [local_ip]:[local_port];branch=[branch]
From: <sip:{self.extension}@[remote_ip]>;tag=[call_number]
To: <sip:{self.extension}@[remote_ip]>
Call-ID: [call_id]
CSeq: 1 REGISTER
Contact: <sip:{self.extension}@[local_ip]:[local_port]>
Max-Forwards: 70
Expires: 300
Content-Length: 0

    ]]>
  </send>

  <recv response="401" auth="true" optional="true" />

  <send retrans="500">
    <![CDATA[
REGISTER sip:[remote_ip] SIP/2.0
Via: SIP/2.0/[transport] [local_ip]:[local_port];branch=[branch]
From: <sip:{self.extension}@[remote_ip]>;tag=[call_number]
To: <sip:{self.extension}@[remote_ip]>
Call-ID: [call_id]
CSeq: 2 REGISTER
Contact: <sip:{self.extension}@[local_ip]:[local_port]>
Max-Forwards: 70
Expires: 300
[authentication username={self.extension} password={self.password}]
Content-Length: 0

    ]]>
  </send>

  <recv response="200" />
  <recv request="INVITE" />

  <send>
    <![CDATA[
SIP/2.0 180 Ringing
[last_Via:]
[last_From:]
[last_To:];tag=[call_number]
[last_Call-ID:]
[last_CSeq:]
Contact: <sip:{self.extension}@[local_ip]:[local_port]>
Content-Length: 0

    ]]>
  </send>

  <send retrans="500">
    <![CDATA[
SIP/2.0 200 OK
[last_Via:]
[last_From:]
[last_To:];tag=[call_number]
[last_Call-ID:]
[last_CSeq:]
Contact: <sip:{self.extension}@[local_ip]:[local_port]>
Content-Type: application/sdp
Content-Length: [len]

v=0
o=user1 53655765 2353687637 IN IP[local_ip_type] [local_ip]
s=-
c=IN IP[media_ip_type] [media_ip]
t=0 0
m=audio [media_port] RTP/AVP 0
a=rtpmap:0 PCMU/8000

    ]]>
  </send>

  <recv request="ACK" optional="true" />
  <pause milliseconds="{int(float(self.auto_hangup_seconds) * 1000)}" />

  <send retrans="500">
    <![CDATA[
BYE sip:[remote_ip]:[remote_port] SIP/2.0
Via: SIP/2.0/[transport] [local_ip]:[local_port];branch=[branch]
[last_From:]
[last_To:]
[last_Call-ID:]
CSeq: 1 BYE
Max-Forwards: 70
Content-Length: 0

    ]]>
  </send>

  <recv response="200" optional="true" />
</scenario>
"""
        self.scenario_file.write_text(scenario, encoding="utf-8")

