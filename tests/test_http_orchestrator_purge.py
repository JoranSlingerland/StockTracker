"""Test http_orchestrator_purge"""

import json
from copy import deepcopy
from pathlib import Path
from unittest.mock import MagicMock, patch

import azure.durable_functions as df
import pytest

from http_orchestrator_purge import main
from shared_code.utils import create_params_func_request

starter = MagicMock()

with open(Path(__file__).parent / "data" / "get_user_data.json", "r") as f:
    mock_get_user_data = json.load(f)

get_status = MagicMock()
get_status.to_json.return_value = {
    "name": "stocktracker_orchestrator",
    "instanceId": "123",
    "createdTime": "2023-03-16T17:07:26.000000Z",
    "lastUpdatedTime": "2023-03-16T17:08:32.000000Z",
    "output": '{"status": "Done"}',
    "input": '["all", "123"]',
    "runtimeStatus": "Running",
    "customStatus": None,
    "history": None,
}


@pytest.mark.asyncio()
@patch("azure.durable_functions.DurableOrchestrationClient")
async def test_empty_request(mock_df):
    """Test Orchestrator Purge."""
    req = create_params_func_request(
        url="http://localhost:7071/api/orchestrator/purge",
        method="DELETE",
        params={},
    )
    response = await main(req, starter)
    assert response.status_code == 400
    assert response.get_body() == b'{"error": "Missing instanceId"}'


@pytest.mark.asyncio()
@patch("shared_code.utils.get_user")
@patch(
    "azure.durable_functions.DurableOrchestrationClient",
    spec=df.DurableOrchestrationClient,
)
async def test_no_data(mock_df, get_user):
    """Test Orchestrator Purge."""
    req = create_params_func_request(
        url="http://localhost:7071/api/orchestrator/purge",
        method="DELETE",
        params={"instanceId": "123"},
    )

    custom_get_status = deepcopy(get_status)
    custom_get_status.to_json.return_value = {}
    mock_df.return_value.get_status.return_value = custom_get_status
    get_user.return_value = mock_get_user_data

    response = await main(req, starter)
    assert response.status_code == 401
    assert response.get_body() == b'{"status": "Not authorized to purge this instance"}'


@pytest.mark.asyncio()
@patch("shared_code.utils.get_user")
@patch(
    "azure.durable_functions.DurableOrchestrationClient",
    spec=df.DurableOrchestrationClient,
)
async def test_unauthorized(mock_df, get_user):
    """Test Orchestrator Purge."""
    req = create_params_func_request(
        url="http://localhost:7071/api/orchestrator/purge",
        method="DELETE",
        params={"instanceId": "123"},
    )

    mock_df.return_value.get_status.return_value = get_status
    custom_get_user_data = deepcopy(mock_get_user_data)
    custom_get_user_data["userId"] = "unauthorized"
    get_user.return_value = custom_get_user_data

    response = await main(req, starter)
    assert response.status_code == 401
    assert response.get_body() == b'{"status": "Not authorized to purge this instance"}'


@pytest.mark.asyncio()
@patch("shared_code.utils.get_user")
@patch(
    "azure.durable_functions.DurableOrchestrationClient",
    spec=df.DurableOrchestrationClient,
)
async def test_invalid_json(mock_df, get_user):
    """Test Orchestrator Purge."""
    req = create_params_func_request(
        url="http://localhost:7071/api/orchestrator/purge",
        method="DELETE",
        params={"instanceId": "123"},
    )

    custom_get_status = deepcopy(get_status)
    custom_get_status.to_json.side_effect = AttributeError()
    mock_df.return_value.get_status.return_value = custom_get_status
    get_user.return_value = mock_get_user_data

    response = await main(req, starter)
    assert response.status_code == 404
    assert response.get_body() == b'{"status": "Instance not found"}'


@pytest.mark.asyncio()
@patch("shared_code.utils.get_user")
@patch(
    "azure.durable_functions.DurableOrchestrationClient",
    spec=df.DurableOrchestrationClient,
)
async def test_failed_purge(mock_df, get_user):
    """Test Orchestrator Purge."""
    req = create_params_func_request(
        url="http://localhost:7071/api/orchestrator/purge",
        method="DELETE",
        params={"instanceId": "123"},
    )

    mock_df.return_value.get_status.return_value = get_status
    mock_df.return_value.purge_instance_history.side_effect = Exception()
    get_user.return_value = mock_get_user_data

    response = await main(req, starter)
    assert response.status_code == 500
    assert response.get_body() == b'{"status": "Error purging instance"}'


@pytest.mark.asyncio()
@patch("shared_code.utils.get_user")
@patch(
    "azure.durable_functions.DurableOrchestrationClient",
    spec=df.DurableOrchestrationClient,
)
async def test_zero_instances_purged(mock_df, get_user):
    """Test Orchestrator Purge."""
    req = create_params_func_request(
        url="http://localhost:7071/api/orchestrator/purge",
        method="DELETE",
        params={"instanceId": "123"},
    )

    mock_df.return_value.get_status.return_value = get_status
    mock_df.return_value.purge_instance_history.return_value.instances_deleted = 0
    get_user.return_value = mock_get_user_data

    response = await main(req, starter)
    assert response.status_code == 500
    assert response.get_body() == b'{"status": "Instance could not be purged"}'


@pytest.mark.asyncio()
@patch("shared_code.utils.get_user")
@patch(
    "azure.durable_functions.DurableOrchestrationClient",
    spec=df.DurableOrchestrationClient,
)
async def test_valid_purge(mock_df, get_user):
    """Test Orchestrator Purge."""
    req = create_params_func_request(
        url="http://localhost:7071/api/orchestrator/purge",
        method="DELETE",
        params={"instanceId": "123"},
    )

    mock_df.return_value.get_status.return_value = get_status
    mock_df.return_value.purge_instance_history.return_value.instances_deleted = 1
    get_user.return_value = mock_get_user_data

    response = await main(req, starter)
    assert response.status_code == 200
    assert response.get_body() == b'{"status": "Instance purged"}'
