import time

from tests.helpers.extensions.assertions import (
    assert_export_contains_extension,
    assert_export_contains_table_records,
    assert_export_has_expected_columns,
    assert_export_has_real_extension_values,
)
from tests.helpers.extensions.csv_helpers import csv_records, read_csv_rows, wait_for_csv_download
from tests.helpers.extensions.data_helpers import extensions_remaining_in_database
from tests.helpers.test_steps import test_step


def search_extension_and_get_rows(extensions_page, extension_number):
    extensions_page.search_for_extension_number(extension_number)
    extensions_page.wait_for_ui_idle()
    return extensions_page.visible_table_rows()


def clear_search_and_get_rows(extensions_page):
    extensions_page.search_for_extension_number("")
    extensions_page.wait_for_ui_idle()
    return extensions_page.visible_table_rows()


def clear_filters_and_get_rows(extensions_page):
    extensions_page.clear_search_and_submit()
    extensions_page.wait_for_ui_idle()
    return extensions_page.visible_table_rows()


def export_extensions_and_read_rows(extensions_page, download_dir, read_csv_rows, wait_for_csv_download):
    extensions_page.export_extensions()
    extensions_page.wait_for_ui_idle()
    csv_path = wait_for_csv_download(download_dir)
    return read_csv_rows(csv_path)


def collect_table_records_from_all_pages(extensions_page):
    records = extensions_page.all_visible_table_records()
    extensions_page.wait_for_ui_idle()
    if not records:
        debug_snapshot = extensions_page.format_table_debug_snapshot()
        extensions_page.log_action(f"No table records collected. Table state: {debug_snapshot}")
        assert records, f"Expected visible table records before export. Table state: {debug_snapshot}"
    return records


def open_edit_popup_for_first_extension(extensions_page):
    extensions_page.go_to_first_page()
    extensions_page.wait_for_ui_idle()
    first_row_text = extensions_page.first_visible_table_row_text()
    assert first_row_text, "Expected at least one extension row before opening Edit popup."
    extensions_page.open_first_row_edit_popup()
    extensions_page.wait_for_ui_idle()
    return first_row_text


def assert_edit_popup_matches_row(extensions_page, row_text):
    assert extensions_page.is_add_popup_open(), "Edit popup did not open."
    popup_values = extensions_page.popup_field_values()
    assert popup_values, "Expected Edit popup to show existing record values."

    popup_password = extensions_page.edit_popup_password_value()
    assert popup_password in row_text, (
        f"Edit popup Password value is not visible in the selected table row. "
        f"Popup value: {popup_password!r}; row text: {row_text!r}"
    )

    popup_type = extensions_page.edit_popup_type_value()
    assert popup_type in row_text, (
        f"Edit popup Type value is not visible in the selected table row. "
        f"Popup value: {popup_type!r}; row text: {row_text!r}"
    )

    popup_transport_type = extensions_page.edit_popup_transport_type_value()
    assert popup_transport_type in row_text, (
        f"Edit popup Transport type value is not visible in the selected table row. "
        f"Popup value: {popup_transport_type!r}; row text: {row_text!r}"
    )


def close_add_popup_if_open(extensions_page):
    extensions_page.wait_for_ui_idle()
    if extensions_page.is_add_popup_open():
        extensions_page.close_add_popup()


def open_add_popup_and_assert_controls(extensions_page):
    extensions_page.open_add_popup()
    assert extensions_page.has_add_popup_controls(), "Not all Add popup controls are visible."


def trigger_add_required_validation(extensions_page):
    extensions_page.log_action("Testing Add popup required-fields validation")
    extensions_page.open_add_popup()
    extensions_page.touch_add_popup_required_fields()
    extensions_page.wait_for_ui_idle()
    extensions_page.log_action("Finished touching required fields")


