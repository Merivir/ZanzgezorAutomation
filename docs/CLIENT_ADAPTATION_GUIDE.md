# Client Adaptation Guide

This guide explains how to adapt the automation framework to a new client or environment without adding client-specific logic to test cases.

## 1. Adaptation Principles

- Keep test scenarios readable and independent from client configuration.
- Put environment differences in configuration, fixtures, and reusable helpers.
- Use page objects for browser interactions and softphone adapters for SIP interactions.
- Preserve manual test-case IDs and titles so automated results remain traceable.
- Do not change database schema, permissions, or production data as part of test setup.
- Create and remove test data through the UI by default. Any database mutation requires explicit client authorization.
- Keep credentials and tokens out of Git.

## 2. Information Required From the Client

Collect the following before adapting the project:

| Area | Required information |
| --- | --- |
| Environment | Client key, base URL, environment type, and enabled modules |
| Authentication | Test users, roles, login method, logout behavior, and session restrictions |
| Company | Exact company name used by the application and database |
| Database | Host, database name, read-only user, network/VPN requirements, and table ownership |
| Extensions | Supported extension types, transport, password policy, and real-extension behavior |
| Telephony | SIP server, allowed test numbers, routing rules, codecs, and expected call states |
| Test data | Records that may be created, edited, published, and deleted |
| Test catalogue | TestLink/XML export, case IDs, priorities, and cases that must remain manual |
| Execution | Supported OS, browser, CI runner, reporting destination, and schedule |

Never place real passwords, access tokens, or private keys in example configuration files.

## 3. Recommended Configuration Model

Add one named client profile. Test code should select the profile through `TEST_CLIENT` and should not contain client names or URL checks.

```json
{
  "clients": {
    "client_key": {
      "base_url": "https://client.example",
      "extensions": {
        "cloud_related": false,
        "sip_check_enabled": true,
        "pjsip_supported": true,
        "webrtc_supported": false,
        "company_name": "exact-company-name",
      },
      "modules": {
        "administration": true,
        "calls": true
      },
      "database": {
        "host": "configured-locally",
        "name": "configured-locally",
        "read_only": true
      }
    }
  }
}
```

Keep safe defaults in the tracked example file. Store local environment values in the ignored local configuration or environment variables.

Do not configure one global extension type. Each workflow supplies its own type explicitly: `pjsip` for PJSIP scenarios and `webrtc` for WebRTC scenarios.

## 4. Architecture To Preserve

Use these ownership boundaries when adding a client or module:

```text
tests/modules/        readable business scenarios and assertions
tests/pages/          browser locators and Selenium interactions
tests/helpers/        reusable steps, workflows, parsers, and assertions
tests/helpers/softphones/
                      provider-neutral telephony interface and adapters
tests/db/             parameterized read queries and approved cleanup helpers
tests/config/         profile loading and validation
tests/conftest.py     fixtures, lifecycle, reporting, artifacts, and markers
docs/                 onboarding and module behavior
```

A test should read like a manual scenario:

```python
@testcase("111390", "Verify incoming call can be declined")
@pytest.mark.calls
@pytest.mark.integration
def test_incoming_call_can_be_declined(call_page, softphone):
    prepare_available_user(call_page)
    start_incoming_call(softphone)
    verify_incoming_call_is_visible(call_page)
    decline_incoming_call(softphone)
    verify_user_returns_to_available(call_page)
```

Details such as locators, retries, SIP commands, and data conversion belong in their corresponding layers, not inside the test.

## 5. Extension And SIP Identity Rules

Do not build SIP usernames with a hardcoded prefix.

1. Scope extension queries by exact company name and extension type.
2. Select the next administration extension from the `extension` field.
3. Add and select that same short extension in the administration and web UI.
4. After creation, read the saved `extension` and `real_extension` values.
5. Configure the SIP client with `real_extension` when it is present; otherwise use `extension`.
6. Treat a populated `real_extension` as evidence that Publish is required before SIP registration or calling.
7. After deleting a published extension through the UI, Publish again so telephony receives the deletion.

Database reads support test-data selection and verification only. They must not alter schema or permissions.

## 6. Adapting A Manual Test Catalogue

The supplied call catalogue currently contains **120 test cases** in five suites:

