import mysql.connector

from tests.config.automation_config import load_config, get_active_client, get_client_config


def get_db_connection():
    config = load_config()
    active_client = get_active_client(config)
    client_config = get_client_config(config, active_client)
    db_config = client_config["database"]

    required = ("host", "port", "user", "password", "database")
    missing = [key for key in required if not db_config.get(key)]
    if missing:
        raise ValueError(
            f"Missing database configuration: {', '.join(missing)}. "
            "Set DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, and DB_NAME."
        )

    return mysql.connector.connect(
        host=db_config["host"],
        port=db_config["port"],
        user=db_config["user"],
        password=db_config["password"],
        database=db_config["database"],
    )


if __name__ == "__main__":
    conn = get_db_connection()
    try:
        print("Connected successfully")
    finally:
        conn.close()