def assert_add_required_validation(extensions_page):
    required_labels = ["Password", "Type", "Transport"]
    extensions_page.log_action("Verify Submit is disabled while required fields are empty")
    assert extensions_page.is_add_popup_submit_disabled(), "Submit should be disabled when required Add fields are empty."

    extensions_page.wait_for_ui_idle()
    extensions_page.log_action("Verify empty required fields did not receive values")
    assert extensions_page.add_popup_number_fields_are_empty(), "Start and End should stay empty while required validation is shown."

    extensions_page.log_action("Check whether validation messages or invalid states are visible")
    extensions_page.log_add_popup_required_validation_state(required_labels)


def open_add_popup_with_password_visible(extensions_page):
    extensions_page.clear_search_and_submit()
    extensions_page.wait_for_ui_idle()
    extensions_page.open_add_popup()
    extensions_page.wait_for_ui_idle()
    assert extensions_page.is_add_popup_open(), "Add popup did not open."
    assert extensions_page.is_add_popup_password_visible(), "Password field should be visible before Generate Password is checked."


def enable_generated_password_in_add_popup(extensions_page):
    extensions_page.toggle_add_popup_generate_password()
    extensions_page.wait_for_ui_idle()
    assert not extensions_page.is_add_popup_password_visible(), "Password field should be hidden after Generate Password is checked."


def open_mobile_popup_for_first_extension(extensions_page):
    extensions_page.clear_search_and_submit()
    extensions_page.wait_for_ui_idle()
    extensions_page.go_to_first_page()
    extensions_page.wait_for_ui_idle()
    extensions_page.open_first_row_mobile_popup()
    extensions_page.wait_for_ui_idle()


def assert_mobile_popup_controls(extensions_page):
    assert extensions_page.is_mobile_popup_open(), "Mobile popup did not open."
    assert extensions_page.has_mobile_popup_controls(), "Not all Mobile popup controls are visible."


def close_mobile_popup_if_open(extensions_page):
    extensions_page.wait_for_ui_idle()
    extensions_page.close_mobile_popup()


def navigate_to_next_page_and_back(extensions_page):
    extensions_page.clear_search_and_submit()
    extensions_page.wait_for_ui_idle()
    extensions_page.go_to_first_page()
    extensions_page.wait_for_ui_idle()

    first_page_number = extensions_page.current_page_number()
    first_page_records = extensions_page.visible_table_records()
    assert first_page_records, "Expected records on the first page before testing pagination."

    return first_page_number, first_page_records


def assert_next_page_changes_records(extensions_page, first_page_number, first_page_records, pytest_module):
    if not extensions_page.go_to_next_page():
        pytest_module.skip("Only one Extensions page is available; pagination navigation cannot be verified.")
    extensions_page.wait_for_ui_idle()

    second_page_number = extensions_page.current_page_number()
    second_page_records = extensions_page.visible_table_records()
    assert second_page_records, "Expected records on the next page after pagination."
    assert second_page_number != first_page_number or second_page_records != first_page_records, (
        "Expected paginator to move to another page or show different records."
    )


def return_to_previous_page(extensions_page, expected_page_number):
    assert extensions_page.go_to_previous_page(), "Expected Previous Page to be available after moving forward."
    extensions_page.wait_for_ui_idle()
    assert extensions_page.current_page_number() == expected_page_number, "Expected paginator to return to the first page."


def publish_changes_and_assert_page_loaded(extensions_page):
    extensions_page.clear_search_and_submit()
    extensions_page.wait_for_ui_idle()
    extensions_page.publish_changes()
    extensions_page.wait_for_ui_idle()
    assert extensions_page.is_loaded(), "Extensions page did not remain loaded after publishing changes."


def assert_extension_is_visible(extensions_page, extension_number, context):
    assert extensions_page.has_visible_extension(extension_number), (
        f"Expected extension '{extension_number}' to be visible {context}."
    )


def assert_extension_record_is_visible(extensions_page, extension_number, context):
    record = extensions_page.visible_record_for_extension(extension_number)
    assert record and record["Extension"] == str(extension_number), (
        f"Expected extension '{extension_number}' {context}, got: {record}"
    )
    return record


