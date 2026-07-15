from tests.helpers.extensions.csv_helpers import (
    column_values,
    normalize_csv_cell,
    normalize_record_value,
    records_by_column,
)

EXPECTED_EXPORT_COLUMNS = ["Extension", "Real Extension", "Password", "Type", "Transport Type", "Status"]
EXPORT_COLUMN_ALIASES = {
    "Extension": "Extension",
    "Real Extension": "Real Extension",
    "Password": "Password",
    "Type": "Type",
    "Transport type": "Transport Type",
    "Transport Type": "Transport Type",
    "Status": "Status",
}


def assert_export_has_expected_columns(rows):
    header = [normalize_csv_cell(cell) for cell in rows[0]]
    missing_columns = [column for column in EXPECTED_EXPORT_COLUMNS if column not in header]
    assert not missing_columns, f"Exported CSV is missing columns: {missing_columns}. Header was: {header}"


def assert_export_contains_extension(rows, extension_number):
    exported_extensions = column_values(rows, "Extension")
    assert str(extension_number) in exported_extensions, (
        f"Expected existing extension '{extension_number}' to appear in exported CSV. "
        f"Exported extensions included: {exported_extensions[:10]}"
    )


def assert_export_has_real_extension_values(rows):
    real_extensions = column_values(rows, "Real Extension")
    assert any(real_extensions), "Expected exported CSV to contain at least one Real Extension value."


def assert_export_contains_table_records(table_records, exported_records):
    exported_by_extension = records_by_column(exported_records, "Extension")
    missing_extensions = [
        record["Extension"]
        for record in table_records
        if record.get("Extension") not in exported_by_extension
    ]
    assert not missing_extensions, (
        "Exported CSV is missing extensions visible across paginated table pages: "
        f"{missing_extensions[:10]}"
    )

    for table_record in table_records:
        exported_record = exported_by_extension[table_record["Extension"]]
        for table_column, export_column in EXPORT_COLUMN_ALIASES.items():
            if table_column not in table_record or export_column not in exported_record:
                continue
            assert normalize_record_value(table_record[table_column]) == normalize_record_value(exported_record[export_column]), (
                f"Exported value mismatch for extension {table_record['Extension']} column {export_column}. "
                f"Table value: {table_record[table_column]!r}; CSV value: {exported_record[export_column]!r}"
            )