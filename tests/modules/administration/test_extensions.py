import pytest
from selenium.webdriver.support import expected_conditions as ec

from tests.config.automation_config import (
    load_config,
    get_active_client,
    get_client_config,
    get_extensions_config,
    get_user_credentials,
)
from tests.config.testcase import testcase
from tests.pages.login_page import LoginPage
from tests.pages.administration_page import AdministrationPage
from tests.pages.extensions_page import ExtensionsPage
from tests.pages.softphone_page import SoftphonePage
from tests.helpers.extensions.column_helpers import (
    ensure_extension_columns_visible,
    hide_and_restore_one_extension_column,
)
from tests.helpers.extensions.data_helpers import (
    add_extension_from_ui,
    add_extension_range_from_ui,
    bottom_delete_extension_range_from_ui,
    cleanup_extensions_with_db_fallback,
    extensions_remaining_in_database,
    get_extension_numbers_from_database,
    get_non_existing_extension_number,
    get_extension_identity_from_database,
    row_delete_extension_from_ui,
)
from tests.helpers.extensions.workflows import (
    assert_extension_range_is_visible,
    assert_search_has_no_results,
    call_number_from_softphone,
    cancel_bottom_delete_and_assert_range_remains,
    cancel_row_delete_and_assert_record_remains,
    check_microsip_call_succeeds,
    configure_microsip_account,
    create_unpublished_extension,
    delete_bottom_range_and_assert_removed,
    delete_extension_and_publish,
    delete_row_and_assert_record_is_removed,
    open_bottom_delete_popup_and_assert_fields,
    publish_changes_and_assert_page_loaded,
    verify_add_generate_password_toggles_password_field,
    verify_add_popup_shows_required_controls,
    verify_add_required_validation_prevents_saving,
    verify_call_extension_password_edit_is_saved,
    verify_deleted_extension_cannot_call,
    verify_edit_cancel_discards_changes,
    verify_edit_popup_is_populated_with_existing_data,
    verify_edited_values_are_saved,
    verify_export_contains_records_from_all_pages,
    verify_export_download_contains_expected_columns_and_data,
    verify_extension_created_successfully,
    verify_extension_range_created_successfully,
    verify_filters_are_cleared_and_full_list_is_displayed,
    verify_full_extension_list_is_displayed,
    verify_generated_password_is_saved_after_edit,
    verify_matching_extension_is_displayed,
    verify_mobile_popup_opens_with_required_controls,
    verify_pagination_next_and_previous_work,
    verify_pending_changes_are_published,
)


pytestmark = [pytest.mark.regression, pytest.mark.requires_pjsip]


@pytest.fixture(scope="module")
def opened_extensions_page(driver, wait):
    config = load_config()
    active_client = get_active_client(config)
    client_config = get_client_config(config, active_client)
    credentials = get_user_credentials(config, "default")

    login_page = LoginPage(driver, wait, client_config["base_url"])
    administration_page = AdministrationPage(driver, wait)
    extensions_page = ExtensionsPage(driver, wait)

    login_page.open()
    login_page.login(credentials["username"], credentials["password"])
    administration_page.open_administration_page()
    administration_page.open_extensions()
    extensions_page.wait_until_loaded()

    return extensions_page


@pytest.fixture(scope="module")
def database_extension_numbers():
    extension_numbers = [int(number) for number in get_extension_numbers_from_database()]
    if not extension_numbers:
        pytest.fail("The extensions database table is empty; test numbers cannot be selected.")
    return sorted(extension_numbers)


@pytest.fixture(scope="module")
def first_extension_number(database_extension_numbers):
    """First existing extension used by positive search/read-only cases."""
    return str(database_extension_numbers[0])


@pytest.fixture(scope="module")
def next_extension_number(database_extension_numbers):
    """MAX(extension) + 1, guaranteed unused at the start of this module."""
    return str(database_extension_numbers[-1] + 1)


