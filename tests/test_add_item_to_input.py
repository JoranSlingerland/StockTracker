"""Test add_item_to_input.py"""
import json
from unittest.mock import AsyncMock, MagicMock, patch

import azure.functions as func
import pytest
from azure.cosmos import ContainerProxy

from add_item_to_input import main


@pytest.mark.asyncio()
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


@pytest.mark.asyncio()
async def test_invalid_transaction():
    """Test add transaction"""
    body = {
        "type": "transaction",
        "items": [
            {
                "date": "2023-03-16T21:25:06.206Z",
                "transaction_type": "Deposit",
                "userid": "123",
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


@pytest.mark.asyncio()
async def test_invalid_stock():
    """Test add stock"""
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
                "userid": "123",
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


@pytest.mark.asyncio()
@patch("shared_code.cosmosdb_module.cosmosdb_container")
async def test_main(cosmosdb_container_mock):
    """Test add_item_to_input"""
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
                "userid": "123",
            }
        ],
    }

    req = func.HttpRequest(
        method="POST",
        body=json.dumps(body).encode("utf-8"),
        url="/api/add_item_to_input",
    )

    cosmosdb_container_mock.return_value = MagicMock(spec=ContainerProxy)
    cosmosdb_container_mock.return_value.create_item = AsyncMock()

    response = await main(req)

    assert response.status_code == 200
    assert response.mimetype == "application/json"
    assert response.get_body().decode() == '{"result": "done"}'


@pytest.mark.asyncio()
async def test_invalid_type():
    """Test add_item_to_input with invalid type"""
    body = {
        "type": "invalid",
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
    assert response.get_body() == b'{"result": "Invalid input type"}'
