MODULE_LABELS = {
    "dashboard": "Dashboard",
    "agents": "Agents",
    "records": "Records",
    "reports": "Reports",
    "chat": "Chat",
    "general_info": "General Info",
    "callback_info": "Callback Info",
    "crm": "CRM",
    "campaign": "Campaign",
    "administration": "Administration",
    "knowledge_base": "Knowledge base",
}


def _parse_module_list(value: str) -> set[str]:
    return {item.strip().lower() for item in value.split(",") if item.strip()}


def is_module_enabled(module_flags: dict, module_key: str) -> bool:
    return bool(module_flags.get(module_key, True))


def get_effective_module_flags(module_flags: dict, only_modules: str = "", skip_modules: str = "") -> dict:
    effective = {key: bool(value) for key, value in module_flags.items()}
    known_keys = set(MODULE_LABELS) | set(effective)

    only_set = _parse_module_list(only_modules)
    skip_set = _parse_module_list(skip_modules)

    if only_set:
        for key in known_keys:
            effective[key] = key in only_set

    for key in skip_set:
        effective[key] = False

    return effective