def generate_new_password_in_edit_popup(extensions_page, extension_number):
    assert_extension_record_is_visible(extensions_page, extension_number, "before editing")
    extensions_page.open_extension_edit_popup(extension_number)
    extensions_page.wait_for_ui_idle()

    try:
        assert extensions_page.is_add_popup_open(), "Edit popup did not open."
        old_password = extensions_page.edit_popup_password_value()
        assert extensions_page.is_edit_popup_password_visible(), (
            "Password field should be visible before Generate Password is checked."
        )

        extensions_page.toggle_edit_popup_generate_password()
        extensions_page.wait_for_ui_idle()
        assert not extensions_page.is_edit_popup_password_visible(), (
            "Password field should be hidden after Generate Password is checked."
        )

        extensions_page.submit_edit_popup()
        extensions_page.wait_for_ui_idle()
    finally:
        close_add_popup_if_open(extensions_page)

    return old_password


def assert_generated_password_was_saved(extensions_page, extension_number, old_password):
    extensions_page.reveal_extensions_descending([extension_number])
    extensions_page.open_extension_edit_popup(extension_number)
    extensions_page.wait_for_ui_idle()

    try:
        generated_password = extensions_page.edit_popup_password_value()
        assert generated_password, "Expected generated password to be visible after reopening Edit popup."
        assert generated_password != old_password, (
            f"Expected generated password to differ from old password {old_password!r}, got {generated_password!r}."
        )
    finally:
        close_add_popup_if_open(extensions_page)


def edit_extension_and_save_changes(extensions_page, extension_number):
    assert_extension_record_is_visible(extensions_page, extension_number, "before editing")
    extensions_page.open_extension_edit_popup(extension_number)
    extensions_page.wait_for_ui_idle()

    try:
        assert extensions_page.is_add_popup_open(), "Edit popup did not open."
        original_password = extensions_page.edit_popup_password_value()
        updated_password = f"{original_password}!"

        updated_type = extensions_page.choose_different_extension_type()
        extensions_page.wait_for_ui_idle()
        updated_transport_type = extensions_page.choose_different_transport_type()
        extensions_page.wait_for_ui_idle()
        extensions_page.set_edit_popup_password(updated_password)
        extensions_page.wait_for_ui_idle()

        extensions_page.submit_edit_popup()
        extensions_page.wait_for_ui_idle()
    finally:
        close_add_popup_if_open(extensions_page)

    return updated_password, updated_type, updated_transport_type


def assert_saved_extension_changes_are_visible(
    extensions_page,
    extension_number,
    updated_password,
    updated_type,
    updated_transport_type,
):
    extensions_page.reveal_extensions_descending([extension_number])
    updated_record = assert_extension_record_is_visible(extensions_page, extension_number, "after saving Edit")

    assert updated_record["Type"] == updated_type, (
        f"Type was not updated in table. Expected {updated_type!r}, got {updated_record['Type']!r}."
    )
    assert updated_record["Transport type"] == updated_transport_type, (
        "Transport type was not updated in table. "
        f"Expected {updated_transport_type!r}, got {updated_record['Transport type']!r}."
    )

    extensions_page.open_extension_edit_popup(extension_number)
    extensions_page.wait_for_ui_idle()
    try:
        saved_password = extensions_page.edit_popup_password_value()
        assert saved_password == updated_password, (
            f"Password was not updated in Edit popup. Expected {updated_password!r}, got {saved_password!r}."
        )
    finally:
        close_add_popup_if_open(extensions_page)


def change_extension_values_and_cancel(extensions_page, extension_number):
    original_record = assert_extension_record_is_visible(extensions_page, extension_number, "before editing")
    extensions_page.open_extension_edit_popup(extension_number)
    extensions_page.wait_for_ui_idle()

    try:
        assert extensions_page.is_add_popup_open(), "Edit popup did not open."
        original_password = extensions_page.edit_popup_password_value()
        assert original_password, "Expected existing Password value before testing Cancel."

        extensions_page.choose_different_extension_type()
        extensions_page.wait_for_ui_idle()
        extensions_page.choose_different_transport_type()
        extensions_page.wait_for_ui_idle()
        extensions_page.set_edit_popup_password(f"Cancel{int(time.time())}")
        extensions_page.wait_for_ui_idle()
        extensions_page.close_add_popup()
        extensions_page.wait_for_ui_idle()
    finally:
        close_add_popup_if_open(extensions_page)

    return original_record, original_password


