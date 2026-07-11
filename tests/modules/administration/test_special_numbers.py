import pytest

from tests.config.automation_config import (
    get_active_client,
    get_client_config,
    get_user_credentials,
    load_config,
)
from tests.config.testcase import testcase
from tests.pages.administration_page import AdministrationPage
from tests.pages.login_page import LoginPage
from tests.pages.special_numbers_page import SpecialNumbersPage


pytestmark = pytest.mark.regression


def skip_not_automated_yet():
    pytest.skip("Linked to TestLink, but Selenium steps are not automated yet.")


def not_automated(test_func):
    test_func = pytest.mark.not_automated(test_func)
    return pytest.mark.skip(reason="Linked to TestLink, but Selenium steps are not automated yet.")(test_func)


not_automated.__test__ = False


@pytest.fixture(scope="module")
def opened_special_numbers_page(driver, wait):
    config = load_config()
    active_client = get_active_client(config)
    client_config = get_client_config(config, active_client)
    credentials = get_user_credentials(config, "default")

    login_page = LoginPage(driver, wait, client_config["base_url"])
    administration_page = AdministrationPage(driver, wait)
    special_numbers_page = SpecialNumbersPage(driver, wait)

    login_page.open()
    login_page.login(credentials["username"], credentials["password"])
    administration_page.open_administration_page()
    administration_page.open_special_numbers()
    special_numbers_page.wait_until_loaded()

    return special_numbers_page


def first_record_or_skip(special_numbers_page):
    record = special_numbers_page.first_visible_record()
    if not record:
        pytest.skip("No Special Numbers records are available for this read-only check.")
    return record


def first_record_with_type_or_skip(special_numbers_page):
    for record in special_numbers_page.visible_table_records():
        if record.get("Number Type"):
            return record
    pytest.skip("No Special Numbers record with Number Type is available.")


@testcase("808-3122", "Verify Special Numbers: Navigation - Special Numbers page opens correctly")
@pytest.mark.administration
@pytest.mark.special_numbers
@pytest.mark.smoke
def test_special_numbers_page_opens_correctly(opened_special_numbers_page):
    assert opened_special_numbers_page.is_loaded(), "Special Numbers page did not load correctly."
    assert opened_special_numbers_page.has_main_controls(), "Not all Special Numbers main controls are visible."
    assert opened_special_numbers_page.row_action_icons_exist(), "Expected row edit/delete action icons to be visible."


@testcase("808-3123", "Verify Special Numbers: Filters - Number type filter returns matching results")
@pytest.mark.administration
@pytest.mark.special_numbers
@pytest.mark.smoke
def test_number_type_filter_returns_matching_results(opened_special_numbers_page):
    record = first_record_with_type_or_skip(opened_special_numbers_page)
    number_type = record["Number Type"]

    opened_special_numbers_page.filter_by_type_and_search(number_type)
    opened_special_numbers_page.wait_for_ui_idle()

    assert opened_special_numbers_page.current_type_filter_text(), "Selected type filter should be visible."
    assert opened_special_numbers_page.visible_table_records(), "Expected records after applying type filter."
    assert opened_special_numbers_page.records_match_type(number_type), (
        f"Expected all visible records to match type {number_type!r}."
    )


@testcase("808-3124", "Verify Special Numbers: Filters - Search by number returns matching result")
@pytest.mark.administration
@pytest.mark.special_numbers
@pytest.mark.smoke
def test_search_by_number_returns_matching_result(opened_special_numbers_page):
    opened_special_numbers_page.clear_filters()
    opened_special_numbers_page.wait_for_ui_idle()
    record = first_record_or_skip(opened_special_numbers_page)
    number = record["Number"]

    opened_special_numbers_page.search_by_number(number)
    opened_special_numbers_page.wait_for_ui_idle()

    assert opened_special_numbers_page.visible_table_records(), "Expected record after searching by number."
    assert opened_special_numbers_page.records_match_number(number), (
        f"Expected all visible records to match number {number!r}."
    )


