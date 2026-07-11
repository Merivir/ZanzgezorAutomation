import json
import os
from pathlib import Path


DEFAULT_CONFIG_PATH = Path("tests/config/test_config.json")
CONFIG_PATH_ENV = "TEST_CONFIG_PATH"
CLIENT_ENV = "TEST_CLIENT"


def _set_if_present(container, key, env_name, transform=lambda value: value):
    value = os.getenv(env_name)
    if value is not None:
        container[key] = transform(value)


def _apply_environment_overrides(config):
    active_client = config.get("active_client")
    client_config = config.get("clients", {}).get(active_client)
    if not client_config:
        return

    _set_if_present(client_config, "base_url", "TEST_BASE_URL")

    users = client_config.setdefault("users", {})
    for role, credentials in users.items():
        prefix = f"TEST_{role.upper()}"
        _set_if_present(credentials, "username", f"{prefix}_USERNAME")
        _set_if_present(credentials, "password", f"{prefix}_PASSWORD")

    default_user = users.setdefault("default", {})
    _set_if_present(default_user, "username", "TEST_USERNAME")
    _set_if_present(default_user, "password", "TEST_PASSWORD")

    database = client_config.setdefault("database", {})
    _set_if_present(database, "host", "DB_HOST")
    _set_if_present(database, "port", "DB_PORT", int)
    _set_if_present(database, "database", "DB_NAME")
    _set_if_present(database, "user", "DB_USER")
    _set_if_present(database, "password", "DB_PASSWORD")


def load_config():
    config_path = Path(os.getenv(CONFIG_PATH_ENV, DEFAULT_CONFIG_PATH))
    if not config_path.is_file():
        raise FileNotFoundError(
            f"Test config file was not found: {config_path}. "
            f"Create tests/config/test_config.json or set ${CONFIG_PATH_ENV} to an existing config file."
        )

    with config_path.open(encoding="utf-8") as f:
        config = json.load(f)

    selected_client = os.getenv(CLIENT_ENV)
    if selected_client:
        config["active_client"] = selected_client

    _apply_environment_overrides(config)

    return config
    

def get_user_credentials(config, role):
    """
    Get user credentials for a specific role from the configuration.

    Args:
        config: The configuration dictionary loaded from the JSON file.
        role: The role for which to retrieve credentials (e.g., "admin", "supervisor", "agent").

    Returns:
        A dictionary containing the username, password, and enabled status for the specified role.

    Raises:
        ValueError: If the specified role is not found in the configuration.
    """

    active_client = get_active_client(config)
    client_config = get_client_config(config, active_client)
    
    #taking users from the client configuration and then finding the credentials for the specified role.
    users = client_config.get("users", {})
    if role not in users:
        raise ValueError(f"Role '{role}' not found in configuration.")
    
    credentials = users[role]
    if not credentials.get("username") or not credentials.get("password"):
        raise ValueError(
            f"Credentials for role '{role}' are missing. Set TEST_USERNAME and TEST_PASSWORD "
            "or provide them in your ignored local test_config.json."
        )
    return credentials

def get_active_client(config):
    #taking active client from config and then finding the user credentials for the specified role in the active client configuration.
    active_client = config.get('active_client')
    if not active_client:
        raise ValueError("No active_client specified in configuration.")
    
    return active_client

def get_client_config(config, client_name):
    #taking client configuration for the specified client name from the config.
    client_config = config.get('clients', {}).get(client_name)
    if not client_config:
        raise ValueError(f"Client '{client_name}' not found in configuration.")
    
    return client_config


def get_modules_config(config):  
    active_client = get_active_client(config)
    client_config = get_client_config(config, active_client)
    
    modules_container = client_config.get("modules", {})
    return modules_container

def get_modules_active(config):
    """
    Return the list of active modules for the current active client.

    Args:
        config: The configuration dictionary loaded from the JSON file.

    Returns:
        A list of module keys that are enabled for the active client.

    Raises:
        ValueError: If the active client is missing or invalid.
    """
    modules = get_modules_config(config)
    #take from modules, active modules which are enabled and return the list of active modules.
    active_modules = [module for module, module_container in modules.items() if module_container.get("enabled", False)]
    
    return active_modules

def get_module_active_sections(config, module_name):
    """
    Return the list of active sections for a specific module.

    Args:
        config: The configuration dictionary loaded from the JSON file.
        module_name: The name of the module for which to retrieve active sections. 
    Returns:
        A list of section keys that are enabled for the specified module.           
    Raises:
        ValueError: If the specified module is not found in the configuration.
    """
    modules = get_modules_active(config)
    if module_name not in modules:
        raise ValueError(f"Module '{module_name}' is not active or not found in configuration.")
    
    module_config = get_modules_config(config).get(module_name, {})
    sections = module_config.get("sections", {})

    print(f"Sections for module '{module_name}': {sections}")
    active_sections = [section for section, section_container in sections.items() if section_container]   

    return active_sections