@pytest.fixture(scope="module")
def extensions_environment():
    return get_extensions_config(load_config())


@pytest.fixture
def disposable_extension(opened_extensions_page):
    extension_number = str(get_non_existing_extension_number())
    try:
        add_extension_from_ui(opened_extensions_page, extension_number)
        yield extension_number
    finally:
        cleanup_extensions_with_db_fallback(
            opened_extensions_page,
            [extension_number],
            lambda: row_delete_extension_from_ui(opened_extensions_page, extension_number),
        )


@pytest.fixture
def disposable_extension_range(opened_extensions_page):
    start_extension = get_non_existing_extension_number() + 1
    end_extension = start_extension + 2
    extension_numbers = list(range(start_extension, end_extension + 1))
    try:
        extension_range = add_extension_range_from_ui(
            opened_extensions_page,
            start_extension,
            end_extension,
        )
        yield extension_range
    finally:
        cleanup_extensions_with_db_fallback(
            opened_extensions_page,
            extension_numbers,
            lambda: bottom_delete_extension_range_from_ui(opened_extensions_page, start_extension, end_extension),
        )


def skip_not_automated_yet():
    pytest.skip("Linked to TestLink, but Selenium steps are not automated yet.")


def not_automated(test_func):
    test_func = pytest.mark.not_automated(test_func)
    return pytest.mark.skip(reason="Linked to TestLink, but Selenium steps are not automated yet.")(test_func)


not_automated.__test__ = False


@testcase("808-808", "Verify Company Extensions: Navigation - Extensions page opens correctly")
@pytest.mark.administration
@pytest.mark.extensions
@pytest.mark.smoke
def test_extensions_page_opens_correctly(opened_extensions_page):
    assert opened_extensions_page.is_loaded(), "Extensions page did not load correctly."


@testcase("808-3033", "Verify Company Extensions: Search - Matching extension returns filtered result")
@pytest.mark.administration
@pytest.mark.extensions
@pytest.mark.smoke
def test_extension_search_functionality(opened_extensions_page, first_extension_number):
    verify_matching_extension_is_displayed(opened_extensions_page, first_extension_number)

@testcase("808-3034", "Verify Company Extensions: Search - Empty search returns full extensions list")
@pytest.mark.administration
@pytest.mark.extensions
def test_empty_extension_search_returns_full_extensions_list(opened_extensions_page):
    verify_full_extension_list_is_displayed(opened_extensions_page)

@pytest.mark.skipif(False, reason="Temporarily disabled")
def test_extension_search_no_results(opened_extensions_page, next_extension_number):
    assert_search_has_no_results(opened_extensions_page, next_extension_number, ec)


@testcase("808-3035", "Verify Company Extensions: Filters - Clear filters resets search field")
@pytest.mark.administration
@pytest.mark.extensions
def test_extension_clear_filters(opened_extensions_page, first_extension_number):
    verify_filters_are_cleared_and_full_list_is_displayed(opened_extensions_page, first_extension_number)

@testcase("808-3036", "Verify Company Extensions: Columns - Visible columns can be changed from dropdown")
@pytest.mark.administration
@pytest.mark.extensions
@pytest.mark.extended
def test_visible_columns_can_be_changed_from_dropdown(opened_extensions_page):
    initial_column_count = ensure_extension_columns_visible(opened_extensions_page, expected_minimum=7)

    hide_and_restore_one_extension_column(opened_extensions_page, initial_column_count)


@testcase("808-3037", "Verify Company Extensions: Export - Export downloads extension data")
@pytest.mark.administration
@pytest.mark.extensions
@pytest.mark.extended
def test_export_downloads_extension_data(opened_extensions_page, download_dir, first_extension_number):
    verify_export_download_contains_expected_columns_and_data(
        opened_extensions_page,
        download_dir,
        first_extension_number,
    )