def assert_cancelled_extension_changes_were_not_saved(
    extensions_page,
    extension_number,
    original_record,
    original_password,
):
    extensions_page.reveal_extensions_descending([extension_number])
    current_record = assert_extension_record_is_visible(extensions_page, extension_number, "after cancelling Edit")

    assert current_record["Type"] == original_record["Type"], (
        f"Type changed after Cancel. Expected {original_record['Type']!r}, got {current_record['Type']!r}."
    )
    assert current_record["Transport type"] == original_record["Transport type"], (
        "Transport type changed after Cancel. "
        f"Expected {original_record['Transport type']!r}, got {current_record['Transport type']!r}."
    )

    extensions_page.open_extension_edit_popup(extension_number)
    extensions_page.wait_for_ui_idle()
    try:
        current_password = extensions_page.edit_popup_password_value()
        assert current_password == original_password, (
            f"Password changed after Cancel. Expected {original_password!r}, got {current_password!r}."
        )
    finally:
        close_add_popup_if_open(extensions_page)


def cancel_row_delete_and_assert_record_remains(extensions_page, extension_number):
    assert_extension_is_visible(extensions_page, extension_number, "before opening row delete confirmation")
    extensions_page.open_extension_delete_confirmation(extension_number).cancel_delete_confirmation()

    try:
        assert not extensions_page.is_delete_confirmation_open(), "Row delete confirmation should be closed after Reject."
    finally:
        if extensions_page.is_delete_confirmation_open():
            extensions_page.cancel_delete_confirmation()

    assert_extension_is_visible(extensions_page, extension_number, "after cancelling row delete")
    extensions_page.reveal_extensions_descending([extension_number])


def delete_row_and_assert_record_is_removed(extensions_page, extension_number, remaining_extensions_lookup):
    assert_extension_is_visible(extensions_page, extension_number, "before row delete")

    extensions_page.open_extension_delete_confirmation(extension_number)
    extensions_page.wait_for_ui_idle()
    assert extensions_page.is_delete_confirmation_open(), "Row delete confirmation did not open."
    extensions_page.confirm_delete_confirmation()
    extensions_page.wait_for_success_notification()
    extensions_page.wait_for_ui_idle()

    assert not extensions_page.has_visible_extension(extension_number), (
        f"Deleted extension '{extension_number}' is still visible after row delete."
    )
    assert not remaining_extensions_lookup([extension_number]), (
        f"Deleted extension '{extension_number}' still exists in the database."
    )


def open_bottom_delete_popup_and_assert_fields(extensions_page):
    extensions_page.open_bottom_delete_popup()
    extensions_page.wait_for_ui_idle()
    try:
        assert extensions_page.is_add_popup_open(), "Bottom delete range popup did not open."
        assert extensions_page.add_popup_number_fields_are_empty(), (
            "Bottom delete range fields should be empty when the popup opens."
        )
    finally:
        close_add_popup_if_open(extensions_page)


def assert_extension_range_is_visible(extensions_page, start_extension, end_extension, context):
    extension_range = range(int(start_extension), int(end_extension) + 1)
    extensions_page.reveal_extensions_descending(extension_range)
    assert_extension_is_visible(extensions_page, start_extension, context)
    assert_extension_is_visible(extensions_page, end_extension, context)


def cancel_bottom_delete_and_assert_range_remains(extensions_page, start_extension, end_extension):
    extensions_page.open_bottom_delete_popup()
    extensions_page.wait_for_ui_idle()
    try:
        assert extensions_page.is_add_popup_open(), "Bottom delete range popup did not open."
        extensions_page.fill_add_popup(start_extension, end_extension)
        extensions_page.wait_for_ui_idle()
        extensions_page.close_add_popup()
        extensions_page.wait_for_ui_idle()
    finally:
        close_add_popup_if_open(extensions_page)

    assert_extension_range_is_visible(
        extensions_page,
        start_extension,
        end_extension,
        "after cancelling bottom delete",
    )


