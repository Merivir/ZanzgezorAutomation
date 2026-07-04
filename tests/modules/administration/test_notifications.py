import pytest
import time

from tests.config.automation_config import (
    get_active_client,
    get_client_config,
    get_user_credentials,
    load_config,
)
from tests.config.testcase import testcase
from tests.pages.administration_page import AdministrationPage
from tests.pages.login_page import LoginPage
from tests.pages.notifications_page import NotificationsPage


def skip_not_automated_yet():
    pytest.skip("Linked to TestLink, but Selenium steps are not automated yet.")


def not_automated(test_func):
    test_func = pytest.mark.not_automated(test_func)
    return pytest.mark.skip(reason="Linked to TestLink, but Selenium steps are not automated yet.")(test_func)


not_automated.__test__ = False


@pytest.fixture(scope="module")
def opened_notifications_page(driver, wait):
    config = load_config()
    active_client = get_active_client(config)
    client_config = get_client_config(config, active_client)
    credentials = get_user_credentials(config, "default")

    login_page = LoginPage(driver, wait, client_config["base_url"])
    administration_page = AdministrationPage(driver, wait)
    notifications_page = NotificationsPage(driver, wait)

    login_page.open()
    login_page.login(credentials["username"], credentials["password"])
    administration_page.open_administration_page()
    administration_page.open_notifications()
    notifications_page.wait_until_loaded()

    return notifications_page


def first_record_or_skip(notifications_page):
    record = notifications_page.first_visible_record()
    if not record:
        pytest.skip("No Notification records are available for this check.")
    return record


def first_record_with_value_or_skip(notifications_page, field):
    record = notifications_page.first_record_with_value_or_none(field)
    if not record:
        pytest.skip(f"No Notification record with {field!r} is available.")
    return record


@testcase("NOTIF-001", "Notifications: Open Notifications page")
@pytest.mark.administration
@pytest.mark.notifications
def test_notifications_page_opens(opened_notifications_page):
    assert opened_notifications_page.is_loaded(), "Notifications page did not load correctly."
    assert opened_notifications_page.has_main_controls(), "Not all Notifications main controls are visible."
    assert opened_notifications_page.row_action_icons_exist(), "Expected edit/delete/translate row action icons."


@testcase("NOTIF-002", "Notifications: Check main table data loading")
@pytest.mark.administration
@pytest.mark.notifications
def test_notifications_table_data_loads(opened_notifications_page):
    opened_notifications_page.clear_filters()
    assert opened_notifications_page.visible_table_records(), "Expected notification records to load in the table."


@testcase("NOTIF-003", "Notifications: Check default result count")
@pytest.mark.administration
@pytest.mark.notifications
def test_default_result_count_is_displayed(opened_notifications_page):
    opened_notifications_page.clear_filters()
    result_count = opened_notifications_page.result_count()

    assert result_count is not None, "Expected result count to be displayed."
    assert result_count >= opened_notifications_page.visible_record_count(), (
        "Result count should be at least the number of visible rows on the current page."
    )


@testcase("NOTIF-004", "Notifications: Search notification by Category")
@pytest.mark.administration
@pytest.mark.notifications
def test_search_notification_by_category(opened_notifications_page):
    opened_notifications_page.clear_filters()
    record = first_record_with_value_or_skip(opened_notifications_page, "Category")

    opened_notifications_page.search_by_category(record["Category"])

    assert opened_notifications_page.visible_table_records(), "Expected records after searching by Category."
    assert opened_notifications_page.records_match_field("Category", record["Category"]), (
        f"Expected all visible records to match Category {record['Category']!r}."
    )


