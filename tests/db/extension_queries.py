def get_extension_numbers(connection):
    cursor = connection.cursor()
    cursor.execute(
        """
        SELECT extension
        FROM extensions
        ORDER BY extension ASC;
        """
    )
    
    return [row[0] for row in cursor.fetchall()]

def get_extension_details_query(extension_number):
    return f"SELECT * FROM extensions WHERE EXTENSION = '{extension_number}';"



