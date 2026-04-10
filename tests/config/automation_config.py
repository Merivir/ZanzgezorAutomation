def load_config():
    import json
    with open("tests/config/test_config.json") as f:
        config = json.load(f)    
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
    
    return users[role]

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


def modules_active(config):
    """
    Return the list of active modules for the current active client.

    Args:
        config: The configuration dictionary loaded from the JSON file.

    Returns:
        A list of module keys that are enabled for the active client.

    Raises:
        ValueError: If the active client is missing or invalid.
    """
    active_client = get_active_client(config)
    client_config = get_client_config(config, active_client)
    
    modules = client_config.get("modules", {})
    # Return a list of module names that are active (enabled) for the active client.
    #this takes modules pair, and leaves only those modules where the value is true, meaning they are active, and then returns the list of active module names.
    return [module for module, is_active in modules.items() if is_active]