def delete_bottom_range_and_assert_removed(
    extensions_page,
    start_extension,
    end_extension,
    remaining_extensions_lookup,
):
    extensions_page.open_bottom_delete_popup()
    extensions_page.wait_for_ui_idle()
    try:
        assert extensions_page.is_add_popup_open(), "Bottom delete range popup did not open."
        extensions_page.fill_add_popup(start_extension, end_extension)
        extensions_page.wait_for_ui_idle()
        extensions_page.submit_add_popup(wait_until_closed=True)
        if extensions_page.is_delete_confirmation_open():
            extensions_page.confirm_delete_confirmation()
        extensions_page.wait_for_success_notification()
        extensions_page.wait_for_ui_idle()
    finally:
        close_add_popup_if_open(extensions_page)

    deleted_range = list(range(int(start_extension), int(end_extension) + 1))
    for extension_number in deleted_range:
        assert not extensions_page.has_visible_extension(extension_number), (
            f"Extension '{extension_number}' is still visible after bottom delete range removal."
        )
    remaining = remaining_extensions_lookup(deleted_range)
    assert not remaining, f"Range deletion left extensions in the database: {remaining}"


def assert_created_extension_is_visible(extensions_page, extension_number):
    assert_extension_is_visible(extensions_page, extension_number, "after adding it")


def assert_created_extension_range_exists(start_extension, end_extension):
    assert start_extension and end_extension, "Expected disposable extension range to be created."



def create_unpublished_extension(extensions_page, extension_number, password):
    extensions_page.create_extension(extension_number=extension_number, password=password)


def configure_microsip_account(microsip, extension_number, password):
    microsip.configure_account(extension=extension_number, password=password).restart()


def check_microsip_call_succeeds(microsip, extension_number, password):
    succeeded = microsip.call_succeeds(extension=extension_number, password=password)
    microsip.log_action(f"Outgoing call result: {'SUCCEEDED' if succeeded else 'DECLINED'}")
    return succeeded


def assert_microsip_call_is_declined(microsip, extension_number, password, message):
    assert microsip.call_is_declined(extension=extension_number, password=password), message


def assert_microsip_call_succeeds(microsip, extension_number, password, message):
    assert microsip.call_succeeds(extension=extension_number, password=password), message


def delete_extension_and_publish(extensions_page, extension_number):
    extensions_page.delete_extension_if_exists(extension_number)
    extensions_page.publish_changes()
    extensions_page.wait_for_ui_idle()
    remaining = extensions_remaining_in_database([extension_number])
    assert not remaining, f"Extension remained in the database after UI delete and Publish: {remaining}"


def call_number_from_softphone(softphone_page, extension_number, call_number, microsip=None):
    incoming_call_marker = microsip.log_marker() if microsip else None
    softphone_page.switch_to_call_tab().select_online_extension(extension_number).call_number(call_number)
    if microsip:
        microsip.wait_for_incoming_call(incoming_call_marker).decline_incoming_call()


def assert_search_field_is_empty(extensions_page):
    search_value = extensions_page.driver.find_element(*extensions_page.SEARCH_INPUT).get_attribute("value")
    assert search_value == "", "Expected search field to be empty after clearing filters."


def assert_search_has_no_results(extensions_page, extension_number, expected_conditions):
    extensions_page.search_for_extension_number(extension_number)
    assert extensions_page.wait.until(
        expected_conditions.text_to_be_present_in_element(
            extensions_page.EMPTY_TABLE_MESSAGE,
            "No data to display!",
        )
    )

def verify_matching_extension_is_displayed(extensions_page, extension_number):
    search_extension_and_get_rows(extensions_page, extension_number)
    assert_extension_record_is_visible(extensions_page, extension_number, "after searching")


def verify_full_extension_list_is_displayed(extensions_page):
    rows = clear_search_and_get_rows(extensions_page)
    assert rows, "Expected full extension list to be displayed after empty search."


