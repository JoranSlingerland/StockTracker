"""Test Orchestrator purge."""

from copy import deepcopy
from unittest.mock import MagicMock, patch

import azure.durable_functions as df
import pytest

from orchestrator_purge import main
from shared_code.utils import create_form_func_request

starter = MagicMock()

get_status = MagicMock()
get_status.to_json.return_value = {
    "name": "stocktracker_orchestrator",
    "instanceId": "123",
    "createdTime": "2023-03-16T17:07:26.000000Z",
    "lastUpdatedTime": "2023-03-16T17:08:32.000000Z",
    "output": '{"status": "Done"}',
    "input": '["all", "456"]',
    "runtimeStatus": "Running",
    "customStatus": None,
    "history": None,
}


@pytest.mark.asyncio()
@patch("azure.durable_functions.DurableOrchestrationClient")
async def test_empty_request(mock_df):
    """Test Orchestrator Purge."""
    req = create_form_func_request({}, "http://localhost:7071/api/orchestrator/purge")
    response = await main(req, starter)
    assert response.status_code == 400
    assert response.get_body() == b'{"error": "Missing instanceId or userId"}'


@pytest.mark.asyncio()
@patch(
    "azure.durable_functions.DurableOrchestrationClient",
    spec=df.DurableOrchestrationClient,
)
async def test_no_data(mock_df):
    """Test Orchestrator Purge."""
    req = create_form_func_request(
        {"instanceId": "123", "userId": "456"},
        "http://localhost:7071/api/orchestrator/purge",
    )

    custom_get_status = deepcopy(get_status)
    custom_get_status.to_json.return_value = {}
    mock_df.return_value.get_status.return_value = custom_get_status

    response = await main(req, starter)
    assert response.status_code == 401
    assert response.get_body() == b'{"status": "Not authorized to purge this instance"}'


@pytest.mark.asyncio()
@patch(
    "azure.durable_functions.DurableOrchestrationClient",
    spec=df.DurableOrchestrationClient,
)
async def test_unauthorized(mock_df):
    """Test Orchestrator Purge."""
    req = create_form_func_request(
        {"instanceId": "123", "userId": "unauthorized"},
        "http://localhost:7071/api/orchestrator/purge",
    )

    mock_df.return_value.get_status.return_value = get_status

    response = await main(req, starter)
    assert response.status_code == 401
    assert response.get_body() == b'{"status": "Not authorized to purge this instance"}'


@pytest.mark.asyncio()
@patch(
    "azure.durable_functions.DurableOrchestrationClient",
    spec=df.DurableOrchestrationClient,
)
async def test_invalid_json(mock_df):
    """Test Orchestrator Purge."""
    req = create_form_func_request(
        {"instanceId": "123", "userId": "456"},
        "http://localhost:7071/api/orchestrator/purge",
    )

    custom_get_status = deepcopy(get_status)
    custom_get_status.to_json.side_effect = AttributeError()
    mock_df.return_value.get_status.return_value = custom_get_status

    response = await main(req, starter)
    assert response.status_code == 404
    assert response.get_body() == b'{"status": "Instance not found"}'


@pytest.mark.asyncio()
@patch(
    "azure.durable_functions.DurableOrchestrationClient",
    spec=df.DurableOrchestrationClient,
)
async def test_failed_purge(mock_df):
    """Test Orchestrator Purge."""
    req = create_form_func_request(
        {"instanceId": "123", "userId": "456"},
        "http://localhost:7071/api/orchestrator/purge",
    )

    mock_df.return_value.get_status.return_value = get_status
    mock_df.return_value.purge_instance_history.side_effect = Exception()

    response = await main(req, starter)
    assert response.status_code == 500
    assert response.get_body() == b'{"status": "Error purging instance"}'


@pytest.mark.asyncio()
@patch(
    "azure.durable_functions.DurableOrchestrationClient",
    spec=df.DurableOrchestrationClient,
)
async def test_zero_instances_purged(mock_df):
    """Test Orchestrator Purge."""
    req = create_form_func_request(
        {"instanceId": "123", "userId": "456"},
        "http://localhost:7071/api/orchestrator/purge",
    )

    mock_df.return_value.get_status.return_value = get_status
    mock_df.return_value.purge_instance_history.return_value.instances_deleted = 0

    response = await main(req, starter)
    assert response.status_code == 500
    assert response.get_body() == b'{"status": "Instance could not be purged"}'


@pytest.mark.asyncio()
@patch(
    "azure.durable_functions.DurableOrchestrationClient",
    spec=df.DurableOrchestrationClient,
)
async def test_valid_purge(mock_df):
    """Test Orchestrator Purge."""
    req = create_form_func_request(
        {"instanceId": "123", "userId": "456"},
        "http://localhost:7071/api/orchestrator/purge",
    )

    mock_df.return_value.get_status.return_value = get_status
    mock_df.return_value.purge_instance_history.return_value.instances_deleted = 1

    response = await main(req, starter)
    assert response.status_code == 200
    assert response.get_body() == b'{"status": "Instance purged"}'