@testcase("808-3125", "Verify Special Numbers: Filters - Combined filters return matching results")
@pytest.mark.administration
@pytest.mark.special_numbers
def test_combined_filters_return_matching_results(opened_special_numbers_page):
    opened_special_numbers_page.clear_filters()
    opened_special_numbers_page.wait_for_ui_idle()
    record = first_record_with_type_or_skip(opened_special_numbers_page)
    number = record["Number"]
    number_type = record["Number Type"]

    opened_special_numbers_page.choose_type_filter(number_type)
    opened_special_numbers_page.search_by_number(number)
    opened_special_numbers_page.wait_for_ui_idle()

    assert opened_special_numbers_page.visible_table_records(), "Expected records after applying combined filters."
    assert opened_special_numbers_page.records_match_number(number), (
        f"Expected all visible records to match number {number!r}."
    )
    assert opened_special_numbers_page.records_match_type(number_type), (
        f"Expected all visible records to match type {number_type!r}."
    )


@testcase("808-3126", "Verify Special Numbers: Filters - Clear filters resets selected values")
@pytest.mark.administration
@pytest.mark.special_numbers
def test_clear_filters_resets_selected_values(opened_special_numbers_page):
    record = first_record_with_type_or_skip(opened_special_numbers_page)

    opened_special_numbers_page.choose_type_filter(record["Number Type"])
    opened_special_numbers_page.search_by_number(record["Number"])
    opened_special_numbers_page.wait_for_ui_idle()
    opened_special_numbers_page.clear_filters()
    opened_special_numbers_page.wait_for_ui_idle()

    assert opened_special_numbers_page.visible_table_records(), "Expected table records after clearing filters."


@testcase("808-3127", "Verify Special Numbers: Results - Results count reflects displayed records")
@pytest.mark.administration
@pytest.mark.special_numbers
@pytest.mark.extended
def test_results_count_reflects_displayed_records(opened_special_numbers_page):
    opened_special_numbers_page.clear_filters()
    opened_special_numbers_page.wait_for_ui_idle()
    record = first_record_with_type_or_skip(opened_special_numbers_page)

    opened_special_numbers_page.filter_by_type_and_search(record["Number Type"])
    opened_special_numbers_page.wait_for_ui_idle()

    assert opened_special_numbers_page.result_count() == opened_special_numbers_page.visible_record_count(), (
        "Results count should match visible table record count."
    )


@testcase("808-3128", "Verify Special Numbers: Columns - Visible columns can be changed from dropdown")
@pytest.mark.administration
@pytest.mark.special_numbers
@pytest.mark.extended
def test_visible_columns_can_be_changed_from_dropdown(opened_special_numbers_page):
    initial_column_count = opened_special_numbers_page.visible_table_column_count()
    assert initial_column_count > 0, "Expected visible table columns before changing column visibility."

    opened_special_numbers_page.open_column_visibility_dropdown()
    opened_special_numbers_page.wait_for_ui_idle()
    labels = opened_special_numbers_page.column_visibility_option_labels()
    assert labels, "Expected Special Numbers column visibility options."
    column_to_toggle = labels[0]

    try:
        opened_special_numbers_page.set_column_option_visibility(column_to_toggle, False)
        opened_special_numbers_page.wait_for_ui_idle()
        assert opened_special_numbers_page.visible_table_column_count() == initial_column_count - 1, (
            f"Expected one fewer visible column after hiding {column_to_toggle!r}."
        )

        opened_special_numbers_page.set_column_option_visibility(column_to_toggle, True)
        opened_special_numbers_page.wait_for_ui_idle()
        assert opened_special_numbers_page.visible_table_column_count() == initial_column_count, (
            f"Expected column count to return after showing {column_to_toggle!r}."
        )
    finally:
        opened_special_numbers_page.set_column_option_visibility(column_to_toggle, True)
        opened_special_numbers_page.close_column_visibility_dropdown()


@testcase("808-3129", "Verify Special Numbers: Add - Add Number popup opens correctly")
@pytest.mark.administration
@pytest.mark.special_numbers
@not_automated
def test_add_number_popup_opens_correctly(opened_special_numbers_page):
    skip_not_automated_yet()


@testcase("808-3130", "Verify Special Numbers: Add - Required fields validation works")
@pytest.mark.administration
@pytest.mark.special_numbers
@not_automated
def test_add_required_fields_validation_works(opened_special_numbers_page):
    skip_not_automated_yet()


