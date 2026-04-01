# Extensions Automation Plan

## Source Inputs

- Business/QA notes from manual exploration of the new Administration > Extensions UI
- TestLink XML suite: `Extension.testsuite-deep (1).xml`
- Existing repo structure: `pytest` + Selenium page objects

## Scope Summary

The Extensions page belongs to the Administration module and should be automated as a configuration workflow for `admin` and `supervisor` roles. It is not a live handling page, so the main automation value is in validating:

- access permissions
- filters and table behavior
- popup behavior and required-field validation
- add/edit/delete flows
- export behavior
- publish persistence
- cloud Asterisk-related number/mobile behavior where the environment supports it

## Proposed Test Structure

- `tests/pages/extensions_page.py`
  - page object for search, table, popups, row actions, export, pagination, publish
- `tests/modules/administration/__init__.py`
- `tests/modules/administration/test_extensions_smoke.py`
  - safe, non-destructive coverage
- `tests/modules/administration/test_extensions_crud.py`
  - add/edit/delete/mobile flows
- `tests/modules/administration/test_extensions_export_publish.py`
  - export and publish checks

## Role Model

- `admin`: should have access
- `supervisor`: should have access
- `agent`: should not have access

Note: this differs from the current `test_auth_regression.py` expectation, which treats `supervisor` as denied for Administration. That test should be corrected before or alongside Extensions implementation.

## Priority Order

### Phase 1: Safe and stable UI automation

Automate first because these are low-risk and useful on every run:

- TC-808: navigation and page opens correctly
- TC-3033: search returns matching result
- TC-3034: empty search returns full list
- TC-3035: clear filters resets search
- TC-3036: visible columns can be changed
- TC-3039: edit popup opens with existing data
- TC-3040: edit generate password hides password field
- TC-3043: add popup opens correctly
- TC-3044: add required-field validation
- TC-3045: add generate password hides password field
- TC-3047: mobile popup opens
- TC-3052: bottom delete popup opens
- TC-3055: pagination works

### Phase 2: Data-changing regression flows

Automate next, but preferably with dedicated test data:

- TC-3041: existing extension can be edited successfully
- TC-3042: cancel in edit keeps original values
- TC-3046: new extension range can be added successfully
- TC-3048: number can be added and active phone selected
- TC-3049: cancel in mobile keeps data unchanged
- TC-3050: cancel in row delete keeps record
- TC-3051: row delete removes selected extension
- TC-3053: cancel in bottom delete keeps range
- TC-3054: bottom delete removes selected range
- TC-3056: publish applies saved changes successfully

### Phase 3: High-value bug/regression coverage

These are not fully represented in the XML, but they should be added because your notes already identified them as risky:

- export ignores selected visible columns
- export should include all pages, not just current page
- mobile popup title shows raw key `DYNAMIC.ACTIONS.MOBILE`
- number attached through mobile popup may be reset after password update
- reopened record should preserve linked number unless explicitly changed
- `Real Ext` and `Number` assertions should be conditional for cloud Asterisk environments

## Automation Preconditions

To keep the suite reliable, add environment-aware guards for these cases:

- skip mobile/number tests if cloud Asterisk behavior is unavailable
- skip multi-page export assertions if the table has only one page
- skip destructive delete tests unless dedicated removable data exists
- skip publish mutation tests unless the environment is intended for configuration changes

## Recommended Config Additions

The current config supports credentials and module flags, but Extensions automation will benefit from dedicated data inputs in `config/test_config.json`, for example:

```json
{
  "clients": {
    "kube1": {
      "administration": {
        "extensions": {
          "page_path": "/zz-portal/administration/extensions",
          "search_extension": "1001",
          "editable_extension": "1001",
          "range_start": "7100",
          "range_end": "7102",
          "deletable_range_start": "7100",
          "deletable_range_end": "7102",
          "mobile_test_number": "37499000111",
          "supports_cloud_asterisk": true,
          "allow_publish_mutation": false
        }
      }
    }
  }
}
```

This allows the tests to stay data-driven and prevents hardcoding unstable values.

## Page Object Capabilities Needed

`ExtensionsPage` should expose helpers for:

- open page directly
- assert main controls are visible
- search by extension
- clear filters
- read row count / total count
- inspect visible table headers
- toggle column visibility
- open edit popup for a row
- open mobile popup for a row
- open row delete confirmation for a row
- open add popup
- open bottom delete popup
- click publish
- paginate and change page size
- export and wait for downloaded file

Popup helpers will likely be clearer if split into modal classes:

- `ExtensionEditModal`
- `ExtensionAddModal`
- `ExtensionMobileModal`
- `ExtensionDeleteRangeModal`

## Execution Strategy

Recommended run layers:

- smoke:
  - navigation
  - search
  - clear filters
  - columns
  - popup open/close
  - validation
- regression:
  - edit persistence
  - add range
  - mobile assignment
  - export file validation
  - pagination
- controlled admin run:
  - row delete
  - bottom range delete
  - publish

## Immediate Next Steps

1. Correct the existing Administration access expectation so `supervisor` is allowed.
2. Add config data for Extensions-specific test values.
3. Implement `tests/pages/extensions_page.py`.
4. Implement the Phase 1 smoke scenarios first.
5. Add destructive and publish flows only behind explicit config guards.

