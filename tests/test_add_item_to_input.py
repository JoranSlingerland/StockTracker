"""Test add_item_to_input.py"""
from unittest.mock import MagicMock, patch
import json
import pytest
import azure.functions as func
from add_item_to_input import main


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


@pytest.mark.asyncio
@patch("shared_code.get_config.get_cosmosdb")
@patch("azure.cosmos.aio.CosmosClient")
async def test_main(cosmos_client_mock, get_cosmosdb_mock):
    """test add_item_to_input"""
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

    cosmosdb_config = {
        "endpoint": "test-endpoint",
        "key": "test-key",
        "database": "test-db",
    }
    get_cosmosdb_mock.return_value = cosmosdb_config

    cosmos_db_mock = MagicMock()
    cosmos_client_mock.return_value = cosmos_db_mock

    container_mock = MagicMock()
    cosmos_db_mock.get_container_client.return_value = container_mock

    response = await main(req)

    assert response.status_code == 200
    assert response.mimetype == "application/json"
    assert response.get_body().decode() == '{"result": "done"}'
