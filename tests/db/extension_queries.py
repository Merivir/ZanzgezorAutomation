def get_extension_numbers(connection, company_name, extension_type):
    cursor = connection.cursor()
    try:
        cursor.execute(
            """
            SELECT e.extension
            FROM company c
            INNER JOIN extensions e ON c.id = e.company_id
            WHERE e.`type` = %s AND c.name = %s
            ORDER BY e.extension ASC
            """,
            (extension_type, company_name),
        )
        return [row[0] for row in cursor.fetchall()]
    finally:
        cursor.close()


def get_last_extension_number(connection, company_name, extension_type):
    cursor = connection.cursor()
    try:
        cursor.execute(
            """
            SELECT e.extension
            FROM company c
            INNER JOIN extensions e ON c.id = e.company_id
            WHERE e.`type` = %s AND c.name = %s
            ORDER BY e.extension DESC
            LIMIT 1
            """,
            (extension_type, company_name),
        )
        row = cursor.fetchone()
        return row[0] if row else None
    finally:
        cursor.close()


def get_extension_identity(connection, extension_number, company_name, extension_type):
    cursor = connection.cursor()
    try:
        cursor.execute(
            """
            SELECT e.extension, e.real_extension
            FROM company c
            INNER JOIN extensions e ON c.id = e.company_id
            WHERE e.extension = %s AND e.`type` = %s AND c.name = %s
            LIMIT 1
            """,
            (str(extension_number), extension_type, company_name),
        )
        row = cursor.fetchone()
        if not row:
            return None
        extension, real_extension = row
        normalized_real_extension = (
            str(real_extension).strip() if real_extension not in (None, "") else None
        )
        return str(extension), normalized_real_extension
    finally:
        cursor.close()


def get_extension_details_query(extension_number):
    return f"SELECT * FROM extensions WHERE EXTENSION = '{extension_number}';"


def get_existing_extensions(connection, extension_numbers, company_name, extension_type):
    numbers = [str(number) for number in extension_numbers]
    if not numbers:
        return []

    placeholders = ", ".join(["%s"] * len(numbers))
    cursor = connection.cursor()
    try:
        cursor.execute(
            f"""
            SELECT e.extension
            FROM company c
            INNER JOIN extensions e ON c.id = e.company_id
            WHERE e.extension IN ({placeholders}) AND e.`type` = %s AND c.name = %s
            """,
            (*numbers, extension_type, company_name),
        )
        return [str(row[0]) for row in cursor.fetchall()]
    finally:
        cursor.close()


def delete_extensions(connection, extension_numbers, company_name, extension_type):
    numbers = [str(number) for number in extension_numbers]
    if not numbers:
        return 0

    placeholders = ", ".join(["%s"] * len(numbers))
    cursor = connection.cursor()
    try:
        cursor.execute(
            f"""
            DELETE e
            FROM extensions e
            INNER JOIN company c ON c.id = e.company_id
            WHERE e.extension IN ({placeholders}) AND e.`type` = %s AND c.name = %s
            """,
            (*numbers, extension_type, company_name),
        )
        connection.commit()
        return cursor.rowcount
    except Exception:
        connection.rollback()
        raise
    finally:
        cursor.close()
