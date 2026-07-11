def get_extension_numbers(connection):
    cursor = connection.cursor()
    try:
        cursor.execute(
            """
            SELECT extension
            FROM extensions
            ORDER BY extension ASC;
            """
        )
        return [row[0] for row in cursor.fetchall()]
    finally:
        cursor.close()

def get_extension_details_query(extension_number):
    return f"SELECT * FROM extensions WHERE EXTENSION = '{extension_number}';"


def get_existing_extensions(connection, extension_numbers):
    numbers = [str(number) for number in extension_numbers]
    if not numbers:
        return []

    placeholders = ", ".join(["%s"] * len(numbers))
    cursor = connection.cursor()
    try:
        cursor.execute(
            f"SELECT extension FROM extensions WHERE extension IN ({placeholders})",
            tuple(numbers),
        )
        return [str(row[0]) for row in cursor.fetchall()]
    finally:
        cursor.close()