@testcase("808-3038", "Verify Company Extensions: Export - Export contains records from all pages")
@pytest.mark.administration
@pytest.mark.extensions
@pytest.mark.extended
def test_export_contains_records_from_all_pages(opened_extensions_page, download_dir):
    verify_export_contains_records_from_all_pages(opened_extensions_page, download_dir)

@testcase("808-3039", "Verify Company Extensions: Edit - Edit popup opens with existing record data")
@pytest.mark.administration
@pytest.mark.extensions
@pytest.mark.extended
def test_edit_popup_opens_with_existing_record_data(opened_extensions_page):
    verify_edit_popup_is_populated_with_existing_data(opened_extensions_page)

@testcase("808-3040", "Verify Company Extensions: Edit - Generate Password checkbox hides password field")
@pytest.mark.administration
@pytest.mark.extensions
@pytest.mark.destructive
def test_edit_generate_password_checkbox_hides_password_field(opened_extensions_page, disposable_extension):
    verify_generated_password_is_saved_after_edit(opened_extensions_page, disposable_extension)

@testcase("808-3041", "Verify Company Extensions: Edit - Existing extension can be edited successfully")
@pytest.mark.administration
@pytest.mark.extensions
@pytest.mark.destructive
def test_existing_extension_can_be_edited_successfully(opened_extensions_page, disposable_extension):
    verify_edited_values_are_saved(opened_extensions_page, disposable_extension)

@testcase("808-3042", "Verify Company Extensions: Edit - Cancel keeps original extension values")
@pytest.mark.administration
@pytest.mark.extensions
@pytest.mark.destructive
def test_edit_cancel_keeps_original_extension_values(opened_extensions_page, disposable_extension):
    verify_edit_cancel_discards_changes(opened_extensions_page, disposable_extension)

@testcase("808-3043", "Verify Company Extensions: Add - Add popup opens correctly")
@pytest.mark.administration
@pytest.mark.extensions
@pytest.mark.extended
def test_add_popup_opens_correctly(opened_extensions_page):
    verify_add_popup_shows_required_controls(opened_extensions_page)

@testcase("808-3044", "Verify Company Extensions: Add - Required fields validation works in Add popup")
@pytest.mark.administration
@pytest.mark.extensions
def test_add_required_fields_validation_works(opened_extensions_page):
    verify_add_required_validation_prevents_saving(opened_extensions_page)

@testcase("808-3045", "Verify Company Extensions: Add - Generate Password checkbox hides password field in Add popup")
@pytest.mark.administration
@pytest.mark.extensions
def test_add_generate_password_checkbox_hides_password_field(opened_extensions_page):
    verify_add_generate_password_toggles_password_field(opened_extensions_page)

@testcase("808-3046", "Verify Company Extensions: Add - New extension range can be added successfully")
@pytest.mark.administration
@pytest.mark.extensions
@pytest.mark.destructive
def test_adding_non_existent_extension(opened_extensions_page, disposable_extension):
    verify_extension_created_successfully(opened_extensions_page, disposable_extension)

@pytest.mark.administration
@pytest.mark.extensions
@pytest.mark.destructive
def test_adding_non_existent_extension_range(opened_extensions_page, disposable_extension_range):
    start_extension, end_extension = disposable_extension_range

    verify_extension_range_created_successfully(start_extension, end_extension)

@testcase("808-3047", "Verify Company Extensions: Mobile - Mobile popup opens for selected extension")
@pytest.mark.administration
@pytest.mark.extensions
@pytest.mark.extended
def test_mobile_popup_opens_for_selected_extension(opened_extensions_page):
    verify_mobile_popup_opens_with_required_controls(opened_extensions_page)

@testcase("808-3048", "Verify Company Extensions: Mobile - Number can be added and active phone selected")
@pytest.mark.administration
@pytest.mark.extensions
@not_automated
def test_mobile_number_can_be_added_and_active_phone_selected(opened_extensions_page):
    skip_not_automated_yet()


