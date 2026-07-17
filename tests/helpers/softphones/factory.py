import os

from tests.config.automation_config import get_telephony_config, load_config
from tests.helpers.softphones.microsip_client import DEFAULT_MICROSIP_DIR, MicroSIPHelper
from tests.helpers.softphones.pjsua_client import PjsuaClient


def create_softphone_client(provider=None):
    provider = (provider or os.getenv("SOFTPHONE_PROVIDER", "microsip")).strip().lower()
    telephony_config = get_telephony_config(load_config())

    if provider == "microsip":
        return MicroSIPHelper(
            microsip_dir=os.getenv("MICROSIP_DIR", DEFAULT_MICROSIP_DIR),
            server=os.getenv("MICROSIP_SERVER") or telephony_config["sip_server"],
            account_label=os.getenv("MICROSIP_ACCOUNT_LABEL", "Kube-dev"),
            call_number=os.getenv("MICROSIP_CALL_NUMBER") or telephony_config["call_number"],
            check_command=os.getenv("MICROSIP_CHECK_COMMAND"),
            decline_command=os.getenv("MICROSIP_DECLINE_COMMAND"),
            call_control_mode=os.getenv("MICROSIP_CALL_CONTROL", "normal"),
        )

    if provider == "pjsua":
        return PjsuaClient(
            pjsua_exe=os.getenv("PJSUA_EXE"),
            server=os.getenv("PJSUA_SERVER") or os.getenv("MICROSIP_SERVER") or telephony_config["sip_server"],
            local_port=os.getenv("PJSUA_LOCAL_PORT") or telephony_config["local_port"],
            call_number=os.getenv("PJSUA_CALL_NUMBER") or os.getenv("MICROSIP_CALL_NUMBER") or telephony_config["call_number"],
            auto_answer_code=os.getenv("PJSUA_AUTO_ANSWER_CODE", "200"),
            auto_hangup_seconds=os.getenv("PJSUA_AUTO_HANGUP_SECONDS", "3"),
            work_dir=os.getenv("PJSUA_WORK_DIR", "tests/downloads/pjsua"),
        )

    if provider == "3cx":
        raise AssertionError("Softphone provider '3cx' is reserved, but its client implementation is not added yet.")

    raise AssertionError(f"Unsupported softphone provider: {provider}. Use pjsua, microsip, or 3cx.")
