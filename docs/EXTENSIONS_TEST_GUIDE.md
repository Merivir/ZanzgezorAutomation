# Extensions Test Guide

## Purpose

This document explains what the Extensions automation verifies, how test data is selected, and how to debug or extend the suite. Read it before changing `test_extensions.py`.

## Architecture

The suite follows these layers:

- `tests/modules/administration/test_extensions.py`: readable test scenarios and assertions.
- `tests/pages/extensions_page.py`: Selenium locators and page interactions.
- `tests/helpers/extensions/workflows.py`: reusable business steps.
- `tests/helpers/extensions/data_helpers.py`: test-data selection and cleanup orchestration.
- `tests/db/extension_queries.py`: parameterized SQL only.
- `tests/helpers/softphones/`: provider-neutral SIP client interface with MicroSIP and PJSUA adapters.
- `tests/conftest.py`: browser lifecycle, environment selection, logs, failure artifacts, and shared fixtures.

Tests should read as business steps. Locators, SQL, CSV parsing, process control, and retries belong in their helper layers.

## Environment Configuration

Each client has an `extensions` block:

```json
"extensions": {
  "cloud_related": true,
  "sip_check_enabled": true,
  "company_name": "new-hzor",
  "extension_type": "pjsip"
}
```

- `cloud_related`: enables cloud-only behavior tests.
- `sip_check_enabled`: allows SIP integration checks in that environment.
- Publish behavior is derived from the created row: a non-empty `real_extension` requires Publish.
- `company_name`: exact `company.name` used to scope extension SQL.
- `extension_type`: extension type used for data selection, currently `pjsip`.

Permission fields are independent from these settings and must not be changed while configuring Extensions tests.

## Extension Identity

The suite uses two identifiers and must not mix them:

- `extension`: the normal Administration and web softphone value, such as `347`.
- `sip_extension`: the account identity used by MicroSIP or PJSUA.

After an extension is created, the suite reads its scoped database row:

```sql
SELECT e.extension, e.real_extension
FROM company c
INNER JOIN extensions e ON c.id = e.company_id
WHERE e.extension = ? AND e.type = ? AND c.name = ?;
```

SIP identity is selected as follows:

```text
if real_extension has a value: use real_extension and Publish Add/Delete
otherwise: use extension and do not Publish Add/Delete
```

Example for `new-hzor`:

```text
Administration adds: 347
Web softphone selects: 347
Database real_extension: 1290238
SIP client registers: 1290238
Administration cleanup deletes: 347
```

There is no configured prefix calculation. The database is the source of truth.

## Test Data Selection

All extension reads and deletes are scoped by both company and type. The next disposable number comes from:

```sql
SELECT e.extension
FROM company c
INNER JOIN extensions e ON c.id = e.company_id
WHERE e.type = 'pjsip' AND c.name = 'new-hzor'
ORDER BY e.extension DESC
LIMIT 1;
```

The test adds one to the returned extension. Parameterized values are used in code; the literal query above is only an example.

Cleanup uses the same company/type scope so a matching extension from another company cannot be deleted accidentally.

## Covered Scenarios

### Page And Search

- Extensions page loads.
- Search returns the requested extension.
- Empty search restores the full list.
- Missing extension search shows no results.
- Clear filters restores rows.

### Columns And Export

- A visible column can be hidden and restored.
- Export downloads a CSV with expected columns and records.
- Export contains records represented across paginated table pages.
- Real Extension values are validated separately from Extension values.

### Edit

- Edit opens with existing row data.
- Generate Password hides the manual password field.
- Saved edits appear in the table.
- Cancel preserves original values.

### Add

- Add popup opens with expected controls.
- Required-field validation is shown.
- Generate Password hides the password field.
- A disposable single extension can be added.
- A disposable extension range can be added.

### Mobile

- Mobile popup opens for a selected extension.
- A mobile number and active phone can be selected.
- Cancel keeps original phone data.

### Delete

- Row-delete Cancel keeps the record.
- Row delete removes the selected extension.
- Bottom range-delete opens correctly.
- Bottom range-delete Cancel keeps the range.
- Bottom range-delete removes the selected range.

### Pagination And Publish

- Next/previous navigation and items-per-page work.
- Publish leaves the Extensions page usable.
- Cloud extension SIP behavior is checked before Publish, after Publish, and after delete plus Publish.

### SIP Integration

- Administration creates the normal extension.
- The SIP client registers with `real_extension` when available.
- The web softphone selects the normal extension and starts the call.
- The external SIP client detects and ends the incoming call.
- The normal extension is removed through Administration and verified absent in the scoped database.

## Cleanup Rules

Disposable data must be cleaned in `finally` or fixture teardown.

1. Delete through the UI.
2. Publish deletion only when the environment requires Publish.
3. Verify absence using scoped database queries.
4. Use direct database deletion only as a fallback when UI cleanup fails.
5. Never delete by extension number without company and type scope.

## Running

Collect without opening a browser:

```powershell
.venv\Scripts\python.exe -m pytest --collect-only -q
```

Run the focused Extensions suite:

```powershell
.venv\Scripts\python.exe -m pytest tests\modules\administration\test_extensions.py -v -s
```

Run one SIP integration scenario:

```powershell
.venv\Scripts\python.exe -m pytest tests\modules\administration\test_extensions.py::test_single_extension_can_make_call_from_ui -v -s --all-modules
```

Temporarily select another client without editing JSON:

```powershell
$env:TEST_CLIENT="newhzor"
.venv\Scripts\python.exe -m pytest tests\modules\administration\test_extensions.py -v -s --all-modules
Remove-Item Env:TEST_CLIENT
```

## Debugging Checklist

- Confirm `active_client` or `TEST_CLIENT`.
- Confirm `company_name` exactly matches the database value.
- Confirm `extension_type` matches the Add form selection.
- Confirm the database endpoint is reachable.
- Compare `extension` and `real_extension` before debugging SIP registration.
- Confirm the configured softphone provider has a usable executable.
- Read the failed step, one-line failure summary, browser URL, screenshot, and HTML artifact.
- Check cleanup logs and verify no disposable extension remains in the scoped company.

## Adding A New Scenario

1. Write a short test whose body shows business-level steps.
2. Reuse or add workflow methods for repeated actions.
3. Keep locators in the page object.
4. Keep SQL parameterized and company/type scoped.
5. Add cleanup before considering the scenario complete.
6. Add the scenario to this document in the same change.
7. Run collection and the narrowest affected test before the full suite.
