"""Test http_input_delete"""

import json
from pathlib import Path
from unittest.mock import patch

import azure.functions as func
from azure.cosmos import exceptions

from http_input_delete import main

body = {
    "itemIds": ["123"],
    "container": "input_invested",
}

with open(Path(__file__).parent / "data" / "get_user_data.json", "r") as f:
    mock_get_user_data = json.load(f)


def test_empty_request():
    """Test empty request"""
    req = func.HttpRequest(
        method="POST",
        body=json.dumps({}).encode("utf-8"),
        url="/api/delete/delete_input_items",
    )
    response = main(req)
    assert response.status_code == 400
    assert response.get_body() == b'{"result": "Invalid json body"}'


@patch("shared_code.utils.get_user")
@patch("shared_code.cosmosdb_module.cosmosdb_container")
def test_valid_request(cosmosdb_container_mock, get_user_mock):
    """Test valid request"""
    req = func.HttpRequest(
        method="POST",
        body=json.dumps(body).encode("utf-8"),
        url="/api/delete/delete_input_items",
    )

    cosmosdb_container_mock.return_value.query_items.return_value = [
        {"id": "123", "userId": "123"}
    ]
    cosmosdb_container_mock.return_value.delete_item.return_value = None
    get_user_mock.return_value = mock_get_user_data

    response = main(req)
    assert response.status_code == 200
    assert response.get_body() == b'{"Status": "Success"}'
    cosmosdb_container_mock.assert_called_once_with("input_invested")
    cosmosdb_container_mock.return_value.query_items.assert_called_once_with(
        query="SELECT * FROM c WHERE c.id = @id and c.userid = @userid",
        parameters=[
            {"name": "@id", "value": "123"},
            {"name": "@userid", "value": "123"},
        ],
        enable_cross_partition_query=True,
    )
    cosmosdb_container_mock.return_value.delete_item.assert_called_once_with(
        item={"id": "123", "userId": "123"}, partition_key="123"
    )


@patch("shared_code.utils.get_user")
@patch("shared_code.cosmosdb_module.cosmosdb_container")
def test_cosmos_resource_not_found_error(cosmosdb_container_mock, get_user_mock):
    """Test CosmosResourceNotFoundError"""
    req = func.HttpRequest(
        method="POST",
        body=json.dumps(body).encode("utf-8"),
        url="/api/delete/delete_input_items",
    )

    cosmosdb_container_mock.return_value.query_items.return_value = [
        {"id": "123", "userId": "123"}
    ]
    cosmosdb_container_mock.return_value.delete_item.side_effect = (
        exceptions.CosmosResourceNotFoundError(404)
    )
    get_user_mock.return_value = mock_get_user_data

    response = main(req)
    assert response.status_code == 400
    assert (
        response.get_body()
        == b'{"status": "Failed", "errors": [{"id": "123", "error": "Item not found", "http_code": 404}]}'
    )


@patch("shared_code.utils.get_user")
@patch("shared_code.cosmosdb_module.cosmosdb_container")
def test_cosmos_http_response_error(cosmosdb_container_mock, get_user_mock):
    """Test CosmosHttpResponseError"""
    req = func.HttpRequest(
        method="POST",
        body=json.dumps(body).encode("utf-8"),
        url="/api/delete/delete_input_items",
    )

    cosmosdb_container_mock.return_value.query_items.return_value = [
        {"id": "123", "userId": "123"}
    ]
    cosmosdb_container_mock.return_value.delete_item.side_effect = (
        exceptions.CosmosHttpResponseError(500)
    )
    get_user_mock.return_value = mock_get_user_data

    response = main(req)
    assert response.status_code == 400
    assert (
        response.get_body()
        == b'{"status": "Failed", "errors": [{"id": "123", "error": "Status code: 500\\nNone", "http_code": 500}]}'
    )


@patch("shared_code.utils.get_user")
@patch("shared_code.cosmosdb_module.cosmosdb_container")
def test_no_cosmosdb_date(cosmosdb_container_mock, get_user_mock):
    """Test no cosmosdb date"""
    req = func.HttpRequest(
        method="POST",
        body=json.dumps(body).encode("utf-8"),
        url="/api/delete/delete_input_items",
    )

    cosmosdb_container_mock.return_value.query_items.return_value = []
    get_user_mock.return_value = mock_get_user_data

    response = main(req)
    assert response.status_code == 400
    assert (
        response.get_body()
        == b'{"status": "Failed", "errors": [{"id": "123", "error": "Item not found", "http_code": 404}]}'
    )


@patch("shared_code.utils.get_user")
@patch("shared_code.cosmosdb_module.cosmosdb_container")
def test_partial_error(cosmosdb_container_mock, get_user_mock):
    """Test partial error"""

    body.update({"itemIds": ["123", "456"]})

    req = func.HttpRequest(
        method="POST",
        body=json.dumps(body).encode("utf-8"),
        url="/api/delete/delete_input_items",
    )

    cosmosdb_container_mock.return_value.query_items.side_effect = [
        [{"id": "123", "userId": "123"}],
        [],
    ]
    get_user_mock.return_value = mock_get_user_data

    response = main(req)
    assert response.status_code == 400
    assert (
        response.get_body()
        == b'{"status": "Partial success", "errors": [{"id": "456", "error": "Item not found", "http_code": 404}]}'
    )