@testcase("808-3049", "Verify Company Extensions: Mobile - Cancel keeps phone data unchanged")
@pytest.mark.administration
@pytest.mark.extensions
@not_automated
def test_mobile_cancel_keeps_phone_data_unchanged(opened_extensions_page):
    skip_not_automated_yet()


@testcase("808-3050", "Verify Company Extensions: Delete - Cancel in row delete confirmation keeps record")
@pytest.mark.administration
@pytest.mark.extensions
@pytest.mark.destructive
def test_row_delete_cancel_keeps_record(opened_extensions_page, disposable_extension):
    cancel_row_delete_and_assert_record_remains(opened_extensions_page, disposable_extension)


@testcase("808-3051", "Verify Company Extensions: Delete - Row delete removes selected extension")
@pytest.mark.administration
@pytest.mark.extensions
@pytest.mark.destructive
def test_row_delete_removes_selected_extension(opened_extensions_page, disposable_extension):
    delete_row_and_assert_record_is_removed(
        opened_extensions_page,
        disposable_extension,
        extensions_remaining_in_database,
    )


@testcase("808-3052", "Verify Company Extensions: Delete - Bottom delete popup opens for extension range")
@pytest.mark.administration
@pytest.mark.extensions
@pytest.mark.destructive
def test_bottom_delete_popup_opens_for_extension_range(opened_extensions_page, disposable_extension_range):
    start_extension, end_extension = disposable_extension_range

    open_bottom_delete_popup_and_assert_fields(opened_extensions_page)
    assert_extension_range_is_visible(
        opened_extensions_page,
        start_extension,
        end_extension,
        "after opening bottom delete popup",
    )


@testcase("808-3053", "Verify Company Extensions: Delete - Cancel in bottom delete keeps extension range")
@pytest.mark.administration
@pytest.mark.extensions
@pytest.mark.destructive
def test_bottom_delete_cancel_keeps_extension_range(opened_extensions_page, disposable_extension_range):
    start_extension, end_extension = disposable_extension_range

    cancel_bottom_delete_and_assert_range_remains(opened_extensions_page, start_extension, end_extension)


@testcase("808-3054", "Verify Company Extensions: Delete - Bottom delete removes selected extension range")
@pytest.mark.administration
@pytest.mark.extensions
@pytest.mark.destructive
def test_bottom_delete_removes_selected_extension_range(opened_extensions_page, disposable_extension_range):
    start_extension, end_extension = disposable_extension_range

    delete_bottom_range_and_assert_removed(
        opened_extensions_page,
        start_extension,
        end_extension,
        extensions_remaining_in_database,
    )


@testcase("808-3055", "Verify Company Extensions: Pagination - Page navigation and items per page work correctly")
@pytest.mark.administration
@pytest.mark.extensions
def test_page_navigation_and_items_per_page_work_correctly(opened_extensions_page):
    verify_pagination_next_and_previous_work(opened_extensions_page, pytest)

@testcase("808-3056", "Verify Company Extensions: Publish - Publish applies saved changes successfully")
@pytest.mark.administration
@pytest.mark.extensions
@pytest.mark.destructive
@pytest.mark.publish
@pytest.mark.cloud_related
def test_publish_applies_saved_changes_successfully(opened_extensions_page):
    verify_pending_changes_are_published(opened_extensions_page)

