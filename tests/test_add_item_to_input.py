"""Test add_item_to_input.py"""
# pylint: disable=line-too-long

from unittest.mock import Mock, MagicMock, patch, AsyncMock
from azure.cosmos.aio import CosmosClient
import json
import pytest
from shared_code import get_config
import azure.functions as func
from add_item_to_input import main

from asyncio import Future


@pytest.mark.asyncio
async def test_add_invalid_json_body():
    """Test add_item_to_input with invalid json body"""
    req = func.HttpRequest(
        method="POST",
        body={"items": [{"invalid": "json"}]},
        url="/api/add_item_to_input",
    )
    response = await main(req)
    assert response.status_code == 400
    assert response.get_body() == b'{"result": "Invalid json body"}'


@pytest.mark.asyncio
async def test_invalid_transaction():
    """test add transaction"""
    body = {
        "type": "transaction",
        "items": [
            {
                "date": "2023-03-16T21:25:06.206Z",
                "transaction_type": "Deposit",
                "userid": "2e43b4a359f8d5bb81550495b114e9e3",
            }
        ],
    }

    req = func.HttpRequest(
        method="POST",
        body=json.dumps(body).encode("utf-8"),
        url="/api/add_item_to_input",
    )

    response = await main(req)
    assert response.status_code == 400
    assert response.get_body() == b'{"result": "Schema validation failed"}'


@pytest.mark.asyncio
async def test_invalid_stock():
    """test add stock"""
    body = {
        "type": "stock",
        "items": [
            {
                "date": "2023-03-16T21:41:18.901Z",
                "cost": 100,
                "quantity": 1,
                "transaction_type": "Buy",
                "transaction_cost": 0.5,
                "currency": "USD",
                "domain": "amd.com",
                "userid": "2e43b4a359f8d5bb81550495b114e9e3",
            }
        ],
    }

    req = func.HttpRequest(
        method="POST",
        body=json.dumps(body).encode("utf-8"),
        url="/api/add_item_to_input",
    )

    response = await main(req)
    assert response.status_code == 400
    body = response.get_body()
    assert body == b'{"result": "Schema validation failed"}'


# @pytest.mark.asyncio
# @patch("shared_code.aio_helper.gather_with_concurrency")
# @patch("add_item_to_input.CosmosClient", new_callable=AsyncMock)
# @patch("shared_code.get_config.get_cosmosdb")
# async def test_add_stock(mock_get_cosmosdb, mock_cosmos_client, mock_gather):
#     """test add stock"""
#     body = {
#         "type": "stock",
#         "items": [
#             {
#                 "symbol": "AMD",
#                 "date": "2023-03-16T21:41:18.901Z",
#                 "cost": 100,
#                 "quantity": 1,
#                 "transaction_type": "Buy",
#                 "transaction_cost": 0.5,
#                 "currency": "USD",
#                 "domain": "amd.com",
#                 "userid": "2e43b4a359f8d5bb81550495b114e9e3",
#             }
#         ],
#     }

#     req = func.HttpRequest(
#         method="POST",
#         body=json.dumps(body).encode("utf-8"),
#         url="/api/add_item_to_input",
#     )

#     # mock_get_cosmosdb = MagicMock()
#     # mock_get_cosmosdb.get_cosmosdb.return_value = {
#     #     "endpoint": "https://localhost:8081",
#     #     "key": "123",
#     #     "database": "test",
#     #     "offer_throughput": 400,
#     # }

#     mock_get_cosmosdb = MagicMock()
#     mock_get_cosmosdb.return_value = {
#         "endpoint": "https://localhost:8081",
#         "key": "123",
#         "database": "test",
#         "offer_throughput": 400,
#     }

#     # mock_insert_item = Mock()
#     # mock_insert_item.return_value = "done"

#     # mock_container = Mock()
#     # mock_container.insert_item = mock_insert_item

#     mock_database = Mock()
#     mock_database.get_container_client.return_value = "test"

#     # mock_cosmos_client.return_value = Mock()
#     mock_cosmos_client.get_database_client.return_value = mock_database

#     mock_gather = AsyncMock()
#     mock_gather.return_value = "done"
#     mock_cosmos_client.return_value.return_value.close = AsyncMock()

#     # mock get_config and cosmos client
#     response = await main(req)
#     assert response.status_code == 200
#     body = response.get_body()
#     assert body == b'{"result": "done"}'


@pytest.mark.asyncio
@patch("shared_code.get_config.get_cosmosdb")
@patch("azure.cosmos.aio.CosmosClient")
async def test_main(cosmos_client_mock, get_cosmosdb_mock):
    # Set up input data for the function
    body = {
        "type": "stock",
        "items": [
            {
                "symbol": "AMD",
                "date": "2023-03-16T21:41:18.901Z",
                "cost": 100,
                "quantity": 1,
                "transaction_type": "Buy",
                "transaction_cost": 0.5,
                "currency": "USD",
                "domain": "amd.com",
                "userid": "2e43b4a359f8d5bb81550495b114e9e3",
            }
        ],
    }

    req = func.HttpRequest(
        method="POST",
        body=json.dumps(body).encode("utf-8"),
        url="/api/add_item_to_input",
    )

    # Set up mock objects for the function
    cosmosdb_config = {
        "endpoint": "test-endpoint",
        "key": "test-key",
        "database": "test-db",
    }
    get_cosmosdb_mock.return_value = cosmosdb_config

    cosmos_db_mock = MagicMock()
    cosmos_client_mock.return_value = cosmos_db_mock

    # Set up mock containers for the function
    container_mock = MagicMock()
    cosmos_db_mock.get_container_client.return_value = container_mock

    # Call the function and get the response
    response = await main(req)

    # Assert that the response is correct
    assert response.status_code == 200
    assert response.mimetype == "application/json"
    assert response.get_body().decode() == '{"result": "done"}'