@testcase("808-3131", "Verify Special Numbers: Add - Number field validation works")
@pytest.mark.administration
@pytest.mark.special_numbers
@not_automated
def test_add_number_field_validation_works(opened_special_numbers_page):
    skip_not_automated_yet()


@testcase("808-3132", "Verify Special Numbers: Add - Type field validation works")
@pytest.mark.administration
@pytest.mark.special_numbers
@not_automated
def test_add_type_field_validation_works(opened_special_numbers_page):
    skip_not_automated_yet()


@testcase("808-3133", "Verify Special Numbers: Add - Description field validation works")
@pytest.mark.administration
@pytest.mark.special_numbers
@not_automated
def test_add_description_field_validation_works(opened_special_numbers_page):
    skip_not_automated_yet()


@testcase("808-3134", "Verify Special Numbers: Add - Date range validation works")
@pytest.mark.administration
@pytest.mark.special_numbers
@not_automated
def test_add_date_range_validation_works(opened_special_numbers_page):
    skip_not_automated_yet()


@testcase("808-3135", "Verify Special Numbers: Add - White list number can be created successfully")
@pytest.mark.administration
@pytest.mark.special_numbers
@not_automated
def test_white_list_number_can_be_created_successfully(opened_special_numbers_page):
    skip_not_automated_yet()


@testcase("808-3136", "Verify Special Numbers: Add - Black list number can be created successfully")
@pytest.mark.administration
@pytest.mark.special_numbers
@not_automated
def test_black_list_number_can_be_created_successfully(opened_special_numbers_page):
    skip_not_automated_yet()


@testcase("808-3137", "Verify Special Numbers: Add - Cancel closes popup without saving")
@pytest.mark.administration
@pytest.mark.special_numbers
@not_automated
def test_add_cancel_closes_popup_without_saving(opened_special_numbers_page):
    skip_not_automated_yet()


@testcase("808-3138", "Verify Special Numbers: Edit - Edit Number popup opens with existing values")
@pytest.mark.administration
@pytest.mark.special_numbers
@not_automated
def test_edit_number_popup_opens_with_existing_values(opened_special_numbers_page):
    skip_not_automated_yet()


@testcase("808-3139", "Verify Special Numbers: Edit - Existing record can be updated successfully")
@pytest.mark.administration
@pytest.mark.special_numbers
@not_automated
def test_existing_record_can_be_updated_successfully(opened_special_numbers_page):
    skip_not_automated_yet()


@testcase("808-3140", "Verify Special Numbers: Edit - Cancel keeps original values unchanged")
@pytest.mark.administration
@pytest.mark.special_numbers
@not_automated
def test_edit_cancel_keeps_original_values_unchanged(opened_special_numbers_page):
    skip_not_automated_yet()


@testcase("808-3141", "Verify Special Numbers: Delete - Selected record can be deleted successfully")
@pytest.mark.administration
@pytest.mark.special_numbers
@not_automated
def test_selected_record_can_be_deleted_successfully(opened_special_numbers_page):
    skip_not_automated_yet()


@testcase("808-3142", "Verify Special Numbers: Publish - Publish applies saved changes successfully")
@pytest.mark.administration
@pytest.mark.special_numbers
@not_automated
def test_publish_applies_saved_changes_successfully(opened_special_numbers_page):
    skip_not_automated_yet()


@testcase("808-3143", "Verify Special Numbers: Table - Saved values match popup values")
@pytest.mark.administration
@pytest.mark.special_numbers
@not_automated
def test_saved_values_match_popup_values(opened_special_numbers_page):
    skip_not_automated_yet()


@testcase("808-3144", "Verify Special Numbers: Business logic - White list number is saved with correct type")
@pytest.mark.administration
@pytest.mark.special_numbers
@not_automated
def test_white_list_number_is_saved_with_correct_type(opened_special_numbers_page):
    skip_not_automated_yet()


@testcase("808-3145", "Verify Special Numbers: Business logic - Black list number is saved with correct type")
@pytest.mark.administration
@pytest.mark.special_numbers
@not_automated
def test_black_list_number_is_saved_with_correct_type(opened_special_numbers_page):
    skip_not_automated_yet()