def verify_filters_are_cleared_and_full_list_is_displayed(extensions_page, extension_number):
    search_extension_and_get_rows(extensions_page, extension_number)
    rows = clear_filters_and_get_rows(extensions_page)
    assert_search_field_is_empty(extensions_page)
    assert rows, "Expected full extension list to be displayed after clearing filters."


def verify_export_download_contains_expected_columns_and_data(extensions_page, download_dir, extension_number):
    rows = export_extensions_and_read_rows(extensions_page, download_dir, read_csv_rows, wait_for_csv_download)
    assert len(rows) > 1, f"Expected exported CSV to contain header and table data, got: {rows}"
    assert_export_has_expected_columns(rows)
    assert_export_contains_extension(rows, extension_number)
    assert_export_has_real_extension_values(rows)


def verify_export_contains_records_from_all_pages(extensions_page, download_dir):
    table_records = collect_table_records_from_all_pages(extensions_page)
    rows = export_extensions_and_read_rows(extensions_page, download_dir, read_csv_rows, wait_for_csv_download)
    exported_records = csv_records(rows)
    assert_export_contains_table_records(table_records, exported_records)


def verify_edit_popup_is_populated_with_existing_data(extensions_page):
    first_row_text = open_edit_popup_for_first_extension(extensions_page)
    try:
        assert_edit_popup_matches_row(extensions_page, first_row_text)
    finally:
        close_add_popup_if_open(extensions_page)


def verify_generated_password_is_saved_after_edit(extensions_page, extension_number):
    old_password = generate_new_password_in_edit_popup(extensions_page, extension_number)
    assert_generated_password_was_saved(extensions_page, extension_number, old_password)


def verify_edited_values_are_saved(extensions_page, extension_number):
    updated_password, updated_type, updated_transport_type = edit_extension_and_save_changes(
        extensions_page,
        extension_number,
    )
    assert_saved_extension_changes_are_visible(
        extensions_page,
        extension_number,
        updated_password,
        updated_type,
        updated_transport_type,
    )


def verify_edit_cancel_discards_changes(extensions_page, extension_number):
    original_record, original_password = change_extension_values_and_cancel(extensions_page, extension_number)
    assert_cancelled_extension_changes_were_not_saved(
        extensions_page,
        extension_number,
        original_record,
        original_password,
    )


def verify_add_popup_shows_required_controls(extensions_page):
    try:
        open_add_popup_and_assert_controls(extensions_page)
    finally:
        close_add_popup_if_open(extensions_page)


def verify_add_required_validation_prevents_saving(extensions_page):
    try:
        trigger_add_required_validation(extensions_page)
        assert_add_required_validation(extensions_page)
    finally:
        close_add_popup_if_open(extensions_page)


def verify_add_generate_password_toggles_password_field(extensions_page):
    try:
        open_add_popup_with_password_visible(extensions_page)
        enable_generated_password_in_add_popup(extensions_page)
    finally:
        close_add_popup_if_open(extensions_page)


def verify_extension_created_successfully(extensions_page, extension_number):
    assert_created_extension_is_visible(extensions_page, extension_number)


def verify_extension_range_created_successfully(start_extension, end_extension):
    assert_created_extension_range_exists(start_extension, end_extension)


def verify_mobile_popup_opens_with_required_controls(extensions_page):
    try:
        open_mobile_popup_for_first_extension(extensions_page)
        assert_mobile_popup_controls(extensions_page)
    finally:
        close_mobile_popup_if_open(extensions_page)


def verify_pagination_next_and_previous_work(extensions_page, pytest_module):
    first_page_number, first_page_records = navigate_to_next_page_and_back(extensions_page)
    assert_next_page_changes_records(extensions_page, first_page_number, first_page_records, pytest_module)
    return_to_previous_page(extensions_page, first_page_number)


def verify_pending_changes_are_published(extensions_page):
    publish_changes_and_assert_page_loaded(extensions_page)



