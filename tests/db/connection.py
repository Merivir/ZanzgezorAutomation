import mysql.connector

from tests.config.automation_config import load_config, get_active_client, get_client_config


def get_db_connection():
    config = load_config()
    active_client = get_active_client(config)
    client_config = get_client_config(config, active_client)
    db_config = client_config["database"]

    try:
        connection = mysql.connector.connect(
            host=db_config["host"],
            port=db_config["port"],
            user=db_config["user"],
            password=db_config["password"],
            database=db_config["database"],
        )
        return connection
    except mysql.connector.Error as e:
        print(f"Error connecting to database: {e}")
        return None


if __name__ == "__main__":
    conn = get_db_connection()
    print("Connected successfully" if conn else "Connection failed")
