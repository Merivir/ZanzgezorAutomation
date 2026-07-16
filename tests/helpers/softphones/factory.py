import os

from tests.helpers.softphones.microsip_client import DEFAULT_MICROSIP_DIR, MicroSIPHelper
from tests.helpers.softphones.pjsua_client import PjsuaClient
from tests.helpers.softphones.sipp_client import SippClient


def create_softphone_client(provider=None):
    provider = (provider or os.getenv("SOFTPHONE_PROVIDER", "microsip")).strip().lower()

    if provider == "microsip":
        return MicroSIPHelper(
            microsip_dir=os.getenv("MICROSIP_DIR", DEFAULT_MICROSIP_DIR),
            server=os.getenv("MICROSIP_SERVER", "10.100.121.30"),
            account_label=os.getenv("MICROSIP_ACCOUNT_LABEL", "Kube-dev"),
            call_number=os.getenv("MICROSIP_CALL_NUMBER", "099452011"),
            check_command=os.getenv("MICROSIP_CHECK_COMMAND"),
            decline_command=os.getenv("MICROSIP_DECLINE_COMMAND"),
            call_control_mode=os.getenv("MICROSIP_CALL_CONTROL", "normal"),
        )

    if provider == "sipp":
        return SippClient(
            sipp_exe=os.getenv("SIPP_EXE"),
            server=os.getenv("SIPP_SERVER") or os.getenv("MICROSIP_SERVER", "10.100.121.30"),
            local_ip=os.getenv("SIPP_LOCAL_IP", ""),
            local_port=os.getenv("SIPP_LOCAL_PORT", "5062"),
            call_number=os.getenv("SIPP_CALL_NUMBER") or os.getenv("MICROSIP_CALL_NUMBER", "099452011"),
            transport=os.getenv("SIPP_TRANSPORT", "udp"),
            auto_hangup_seconds=os.getenv("SIPP_AUTO_HANGUP_SECONDS", "3"),
            work_dir=os.getenv("SIPP_WORK_DIR", "tests/downloads/sipp"),
        )

    if provider == "pjsua":
        return PjsuaClient(
            pjsua_exe=os.getenv("PJSUA_EXE"),
            server=os.getenv("PJSUA_SERVER") or os.getenv("MICROSIP_SERVER", "10.100.121.30"),
            local_port=os.getenv("PJSUA_LOCAL_PORT", "5062"),
            call_number=os.getenv("PJSUA_CALL_NUMBER") or os.getenv("MICROSIP_CALL_NUMBER", "099452011"),
            auto_answer_code=os.getenv("PJSUA_AUTO_ANSWER_CODE", "200"),
            auto_hangup_seconds=os.getenv("PJSUA_AUTO_HANGUP_SECONDS", "3"),
            work_dir=os.getenv("PJSUA_WORK_DIR", "tests/downloads/pjsua"),
        )

    if provider == "3cx":
        raise AssertionError("Softphone provider '3cx' is reserved, but its client implementation is not added yet.")

    raise AssertionError(f"Unsupported softphone provider: {provider}. Use microsip, sipp, pjsua, or 3cx.")
