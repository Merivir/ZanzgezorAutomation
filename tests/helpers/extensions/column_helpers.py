def ensure_extension_columns_visible(extensions_page, expected_minimum=1):
    if extensions_page.visible_table_column_count() < expected_minimum:
        extensions_page.set_all_column_visibility(True)

    column_count = extensions_page.visible_table_column_count()
    assert column_count > 0, "Expected visible table columns before changing column visibility."
    return column_count


def hide_one_extension_column(extensions_page, initial_column_count):
    extensions_page.open_column_visibility_dropdown()
    column_labels = extensions_page.column_visibility_option_labels()
    assert column_labels, "Expected column visibility options."

    for label in reversed(column_labels):
        extensions_page.set_column_option_visibility(label, False)
        extensions_page.wait_for_ui_idle()
        if extensions_page.visible_table_column_count() < initial_column_count:
            return label
        extensions_page.set_column_option_visibility(label, True)

    raise AssertionError(f"Expected at least one column to be hideable. Options were: {column_labels}")


def restore_extension_column(extensions_page, column_label, expected_column_count):
    if column_label:
        extensions_page.set_column_option_visibility(column_label, True)
    extensions_page.wait_for_ui_idle()
    extensions_page.wait_for_visible_table_column_count(expected_column_count)


def close_column_visibility_dropdown(extensions_page):
    extensions_page.close_column_visibility_dropdown()
    extensions_page.wait_for_ui_idle()

def hide_and_restore_one_extension_column(extensions_page, initial_column_count):
    hidden_column = None
    try:
        hidden_column = hide_one_extension_column(extensions_page, initial_column_count)
        restore_extension_column(extensions_page, hidden_column, initial_column_count)
    finally:
        if hidden_column:
            restore_extension_column(extensions_page, hidden_column, initial_column_count)
        close_column_visibility_dropdown(extensions_page)