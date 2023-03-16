"""Test add_item_to_input.py"""
# pylint: disable=line-too-long

from unittest.mock import Mock
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
async def test_add_stock():
    """test add stock"""
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

    # mock azure.cosmos.aio.CosmosClient
    mock_cosmos_client = Mock()
    mock_cosmos_client.get_database_client.return_value = Mock()
    mock_cosmos_client.get_database_client.return_value.get_container_client.return_value = (
        Mock()
    )
    mock_cosmos_client.get_database_client.return_value.get_container_client.return_value.insert_item.return_value = (
        Mock()
    )

    response = await main(req)
    assert response.status_code == 200
    body = response.get_body()
    assert body == b'{"result": "done"}'