@pytest.mark.administration
@pytest.mark.publish
@pytest.mark.integration
@pytest.mark.destructive
@pytest.mark.requires_microsip
@pytest.mark.cloud_related
def test_extension_becomes_available_only_after_publish(opened_extensions_page, microsip, extensions_environment):
    if not extensions_environment["sip_check_enabled"]:
        pytest.skip("SIP checks are disabled for the active environment.")
    missing_setup_reason = microsip.missing_setup_reason()
    if missing_setup_reason:
        pytest.skip(missing_setup_reason)
    if microsip.provider_name == "MicroSIP" and not microsip.check_command:
        pytest.skip("MICROSIP_CHECK_COMMAND is required to verify whether the call succeeds or declines.")

    extension_number = str(get_non_existing_extension_number())
    password = "Test1234"
    extension_created = False
    deletion_published = False

    try:
        create_unpublished_extension(opened_extensions_page, extension_number, password)
        extension_created = True
        extension_identity = get_extension_identity_from_database(extension_number)
        assert extension_identity["requires_publish"], (
            "Cloud Publish scenario requires a non-empty real_extension."
        )
        sip_extension = extension_identity["sip_extension"]

        configure_microsip_account(microsip, sip_extension, password)
        call_before_publish = check_microsip_call_succeeds(microsip, sip_extension, password)

        publish_changes_and_assert_page_loaded(opened_extensions_page)
        call_after_publish = check_microsip_call_succeeds(microsip, sip_extension, password)

        delete_extension_and_publish(opened_extensions_page, extension_number)
        deletion_published = True
        call_after_delete = check_microsip_call_succeeds(microsip, sip_extension, password)

        observed_states = (
            f"before Publish={call_before_publish}, "
            f"after Publish={call_after_publish}, "
            f"after delete and Publish={call_after_delete}"
        )
        assert not call_before_publish, f"Extension could call before Publish. Observed: {observed_states}"
        assert call_after_publish, f"Extension could not call after Publish. Observed: {observed_states}"
        assert not call_after_delete, f"Deleted extension could still call after Publish. Observed: {observed_states}"
    finally:
        if extension_created and not deletion_published:
            delete_extension_and_publish(opened_extensions_page, extension_number)


@pytest.mark.administration
@pytest.mark.integration
@pytest.mark.destructive
@pytest.mark.requires_microsip
def test_single_extension_can_make_call_from_ui(opened_extensions_page, microsip, extensions_environment):
    if not extensions_environment["sip_check_enabled"]:
        pytest.skip("SIP checks are disabled for the active environment.")
    missing_setup_reason = microsip.missing_setup_reason()
    if missing_setup_reason:
        pytest.skip(missing_setup_reason)

    extension_number = str(get_non_existing_extension_number())
    password = "Test1234"
    administration_tab = opened_extensions_page.driver.current_window_handle
    extension_created = False
    requires_publish = False
    sip_extension = None

    try:
        create_unpublished_extension(opened_extensions_page, extension_number, password)
        extension_created = True
        password = verify_call_extension_password_edit_is_saved(opened_extensions_page, extension_number)
        extension_identity = get_extension_identity_from_database(extension_number)
        sip_extension = extension_identity["sip_extension"]
        requires_publish = extension_identity["requires_publish"]

        if requires_publish:
            publish_changes_and_assert_page_loaded(opened_extensions_page)
        configure_microsip_account(microsip, sip_extension, password)
        call_number_from_softphone(
            SoftphonePage(opened_extensions_page.driver),
            extension_number,
            microsip.call_number,
            microsip=microsip,
        )
    finally:
        try:
            if administration_tab in opened_extensions_page.driver.window_handles:
                opened_extensions_page.driver.switch_to.window(administration_tab)
            if not opened_extensions_page.is_loaded():
                administration_page = AdministrationPage(opened_extensions_page.driver, opened_extensions_page.wait)
                administration_page.open_administration_page()
                administration_page.open_extensions()
                opened_extensions_page.wait_until_loaded()
            if extension_created:
                opened_extensions_page.delete_extension_if_exists(extension_number)
                if requires_publish:
                    opened_extensions_page.publish_changes()
                opened_extensions_page.wait_for_ui_idle()
                if sip_extension:
                    verify_deleted_extension_cannot_call(microsip, sip_extension, password)
                assert not extensions_remaining_in_database([extension_number]), (
                    f"Extension remained in database after cleanup: {extension_number}"
                )
        finally:
            microsip.restore_config_backup()
            if microsip.provider_name == "MicroSIP":
                microsip.restart()