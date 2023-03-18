"""Test delete cosmos db and container"""

from unittest.mock import MagicMock, patch

import azure.functions as func
from azure.cosmos import exceptions
from urllib3 import encode_multipart_formdata

from delete_cosmosdb_container import main

containers = {
    "containers": [
        {
            "container_name": "test_container",
            "partition_key": "/test_partition_key",
            "candelete": True,
            "input_container": False,
            "output_container": True,
        },
        {
            "container_name": "test_container_2",
            "partition_key": "/test_partition_key",
            "candelete": False,
            "input_container": False,
            "output_container": True,
        },
    ]
}


def test_no_containers_to_delete():
    """Test no containers to delete"""
    body, header = encode_multipart_formdata({})
    header = {"Content-Type": header}

    req = func.HttpRequest(
        method="POST",
        url="http://localhost:7071/api/priveleged/delete_cosmosdb_container",
        headers=header,
        body=body,
    )

    response = main(req)
    assert (
        response.get_body()
        == b'{"result": "Please pass a name on the query string or in the request body"}'
    )
    assert response.status_code == 400


@patch("shared_code.cosmosdb_module.cosmosdb_database")
def test_invalid_containers_to_delete(mock_cosmosdb_database: MagicMock):
    """Test invalid containers to delete"""
    body, header = encode_multipart_formdata({"containersToDelete": "invalid"})
    header = {"Content-Type": header}

    req = func.HttpRequest(
        method="POST",
        url="http://localhost:7071/api/priveleged/delete_cosmosdb_container",
        headers=header,
        body=body,
    )

    response = main(req)
    assert (
        response.get_body()
        == b'{"result": "Please pass a valid name on the query string or in the request body"}'
    )
    assert response.status_code == 400
    mock_cosmosdb_database.assert_called_once()


@patch("shared_code.cosmosdb_module.cosmosdb_database")
@patch("shared_code.get_config.get_containers")
def test_all_containers_to_delete(
    mock_get_containers: MagicMock, mock_cosmosdb_database: MagicMock
):
    """Test all containers to delete"""
    body, header = encode_multipart_formdata({"containersToDelete": "all"})
    header = {"Content-Type": header}

    req = func.HttpRequest(
        method="POST",
        url="http://localhost:7071/api/priveleged/delete_cosmosdb_container",
        headers=header,
        body=body,
    )

    delete_container = MagicMock()
    delete_container.delete_container = MagicMock()
    mock_cosmosdb_database.return_value = delete_container
    mock_get_containers.return_value = containers

    response = main(req)
    assert response.get_body() == b'{"result": "done"}'
    assert response.status_code == 200
    mock_cosmosdb_database.assert_called_once()
    assert delete_container.delete_container.call_count == 2


@patch("shared_code.cosmosdb_module.cosmosdb_database")
@patch("shared_code.get_config.get_containers")
def test_output_only_containers_to_delete(
    mock_get_containers: MagicMock, mock_cosmosdb_database: MagicMock
):
    """Test output_only containers to delete"""
    body, header = encode_multipart_formdata({"containersToDelete": "output_only"})
    header = {"Content-Type": header}

    req = func.HttpRequest(
        method="POST",
        url="http://localhost:7071/api/priveleged/delete_cosmosdb_container",
        headers=header,
        body=body,
    )

    delete_container = MagicMock()
    delete_container.delete_container = MagicMock()
    mock_cosmosdb_database.return_value = delete_container
    mock_get_containers.return_value = containers

    response = main(req)
    assert response.get_body() == b'{"result": "done"}'
    assert response.status_code == 200
    mock_cosmosdb_database.assert_called_once()
    assert delete_container.delete_container.call_count == 1


@patch("shared_code.cosmosdb_module.cosmosdb_database")
@patch("shared_code.get_config.get_containers")
def test_all_containers_to_delete_with_exception(
    mock_get_containers: MagicMock, mock_cosmosdb_database: MagicMock
):
    """Test all containers to delete invalid"""
    body, header = encode_multipart_formdata({"containersToDelete": "all"})
    header = {"Content-Type": header}

    req = func.HttpRequest(
        method="POST",
        url="http://localhost:7071/api/priveleged/delete_cosmosdb_container",
        headers=header,
        body=body,
    )

    delete_container = MagicMock()
    delete_container.delete_container = MagicMock(
        side_effect=exceptions.CosmosResourceNotFoundError()
    )
    mock_cosmosdb_database.return_value = delete_container
    mock_get_containers.return_value = containers

    response = main(req)
    assert response.get_body() == b'{"result": "deleted 0 out of 2 containers"}'
    assert response.status_code == 500
    mock_cosmosdb_database.assert_called_once()
    assert delete_container.delete_container.call_count == 2


@patch("shared_code.cosmosdb_module.cosmosdb_database")
@patch("shared_code.get_config.get_containers")
def test_output_only_containers_to_delete_with_exception(
    mock_get_containers: MagicMock, mock_cosmosdb_database: MagicMock
):
    """Test output_only containers to delete invalid"""
    body, header = encode_multipart_formdata({"containersToDelete": "output_only"})
    header = {"Content-Type": header}

    req = func.HttpRequest(
        method="POST",
        url="http://localhost:7071/api/priveleged/delete_cosmosdb_container",
        headers=header,
        body=body,
    )

    delete_container = MagicMock()
    delete_container.delete_container = MagicMock(
        side_effect=exceptions.CosmosResourceNotFoundError()
    )
    mock_cosmosdb_database.return_value = delete_container
    mock_get_containers.return_value = containers

    response = main(req)
    assert response.get_body() == b'{"result": "deleted 0 out of 1 containers"}'
    assert response.status_code == 500
    mock_cosmosdb_database.assert_called_once()
    assert delete_container.delete_container.call_count == 1
