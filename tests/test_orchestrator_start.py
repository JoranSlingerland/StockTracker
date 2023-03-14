"""Test Durable Functions Http Start."""
# pylint: disable=line-too-long

from unittest import mock
import azure.functions as func
import azure.durable_functions as df
from urllib3 import encode_multipart_formdata
import pytest

from orchestartor_start import main

starter = mock.MagicMock()


@pytest.mark.asyncio
async def test_valid_data():
    """Test Durable Functions Http Start."""
    body, header = encode_multipart_formdata(
        {
            "userId": "123",
            "functionName": "stocktracker_orchestrator",
            "daysToUpdate": "all",
        }
    )
    header = {"Content-Type": header}
    # starter = mock.MagicMock()
    mock_request = func.HttpRequest(
        method="POST",
        body=body,
        url="http://localhost:7071/api/orchestrator/start",
        headers=header,
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
        response = await main(mock_request, starter)
        assert response == mock_response


@pytest.mark.asyncio
async def test_invalid_userid():
    """Test Durable Functions Http Start."""
    body, header = encode_multipart_formdata(
        {
            "functionName": "stocktracker_orchestrator",
            "daysToUpdate": "all",
        }
    )
    header = {"Content-Type": header}

    mock_request = func.HttpRequest(
        method="POST",
        body=body,
        url="http://localhost:7071/api/orchestrator/start",
        headers=header,
    )

    excpected_response = func.HttpResponse(
        '{"status": "Please pass a valid user id in the request body"}',
        status_code=400,
    )

    with mock.patch(
        "azure.durable_functions.DurableOrchestrationClient",
        spec=df.DurableOrchestrationClient,
    ):
        response = await main(mock_request, starter)
        assert response.status_code == excpected_response.status_code
        assert response.get_body() == excpected_response.get_body()


@pytest.mark.asyncio
async def test_invalid_function_name():
    """check invalid function name"""
    body, header = encode_multipart_formdata(
        {
            "userId": "123",
            "functionName": "stocktracker_orchestrator1",
            "daysToUpdate": "all",
        }
    )
    header = {"Content-Type": header}

    mock_request = func.HttpRequest(
        method="POST",
        body=body,
        url="http://localhost:7071/api/orchestrator/start",
        headers=header,
    )

    excpected_response = func.HttpResponse(
        '{"status": "Please pass a valid function name in the route parameters"}',
        status_code=400,
    )

    with mock.patch(
        "azure.durable_functions.DurableOrchestrationClient",
        spec=df.DurableOrchestrationClient,
    ):
        response = await main(mock_request, starter)
        assert response.status_code == excpected_response.status_code
        assert response.get_body() == excpected_response.get_body()


@pytest.mark.asyncio
async def test_invalid_days_to_update():
    """check invalid days to update"""
    body, header = encode_multipart_formdata(
        {
            "userId": "123",
            "functionName": "stocktracker_orchestrator",
            "daysToUpdate": "all1",
        }
    )
    header = {"Content-Type": header}

    mock_request = func.HttpRequest(
        method="POST",
        body=body,
        url="http://localhost:7071/api/orchestrator/start",
        headers=header,
    )

    excpected_response = func.HttpResponse(
        '{"status": "Please pass a valid number of days to update or pass all in the route parameters"}',
        status_code=400,
    )

    with mock.patch(
        "azure.durable_functions.DurableOrchestrationClient",
        spec=df.DurableOrchestrationClient,
    ):
        response = await main(mock_request, starter)
        assert response.status_code == excpected_response.status_code
        assert response.get_body() == excpected_response.get_body()
