import csv
import time

import pytest


def wait_for_csv_download(download_dir, timeout=20):
    deadline = time.time() + timeout
    while time.time() < deadline:
        csv_files = list(download_dir.glob("*.csv"))
        active_downloads = list(download_dir.glob("*.crdownload"))
        if csv_files and not active_downloads:
            return max(csv_files, key=lambda path: path.stat().st_mtime)
        time.sleep(1)

    pytest.fail(f"No CSV file was downloaded to {download_dir}.")


def read_csv_rows(csv_path):
    content = csv_path.read_text(encoding="utf-8-sig").strip()
    assert content not in {"501", "505"}, f"Export returned server error status in CSV file: {content}"
    assert not content.startswith(("501", "505")), f"Export returned server error instead of table data: {content[:120]}"
    assert '"status":5' not in content, f"Export returned server error response instead of CSV table data: {content[:120]}"

    sample = content[:1024]
    try:
        dialect = csv.Sniffer().sniff(sample)
    except csv.Error:
        dialect = csv.excel

    return list(csv.reader(content.splitlines(), dialect))


def normalize_csv_cell(value):
    return str(value or "").strip().lstrip("\ufeff").strip('"')


def column_values(rows, column_name):
    header = [normalize_csv_cell(cell) for cell in rows[0]]
    column_index = header.index(column_name)
    return [normalize_csv_cell(row[column_index]) for row in rows[1:] if len(row) > column_index]


def csv_records(rows):
    header = [normalize_csv_cell(cell) for cell in rows[0]]
    return [dict(zip(header, [normalize_csv_cell(cell) for cell in row])) for row in rows[1:]]


def records_by_column(records, column_name):
    return {record[column_name]: record for record in records if record.get(column_name)}


def normalize_record_value(value):
    return normalize_csv_cell(value)