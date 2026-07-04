import os

import pytest

from tests.helpers.reabe_api_helper import ReaBeClient


@pytest.mark.integration
def test_reabe_api_smoke():
    client = ReaBeClient.from_env()
    if client is None:
        pytest.skip("Set REABE_BASE_URL and optionally REABE_API_TOKEN/REABE_API_ENDPOINT to run the ReaBe API smoke test.")

    endpoint = os.getenv("REABE_API_ENDPOINT", "/")
    response = client.get(endpoint)

    assert response.status_code == 200, f"Expected HTTP 200 from ReaBe endpoint {endpoint}, got {response.status_code}."
    assert response.text.strip(), "ReaBe response body was empty."
