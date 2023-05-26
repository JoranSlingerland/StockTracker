"""Test http_input_add"""

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import azure.functions as func
from azure.cosmos import ContainerProxy

from http_input_add import main

with open(Path(__file__).parent / "data" / "get_user_data.json", "r") as f:
    mock_get_user_data = json.load(f)


def test_add_invalid_json_body():
    """Test add_item_to_input with invalid json body"""
    req = func.HttpRequest(
        method="POST",
        body={"items": [{"invalid": "json"}]},
        url="/api/add_item_to_input",
    )
    response = main(req)
    assert response.status_code == 400
    assert response.get_body() == b'{"result": "Invalid json body"}'


def test_invalid_transaction():
    """Test add transaction"""
    body = {
        "type": "transaction",
        "items": [
            {
                "date": "2023-03-16T21:25:06.206Z",
                "transaction_type": "Deposit",
            }
        ],
    }

    req = func.HttpRequest(
        method="POST",
        body=json.dumps(body).encode("utf-8"),
        url="/api/add_item_to_input",
    )

    response = main(req)
    assert response.status_code == 400
    assert response.get_body() == b'{"result": "Schema validation failed"}'


def test_invalid_stock():
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
            }
        ],
    }

    req = func.HttpRequest(
        method="POST",
        body=json.dumps(body).encode("utf-8"),
        url="/api/add_item_to_input",
    )

    response = main(req)
    assert response.status_code == 400
    body = response.get_body()
    assert body == b'{"result": "Schema validation failed"}'


@patch("shared_code.utils.get_user")
@patch("shared_code.cosmosdb_module.cosmosdb_container")
def test_stock_without_id(cosmosdb_container_mock, get_user_mock):
    """Test add_item_to_input"""
    body = {
        "type": "stock",
        "items": [
            {
                "symbol": "AMD",
                "date": "2023-03-16T21:41:18.901Z",
                "cost_per_share": 100,
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

    cosmosdb_container_mock.return_value = MagicMock(spec=ContainerProxy)
    get_user_mock.return_value = mock_get_user_data

    response = main(req)

    assert response.status_code == 200
    assert response.mimetype == "application/json"
    assert response.get_body().decode() == '{"result": "done"}'


@patch("shared_code.utils.get_user")
@patch("shared_code.cosmosdb_module.cosmosdb_container")
def test_stock_with_id(cosmosdb_container_mock, get_user_mock):
    """Test add_item_to_input"""
    body = {
        "type": "stock",
        "items": [
            {
                "symbol": "AMD",
                "date": "2023-03-16T21:41:18.901Z",
                "cost_per_share": 100,
                "quantity": 1,
                "transaction_type": "Buy",
                "transaction_cost": 0.5,
                "currency": "USD",
                "domain": "amd.com",
                "id": "123",
            }
        ],
    }

    req = func.HttpRequest(
        method="POST",
        body=json.dumps(body).encode("utf-8"),
        url="/api/add_item_to_input",
    )

    cosmosdb_container_mock.return_value = MagicMock(spec=ContainerProxy)
    get_user_mock.return_value = mock_get_user_data

    response = main(req)

    assert response.status_code == 200
    assert response.mimetype == "application/json"
    assert response.get_body().decode() == '{"result": "done"}'


def test_invalid_type():
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

    response = main(req)
    assert response.status_code == 400
    assert response.get_body() == b'{"result": "Invalid input type"}'