- Calls
- Call Statuses
- Hold / Mute features
- Call Resolution
- Calls tab

For each imported case, preserve the source `internalid` as test metadata and preserve its business title. Then classify it before implementation:

| Category | Typical automation |
| --- | --- |
| UI only | Selenium page objects and UI assertions |
| UI plus SIP | Selenium plus PJSUA or another softphone adapter |
| Status/reporting | UI action followed by API, UI, or approved read-only DB verification |
| Multi-user | Separate browser sessions and separate SIP accounts |
| Performance/concurrency | Dedicated load or SIP scenario tool, outside normal Selenium regression |
| Manual | Audio quality, physical device behavior, sleep mode, or behavior without a controllable endpoint |

Do not automate every manual step literally. Automate the business outcome at the lowest reliable layer while retaining visible test steps in the pytest scenario.

## 7. Softphone Adaptation

Tests should depend on a common softphone contract rather than one executable. A provider should support only the capabilities it can reliably control:

- configure or register an account
- wait for registration
- originate a call
- wait for an incoming call
- answer, reject, or hang up
- hold, resume, mute, and unmute when supported
- expose concise logs and call state
- stop processes and release resources during teardown

Keep provider-specific command syntax inside its adapter. Mark a test skipped with a clear reason when the selected provider does not support a required capability.

## 8. Markers And Environment Selection

Use markers to describe requirements, not client names:

```python
@pytest.mark.calls
@pytest.mark.integration
@pytest.mark.cloud_related
@pytest.mark.requires_pjsip
@pytest.mark.requires_webrtc
```

- `cloud_related`: collect or run only when the selected profile enables cloud behavior.
- `requires_pjsip`: run only when the selected profile has `pjsip_supported: true`.
- `requires_webrtc`: run only when the selected profile has `webrtc_supported: true`.
- `integration`: requires browser plus external services such as SIP or database connectivity.
- module markers such as `calls` or `extensions`: allow focused execution.

Example commands in PowerShell:

```powershell
$env:TEST_CLIENT = "client_key"
python -m pytest --collect-only -q
python -m pytest -v -s -m calls
python -m pytest -v -s tests/modules/administration/test_extensions.py
```

Run one smoke scenario before the full suite.

## 9. Client Onboarding Procedure

1. Confirm scope, supported modules, roles, and acceptance criteria.
2. Add a client profile without changing shared test behavior.
3. Configure secrets locally and verify VPN, application, database, and SIP connectivity.
4. Run collection and confirm cloud-related cases are selected correctly.
5. Run login/logout smoke tests and verify the session is actually closed.
6. Validate read-only company and extension lookup.
7. Validate one SIP account registration using the resolved SIP identity.
8. Run one complete create, publish-if-required, call, hang-up, delete, and republish-if-required workflow.
9. Confirm teardown leaves no browser sessions, SIP processes, calls, or test records.
10. Expand execution by module and record unsupported manual cases.

## 10. Logging And Failure Evidence

Logs should let a QA engineer reproduce the failure without reading implementation code. Each action should state:

- what is being opened, entered, selected, or verified
- what condition is being awaited and its timeout
- how long the condition took
- the exact failed step and a one-line problem summary
- the browser URL and title for UI failures
- the screenshot and HTML artifact paths
- SIP registration and call-state summaries without passwords
- skipped test names and reasons

Reset the failure-artifact directory at the beginning of a run and retain one screenshot and HTML snapshot per failed UI test.

## 11. Definition Of Done

A client adaptation is ready when:

- configuration contains no committed secrets
- no client name or URL is hardcoded in test scenarios
- login and logout work reliably
- company-scoped test data is selected correctly
- SIP identity is resolved from saved data rather than a prefix rule
- Publish behavior is derived from environment data
- one complete call lifecycle passes
- created data and external processes are cleaned up after pass or failure
- cloud-only and unsupported tests are selected or skipped clearly
- failure reports are readable and include artifacts
- client-specific setup and remaining manual coverage are documented

## 12. Change Control

When adapting another client, update configuration and documentation first. Add shared code only when the behavior represents a reusable capability. Record true client exceptions explicitly and keep them out of individual test bodies.

Any request to mutate database data, change permissions, modify schema, or test against production requires written client approval before execution.
