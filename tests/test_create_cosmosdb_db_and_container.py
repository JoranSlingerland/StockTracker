"""Test create_cosmosdb_db_and_container.py"""

from unittest.mock import MagicMock, patch

import azure.functions as func
from azure.cosmos.partition_key import PartitionKey

from create_cosmosdb_db_and_container import main


@patch("azure.cosmos.cosmos_client.CosmosClient")
@patch("shared_code.get_config.get_containers")
@patch("shared_code.get_config.get_cosmosdb")
def test_create_db_and_table(
    mock_get_cosmosdb, mock_get_containers, mock_cosmos_client
):
    """Test create_db_and_table"""
    mock_get_cosmosdb.return_value = {
        "endpoint": "test_endpoint",
        "key": "test_key",
        "database": "test_database",
        "offer_throughput": "test_offer_throughput",
    }
    mock_get_containers.return_value = {
        "containers": [
            {
                "container_name": "test_container",
                "partition_key": "/test_partition_key",
                "candelete": True,
                "cantruncate": True,
                "input_container": False,
                "output_container": True,
            }
        ]
    }
    mock_cosmos_client.return_value = MagicMock()
    mock_database = MagicMock()
    mock_cosmos_client.return_value.create_database_if_not_exists.return_value = (
        mock_database
    )
    mock_database.create_container_if_not_exists.return_value = None

    request = func.HttpRequest(method="GET", url="http://localhost", body=b"")
    response = main(request)

    assert response.status_code == 200
    assert response.mimetype == "application/json"
    assert response.get_body() == b'{"result": "done"}'
    mock_get_cosmosdb.assert_called_once()
    mock_get_containers.assert_called_once()
    mock_cosmos_client.assert_called_once_with("test_endpoint", "test_key")
    mock_cosmos_client.return_value.create_database_if_not_exists.assert_called_once_with(
        id="test_database", offer_throughput="test_offer_throughput"
    )
    mock_database.create_container_if_not_exists.assert_called_once_with(
        id="test_container", partition_key=PartitionKey(path="/test_partition_key")
    )
