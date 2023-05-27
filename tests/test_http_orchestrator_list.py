"""Test http_orchestrator_list"""

import json
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import azure.durable_functions as df
import pytest

from http_orchestrator_list import main
from shared_code.utils import create_params_func_request

starter = MagicMock()

with open(Path(__file__).parent / "data" / "get_user_data.json", "r") as f:
    mock_get_user_data = json.load(f)


@pytest.mark.asyncio()
@patch("azure.durable_functions.DurableOrchestrationClient")
async def test_empty_request(df):
    """Test Orchestrator List."""
    req = create_params_func_request(
        url="http://localhost:7071/api/orchestrator/list",
        method="GET",
        params={},
    )
    response = await main(req, starter)
    assert response.status_code == 400
    assert response.get_body() == b'{"error": "Missing days"}'


@pytest.mark.asyncio()
@patch("shared_code.utils.get_user")
@patch(
    "azure.durable_functions.DurableOrchestrationClient",
    spec=df.DurableOrchestrationClient,
)
async def test_no_data(mock_df, get_user):
    """Test Orchestrator List."""
    req = create_params_func_request(
        url="http://localhost:7071/api/orchestrator/list",
        method="GET",
        params={"days": "7", "userId": "123"},
    )
    mock_df.get_status_by = AsyncMock()
    mock_df().get_status_by.return_value = []
    get_user.return_value = mock_get_user_data

    response = await main(req, starter)
    assert response.status_code == 200
    assert response.get_body() == b"[]"


# Define a test case for the Azure Function
@pytest.mark.asyncio()
@patch("shared_code.utils.get_user")
@patch(
    "azure.durable_functions.DurableOrchestrationClient",
    spec=df.DurableOrchestrationClient,
)
async def test_main(mock_client, get_user):
    """Test Orchestrator List."""
    request = create_params_func_request(
        url="http://localhost:7071/api/orchestrator/list",
        method="GET",
        params={"days": "1", "userId": "123"},
    )

    json_1 = MagicMock()
    json_1.to_json.return_value = {
        "name": "stocktracker_orchestrator",
        "instanceId": "a664b3d1c9c84475867853c3f14a584a",
        "createdTime": "2023-03-16T17:07:26.000000Z",
        "lastUpdatedTime": "2023-03-16T17:08:32.000000Z",
        "output": '{"status": "Done"}',
        "input": '["all", "123"]',
        "runtimeStatus": "Completed",
        "customStatus": None,
        "history": None,
    }
    json_2 = MagicMock()
    json_2.to_json.return_value = {
        "name": "get_api_data",
        "instanceId": "a664b3d1c9c84475867853c3f14a584a:0",
        "createdTime": "2023-03-16T17:07:31.000000Z",
        "lastUpdatedTime": "2023-03-16T17:07:34.000000Z",
        "output": {},
        "runtimeStatus": "Completed",
        "customStatus": None,
        "history": None,
    }
    json_3 = MagicMock()
    json_3.to_json.return_value = {
        "name": "stocktracker_orchestrator",
        "instanceId": "a664b3d1c9c84475867853c3f14a584a",
        "createdTime": "2023-03-16T17:07:26.000000Z",
        "lastUpdatedTime": "2023-03-16T17:08:32.000000Z",
        "output": '{"status": "Done"}',
        "input": '["all", "abc"]',
        "runtimeStatus": "Completed",
        "customStatus": None,
        "history": None,
    }

    mock_client.return_value.get_status_by.return_value = [json_1, json_2]
    get_user.return_value = mock_get_user_data

    expected_body = [
        {
            "instanceId": "a664b3d1c9c84475867853c3f14a584a",
            "createdTime": "2023-03-16 17:07:26",
            "lastUpdatedTime": "2023-03-16 17:08:32",
            "runtimeStatus": "Completed",
        }
    ]

    response = await main(request, "test")

    assert response.status_code == 200
    assert response.get_body() == json.dumps(expected_body).encode("utf-8")
