"""Test  http_orchestrator_start"""

import json
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import azure.durable_functions as df
import azure.functions as func
import pytest

from http_orchestrator_start import main
from shared_code.utils import create_form_func_request

starter = MagicMock()

with open(Path(__file__).parent / "data" / "get_user_data.json", "r") as f:
    mock_get_user_data = json.load(f)


@pytest.mark.asyncio()
@patch("shared_code.utils.get_user")
@patch(
    "azure.durable_functions.DurableOrchestrationClient",
    spec=df.DurableOrchestrationClient,
)
async def test_valid_data(mock, get_user):
    """Test Durable Functions Http Start."""
    req = create_form_func_request(
        {
            "functionName": "stocktracker_orchestrator",
            "daysToUpdate": "all",
        },
        "http://localhost:7071/api/orchestrator/start",
    )

    mock_response = func.HttpResponse(
        body=None, status_code=200, headers={"test": "test"}
    )
    get_user.return_value = mock_get_user_data

    mock.start_new = AsyncMock()
    mock().start_new.return_value = "123"
    mock().create_check_status_response.return_value = mock_response
    response = await main(req, starter)
    assert response == mock_response


@pytest.mark.asyncio()
@patch(
    "azure.durable_functions.DurableOrchestrationClient",
    spec=df.DurableOrchestrationClient,
)
async def test_invalid_function_name(mock):
    """Check invalid function name"""
    req = create_form_func_request(
        {
            "functionName": "stocktracker_orchestrator1",
            "daysToUpdate": "all",
        },
        "http://localhost:7071/api/orchestrator/start",
    )

    expected_response = func.HttpResponse(
        '{"status": "Please pass a valid function name in the route parameters"}',
        status_code=400,
    )

    response = await main(req, starter)
    assert response.status_code == expected_response.status_code
    assert response.get_body() == expected_response.get_body()


@pytest.mark.asyncio()
@patch(
    "azure.durable_functions.DurableOrchestrationClient",
    spec=df.DurableOrchestrationClient,
)
async def test_invalid_days_to_update(mock):
    """Check invalid days to update"""
    req = create_form_func_request(
        {
            "functionName": "stocktracker_orchestrator",
            "daysToUpdate": "all1",
        },
        "http://localhost:7071/api/orchestrator/start",
    )

    expected_response = func.HttpResponse(
        '{"status": "Please pass a valid number of days to update or pass all in the route parameters"}',
        status_code=400,
    )

    response = await main(req, starter)
    assert response.status_code == expected_response.status_code
    assert response.get_body() == expected_response.get_body()