@testcase("NOTIF-005", "Notifications: Search by partial Category")
@pytest.mark.administration
@pytest.mark.notifications
def test_search_by_partial_category(opened_notifications_page):
    opened_notifications_page.clear_filters()
    record = first_record_with_value_or_skip(opened_notifications_page, "Category")
    category = record["Category"]
    partial_category = category[: max(3, len(category) // 2)]

    opened_notifications_page.search_by_category(partial_category)

    assert opened_notifications_page.visible_table_records(), "Expected records after searching by partial Category."
    assert opened_notifications_page.records_contain_category(partial_category), (
        f"Expected all visible records to contain Category text {partial_category!r}."
    )


@testcase("NOTIF-006", "Notifications: Search by non-existing Category")
@pytest.mark.administration
@pytest.mark.notifications
def test_search_by_non_existing_category(opened_notifications_page):
    opened_notifications_page.clear_filters()
    opened_notifications_page.search_by_category("non-existing-notification-category-999999")

    assert opened_notifications_page.result_count() == 0 or not opened_notifications_page.visible_table_records(), (
        "Expected empty results for a non-existing Category."
    )


@testcase("NOTIF-007", "Notifications: Filter by Type")
@pytest.mark.administration
@pytest.mark.notifications
def test_filter_by_type(opened_notifications_page):
    opened_notifications_page.clear_filters()
    record = first_record_with_value_or_skip(opened_notifications_page, "Type")

    opened_notifications_page.choose_type_filter(record["Type"]).click_search()

    assert opened_notifications_page.visible_table_records(), "Expected records after filtering by Type."
    assert opened_notifications_page.records_match_field("Type", record["Type"]), (
        f"Expected all visible records to match Type {record['Type']!r}."
    )


@testcase("NOTIF-008", "Notifications: Filter by Theme")
@pytest.mark.administration
@pytest.mark.notifications
def test_filter_by_theme(opened_notifications_page):
    opened_notifications_page.clear_filters()
    record = first_record_with_value_or_skip(opened_notifications_page, "Theme")

    opened_notifications_page.choose_theme_filter(record["Theme"]).click_search()

    assert opened_notifications_page.visible_table_records(), "Expected records after filtering by Theme."
    assert opened_notifications_page.records_match_field("Theme", record["Theme"]), (
        f"Expected all visible records to match Theme {record['Theme']!r}."
    )


@testcase("NOTIF-009", "Notifications: Filter by Active status")
@pytest.mark.administration
@pytest.mark.notifications
def test_filter_by_active_status(opened_notifications_page):
    opened_notifications_page.clear_filters()
    record = first_record_with_value_or_skip(opened_notifications_page, "Active")

    opened_notifications_page.choose_active_filter(record["Active"]).click_search()

    assert opened_notifications_page.visible_table_records(), "Expected records after filtering by Active."
    assert opened_notifications_page.records_match_field("Active", record["Active"]), (
        f"Expected all visible records to match Active {record['Active']!r}."
    )


@testcase("NOTIF-010", "Notifications: Search with combined filters")
@pytest.mark.administration
@pytest.mark.notifications
def test_search_with_combined_filters(opened_notifications_page):
    opened_notifications_page.clear_filters()
    record = first_record_or_skip(opened_notifications_page)
    expected_values = {
        "Category": record["Category"],
        "Type": record["Type"],
        "Theme": record["Theme"],
        "Active": record["Active"],
    }

    opened_notifications_page.set_category_filter(record["Category"])
    opened_notifications_page.choose_type_filter(record["Type"])
    opened_notifications_page.choose_theme_filter(record["Theme"])
    opened_notifications_page.choose_active_filter(record["Active"])
    opened_notifications_page.click_search()

    assert opened_notifications_page.visible_table_records(), "Expected records after applying combined filters."
    assert opened_notifications_page.records_match_all(expected_values), (
        f"Expected all visible records to match combined filters {expected_values!r}."
    )


@testcase("NOTIF-011", "Notifications: Clear filters")
@pytest.mark.administration
@pytest.mark.notifications
def test_clear_filters(opened_notifications_page):
    opened_notifications_page.clear_filters()
    full_count = opened_notifications_page.result_count()
    record = first_record_or_skip(opened_notifications_page)

    opened_notifications_page.search_by_category(record["Category"])
    opened_notifications_page.clear_filters()

    assert opened_notifications_page.current_category_filter_value() == "", "Category filter should be empty."
    assert opened_notifications_page.result_count() == full_count, "Expected full result count after clearing filters."


@testcase("NOTIF-012", "Notifications: Clear selected dropdown value")
@pytest.mark.administration
@pytest.mark.notifications
def test_clear_selected_dropdown_value(opened_notifications_page):
    opened_notifications_page.clear_filters()
    record = first_record_with_value_or_skip(opened_notifications_page, "Active")

    opened_notifications_page.choose_active_filter(record["Active"])
    assert opened_notifications_page.current_dropdown_text(opened_notifications_page.ACTIVE_FILTER), (
        "Selected Active dropdown value should be visible."
    )

    opened_notifications_page.clear_dropdown_filter(opened_notifications_page.ACTIVE_FILTER)
    opened_notifications_page.click_search()

    assert opened_notifications_page.visible_table_records(), "Expected table records after clearing dropdown value."


@testcase("NOTIF-013", "Notifications: Open Add form")
@pytest.mark.administration
@pytest.mark.notifications
def test_open_add_form(opened_notifications_page):
    opened_notifications_page.open_add_form()
    try:
        assert opened_notifications_page.is_popup_open(), "Add notification form did not open."
    finally:
        opened_notifications_page.close_popup()


@testcase("NOTIF-014", "Notifications: Add new notification")
@pytest.mark.administration
@pytest.mark.notifications
@not_automated
def test_add_new_notification(opened_notifications_page):
    skip_not_automated_yet()


@testcase("NOTIF-015", "Notifications: Add duplicate notification name")
@pytest.mark.administration
@pytest.mark.notifications
@not_automated
def test_add_duplicate_notification_name(opened_notifications_page):
    skip_not_automated_yet()


@testcase("NOTIF-016", "Notifications: Open Edit form")
@pytest.mark.administration
@pytest.mark.notifications
def test_open_edit_form(opened_notifications_page):
    opened_notifications_page.clear_filters()
    first_record_or_skip(opened_notifications_page)
    opened_notifications_page.open_first_row_edit_form()
    try:
        assert opened_notifications_page.is_popup_open(), "Edit notification form did not open."
    finally:
        opened_notifications_page.close_popup()


@testcase("NOTIF-017", "Notifications: Edit notification data")
@pytest.mark.administration
@pytest.mark.notifications
@not_automated
def test_edit_notification_data(opened_notifications_page):
    skip_not_automated_yet()


@testcase("NOTIF-018", "Notifications: Cancel editing")
@pytest.mark.administration
@pytest.mark.notifications
@not_automated
def test_cancel_editing(opened_notifications_page):
    skip_not_automated_yet()


@testcase("NOTIF-019", "Notifications: Active status behavior")
@pytest.mark.administration
@pytest.mark.notifications
@not_automated
def test_active_status_behavior(opened_notifications_page):
    skip_not_automated_yet()


@testcase("NOTIF-020", "Notifications: Persist in list behavior")
@pytest.mark.administration
@pytest.mark.notifications
@not_automated
def test_persist_in_list_behavior(opened_notifications_page):
    skip_not_automated_yet()


@testcase("NOTIF-021", "Notifications: Non-persist notification behavior")
@pytest.mark.administration
@pytest.mark.notifications
@not_automated
def test_non_persist_notification_behavior(opened_notifications_page):
    skip_not_automated_yet()


@testcase("NOTIF-022", "Notifications: Expire Time dependency on Persist")
@pytest.mark.administration
@pytest.mark.notifications
@not_automated
def test_expire_time_dependency_on_persist(opened_notifications_page):
    skip_not_automated_yet()


@testcase("NOTIF-023", "Notifications: Show Time behavior")
@pytest.mark.administration
@pytest.mark.notifications
@not_automated
def test_show_time_behavior(opened_notifications_page):
    skip_not_automated_yet()


@testcase("NOTIF-024", "Notifications: Expire Time behavior")
@pytest.mark.administration
@pytest.mark.notifications
@not_automated
def test_expire_time_behavior(opened_notifications_page):
    skip_not_automated_yet()


@testcase("NOTIF-025", "Notifications: Zero values are allowed")
@pytest.mark.administration
@pytest.mark.notifications
@not_automated
def test_zero_values_are_allowed(opened_notifications_page):
    skip_not_automated_yet()


@testcase("NOTIF-026", "Notifications: Negative values are blocked")
@pytest.mark.administration
@pytest.mark.notifications
@not_automated
def test_negative_values_are_blocked(opened_notifications_page):
    skip_not_automated_yet()


@testcase("NOTIF-027", "Notifications: Delete notification")
@pytest.mark.administration
@pytest.mark.notifications
@not_automated
def test_delete_notification(opened_notifications_page):
    skip_not_automated_yet()


@testcase("NOTIF-028", "Notifications: Deleted notification cache behavior")
@pytest.mark.administration
@pytest.mark.notifications
@not_automated
def test_deleted_notification_cache_behavior(opened_notifications_page):
    skip_not_automated_yet()


@testcase("NOTIF-029", "Notifications: Open Translate form")
@pytest.mark.administration
@pytest.mark.notifications
def test_open_translate_form(opened_notifications_page):
    opened_notifications_page.clear_filters()
    first_record_or_skip(opened_notifications_page)
    opened_notifications_page.open_first_row_translate_form()
    try:
        assert opened_notifications_page.is_popup_open(), "Translate notification form did not open."
    finally:
        opened_notifications_page.close_popup()


@testcase("NOTIF-030", "Notifications: Save notification translation")
@pytest.mark.administration
@pytest.mark.notifications
@not_automated
def test_save_notification_translation(opened_notifications_page):
    skip_not_automated_yet()


@testcase("NOTIF-031", "Notifications: Missing localization fallback")
@pytest.mark.administration
@pytest.mark.notifications
@not_automated
def test_missing_localization_fallback(opened_notifications_page):
    skip_not_automated_yet()


@testcase("NOTIF-032", "Notifications: Pagination works correctly")
@pytest.mark.administration
@pytest.mark.notifications
def test_pagination_works_correctly(opened_notifications_page):
    opened_notifications_page.clear_filters()

    assert opened_notifications_page.can_use_pagination(), "Rows-per-page control should be visible."
    assert opened_notifications_page.result_count() >= opened_notifications_page.visible_record_count(), (
        "Result count should remain consistent with visible paginated data."
    )


@testcase("NOTIF-033", "Notifications: Column visibility works correctly")
@pytest.mark.administration
@pytest.mark.notifications
def test_column_visibility_works_correctly(opened_notifications_page):
    opened_notifications_page.clear_filters()
    initial_column_count = opened_notifications_page.visible_table_column_count()
    assert initial_column_count > 0, "Expected visible table columns before changing column visibility."

    opened_notifications_page.open_column_visibility_dropdown()
    labels = opened_notifications_page.column_visibility_option_labels()
    assert labels, "Expected Notifications column visibility options."
    column_to_toggle = labels[0]

    try:
        opened_notifications_page.set_column_option_visibility(column_to_toggle, False)
        time.sleep(1)
        assert opened_notifications_page.visible_table_column_count() == initial_column_count - 1, (
            f"Expected one fewer visible column after hiding {column_to_toggle!r}."
        )

        opened_notifications_page.set_column_option_visibility(column_to_toggle, True)
        time.sleep(1)
        assert opened_notifications_page.visible_table_column_count() == initial_column_count, (
            f"Expected column count to return after showing {column_to_toggle!r}."
        )
    finally:
        opened_notifications_page.set_column_option_visibility(column_to_toggle, True)
        opened_notifications_page.close_column_visibility_dropdown()


@testcase("NOTIF-034", "Notifications: Generic ordering check")
@pytest.mark.administration
@pytest.mark.notifications
def test_generic_ordering_check(opened_notifications_page):
    opened_notifications_page.clear_filters()
    before_sort_count = opened_notifications_page.visible_record_count()

    opened_notifications_page.click_sort_header("Category")

    assert opened_notifications_page.visible_record_count() == before_sort_count, (
        "Sorting should keep the current page data count consistent."
    )
    assert opened_notifications_page.visible_table_records(), "Expected records after sorting by Category."


@testcase("NOTIF-035", "Notifications: Actions after filtering/sorting")
@pytest.mark.administration
@pytest.mark.notifications
def test_actions_after_filtering_sorting(opened_notifications_page):
    opened_notifications_page.clear_filters()
    record = first_record_with_value_or_skip(opened_notifications_page, "Category")

    opened_notifications_page.search_by_category(record["Category"])
    opened_notifications_page.click_sort_header("Category")
    opened_notifications_page.open_first_row_edit_form()

    try:
        assert opened_notifications_page.is_popup_open(), "Edit action should open after filtering and sorting."
    finally:
        opened_notifications_page.close_popup()
