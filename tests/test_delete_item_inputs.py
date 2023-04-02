"""Test delete_item_inputs"""

from unittest.mock import patch

from azure.cosmos import exceptions

from delete_input_items import main
from shared_code.utils import create_form_func_request


def test_empty_request():
    """Test empty request"""
    req = create_form_func_request(
        {}, "http://localhost:7071/api/delete/delete/delete_input_items"
    )
    response = main(req)
    assert response.status_code == 400
    assert (
        response.get_body()
        == b'{"status": "Please pass a valid name on the query string or in the request body"}'
    )


@patch("shared_code.cosmosdb_module.cosmosdb_container")
def test_valid_request(cosmosdb_container_mock):
    """Test valid request"""
    req = create_form_func_request(
        {
            "itemIds": '["123"]',
            "container": "input_invested",
            "userId": "123",
        },
        "http://localhost:7071/api/delete/delete_input_items",
    )

    cosmosdb_container_mock.return_value.query_items.return_value = [
        {"id": "123", "userId": "123"}
    ]
    cosmosdb_container_mock.return_value.delete_item.return_value = None

    response = main(req)
    assert response.status_code == 200
    assert response.get_body() == b'{"Status": "Success"}'
    cosmosdb_container_mock.assert_called_once_with("input_invested")
    cosmosdb_container_mock.return_value.query_items.assert_called_once_with(
        query="SELECT * FROM c WHERE c.id = @id and c.userId = @userid",
        parameters=[
            {"name": "@id", "value": "123"},
            {"name": "@userid", "value": "123"},
        ],
        enable_cross_partition_query=True,
    )
    cosmosdb_container_mock.return_value.delete_item.assert_called_once_with(
        item=[{"id": "123", "userId": "123"}]
    )


@patch("shared_code.cosmosdb_module.cosmosdb_container")
def test_cosmos_resource_not_found_error(cosmosdb_container_mock):
    """Test CosmosResourceNotFoundError"""

    req = create_form_func_request(
        {
            "itemIds": '["123"]',
            "container": "input_invested",
            "userId": "123",
        },
        "http://localhost:7071/api/delete/delete_input_items",
    )

    cosmosdb_container_mock.return_value.query_items.return_value = [
        {"id": "123", "userId": "123"}
    ]
    cosmosdb_container_mock.return_value.delete_item.side_effect = (
        exceptions.CosmosResourceNotFoundError(404)
    )

    response = main(req)
    assert response.status_code == 400
    assert (
        response.get_body()
        == b'{"status": "Failed", "errors": [{"id": "123", "error": "Item not found", "http_code": 404}]}'
    )


@patch("shared_code.cosmosdb_module.cosmosdb_container")
def test_cosmos_http_response_error(cosmosdb_container_mock):
    """Test CosmosHttpResponseError"""

    req = create_form_func_request(
        {
            "itemIds": '["123"]',
            "container": "input_invested",
            "userId": "123",
        },
        "http://localhost:7071/api/delete/delete_input_items",
    )

    cosmosdb_container_mock.return_value.query_items.return_value = [
        {"id": "123", "userId": "123"}
    ]
    cosmosdb_container_mock.return_value.delete_item.side_effect = (
        exceptions.CosmosHttpResponseError(500)
    )

    response = main(req)
    assert response.status_code == 400
    assert (
        response.get_body()
        == b'{"status": "Failed", "errors": [{"id": "123", "error": "Status code: 500\\nNone", "http_code": 500}]}'
    )


@patch("shared_code.cosmosdb_module.cosmosdb_container")
def test_no_cosmosdb_date(cosmosdb_container_mock):
    """Test no cosmosdb date"""

    req = create_form_func_request(
        {
            "itemIds": '["123"]',
            "container": "input_invested",
            "userId": "123",
        },
        "http://localhost:7071/api/delete/delete_input_items",
    )

    cosmosdb_container_mock.return_value.query_items.return_value = []

    response = main(req)
    assert response.status_code == 400
    assert (
        response.get_body()
        == b'{"status": "Failed", "errors": [{"id": "123", "error": "Item not found", "http_code": 404}]}'
    )


@patch("shared_code.cosmosdb_module.cosmosdb_container")
def test_partial_error(cosmosdb_container_mock):
    """Test partial error"""

    req = create_form_func_request(
        {
            "itemIds": '["123", "456"]',
            "container": "input_invested",
            "userId": "123",
        },
        "http://localhost:7071/api/delete/delete_input_items",
    )

    cosmosdb_container_mock.return_value.query_items.side_effect = [
        [{"id": "123", "userId": "123"}],
        [],
    ]

    response = main(req)
    assert response.status_code == 400
    assert (
        response.get_body()
        == b'{"status": "Partial success", "errors": [{"id": "456", "error": "Item not found", "http_code": 404}]}'
    )