def verify_call_extension_password_edit_is_saved(extensions_page, extension_number):
    assert_extension_record_is_visible(extensions_page, extension_number, "before call setup edit")
    extensions_page.open_extension_edit_popup(extension_number)
    extensions_page.wait_for_ui_idle()

    try:
        assert extensions_page.is_add_popup_open(), "Edit popup did not open."
        original_password = extensions_page.edit_popup_password_value()
        updated_password = f"{original_password}!"
        extensions_page.set_edit_popup_password(updated_password)
        extensions_page.wait_for_ui_idle()
        extensions_page.submit_edit_popup()
        extensions_page.wait_for_ui_idle()
    finally:
        close_add_popup_if_open(extensions_page)

    extensions_page.open_extension_edit_popup(extension_number)
    extensions_page.wait_for_ui_idle()
    try:
        saved_password = extensions_page.edit_popup_password_value()
        assert saved_password == updated_password, (
            f"Password was not saved before SIP call verification. "
            f"Expected {updated_password!r}, got {saved_password!r}."
        )
    finally:
        close_add_popup_if_open(extensions_page)

    return updated_password

def verify_deleted_extension_cannot_call(microsip, sip_extension, password):
    call_after_delete = check_microsip_call_succeeds(microsip, sip_extension, password)
    assert not call_after_delete, f"Deleted extension '{sip_extension}' could still make a SIP call."
_STEP_WRAPPED_WORKFLOWS = [
    "verify_call_extension_password_edit_is_saved",
    "verify_deleted_extension_cannot_call",
    "verify_pending_changes_are_published",
    "verify_pagination_next_and_previous_work",
    "verify_mobile_popup_opens_with_required_controls",
    "verify_extension_range_created_successfully",
    "verify_extension_created_successfully",
    "verify_add_generate_password_toggles_password_field",
    "verify_add_required_validation_prevents_saving",
    "verify_add_popup_shows_required_controls",
    "verify_edit_cancel_discards_changes",
    "verify_edited_values_are_saved",
    "verify_generated_password_is_saved_after_edit",
    "verify_edit_popup_is_populated_with_existing_data",
    "verify_export_contains_records_from_all_pages",
    "verify_export_download_contains_expected_columns_and_data",
    "verify_filters_are_cleared_and_full_list_is_displayed",
    "verify_full_extension_list_is_displayed",
    "verify_matching_extension_is_displayed",
    "search_extension_and_get_rows",
    "clear_search_and_get_rows",
    "clear_filters_and_get_rows",
    "export_extensions_and_read_rows",
    "collect_table_records_from_all_pages",
    "open_edit_popup_for_first_extension",
    "assert_edit_popup_matches_row",
    "open_add_popup_and_assert_controls",
    "trigger_add_required_validation",
    "assert_add_required_validation",
    "open_add_popup_with_password_visible",
    "enable_generated_password_in_add_popup",
    "open_mobile_popup_for_first_extension",
    "assert_mobile_popup_controls",
    "navigate_to_next_page_and_back",
    "assert_next_page_changes_records",
    "return_to_previous_page",
    "publish_changes_and_assert_page_loaded",
    "assert_extension_is_visible",
    "assert_extension_record_is_visible",
    "generate_new_password_in_edit_popup",
    "assert_generated_password_was_saved",
    "edit_extension_and_save_changes",
    "assert_saved_extension_changes_are_visible",
    "change_extension_values_and_cancel",
    "assert_cancelled_extension_changes_were_not_saved",
    "cancel_row_delete_and_assert_record_remains",
    "delete_row_and_assert_record_is_removed",
    "open_bottom_delete_popup_and_assert_fields",
    "assert_extension_range_is_visible",
    "cancel_bottom_delete_and_assert_range_remains",
    "delete_bottom_range_and_assert_removed",
    "assert_created_extension_is_visible",
    "assert_created_extension_range_exists",
    "create_unpublished_extension",
    "configure_microsip_account",
    "check_microsip_call_succeeds",
    "assert_microsip_call_is_declined",
    "assert_microsip_call_succeeds",
    "delete_extension_and_publish",
    "call_number_from_softphone",
    "assert_search_field_is_empty",
    "assert_search_has_no_results",
]

for _workflow_name in _STEP_WRAPPED_WORKFLOWS:
    globals()[_workflow_name] = test_step()(globals()[_workflow_name])
