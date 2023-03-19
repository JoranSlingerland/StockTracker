"""Test Durable Functions Http Start."""

from unittest import mock

import azure.durable_functions as df
import azure.functions as func
import pytest

from orchestartor_start import main
from shared_code.utils import create_form_func_request

starter = mock.MagicMock()


@pytest.mark.asyncio()
async def test_valid_data():
    """Test Durable Functions Http Start."""
    req = create_form_func_request(
        {
            "userId": "123",
            "functionName": "stocktracker_orchestrator",
            "daysToUpdate": "all",
        },
        "http://localhost:7071/api/orchestrator/start",
    )

    mock_response = func.HttpResponse(
        body=None, status_code=200, headers={"test": "test"}
    )

    with mock.patch(
        "azure.durable_functions.DurableOrchestrationClient",
        spec=df.DurableOrchestrationClient,
    ) as a_mock:
        a_mock.start_new = mock.AsyncMock()
        a_mock().start_new.return_value = "123"
        a_mock().create_check_status_response.return_value = mock_response
        response = await main(req, starter)
        assert response == mock_response


@pytest.mark.asyncio()
async def test_invalid_userid():
    """Test Durable Functions Http Start."""
    req = create_form_func_request(
        {
            "functionName": "stocktracker_orchestrator",
            "daysToUpdate": "all",
        },
        "http://localhost:7071/api/orchestrator/start",
    )

    excpected_response = func.HttpResponse(
        '{"status": "Please pass a valid user id in the request body"}',
        status_code=400,
    )

    with mock.patch(
        "azure.durable_functions.DurableOrchestrationClient",
        spec=df.DurableOrchestrationClient,
    ):
        response = await main(req, starter)
        assert response.status_code == excpected_response.status_code
        assert response.get_body() == excpected_response.get_body()


@pytest.mark.asyncio()
async def test_invalid_function_name():
    """Check invalid function name"""
    req = create_form_func_request(
        {
            "userId": "123",
            "functionName": "stocktracker_orchestrator1",
            "daysToUpdate": "all",
        },
        "http://localhost:7071/api/orchestrator/start",
    )

    excpected_response = func.HttpResponse(
        '{"status": "Please pass a valid function name in the route parameters"}',
        status_code=400,
    )

    with mock.patch(
        "azure.durable_functions.DurableOrchestrationClient",
        spec=df.DurableOrchestrationClient,
    ):
        response = await main(req, starter)
        assert response.status_code == excpected_response.status_code
        assert response.get_body() == excpected_response.get_body()


@pytest.mark.asyncio()
async def test_invalid_days_to_update():
    """Check invalid days to update"""
    req = create_form_func_request(
        {
            "userId": "123",
            "functionName": "stocktracker_orchestrator",
            "daysToUpdate": "all1",
        },
        "http://localhost:7071/api/orchestrator/start",
    )

    excpected_response = func.HttpResponse(
        '{"status": "Please pass a valid number of days to update or pass all in the route parameters"}',
        status_code=400,
    )

    with mock.patch(
        "azure.durable_functions.DurableOrchestrationClient",
        spec=df.DurableOrchestrationClient,
    ):
        response = await main(req, starter)
        assert response.status_code == excpected_response.status_code
        assert response.get_body() == excpected_response.get_body()
