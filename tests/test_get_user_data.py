"""Test get_user_data.py"""

import json
from unittest.mock import patch

from get_user_data import main
from shared_code.utils import create_form_func_request

mock_container_response = [
    {
        "id": "123",
        "dark_mode": True,
        "clearbit_api_key": "123",
        "alpha_vantage_api_key": "123",
        "_rid": "+qI9AL5k7vYBAAAAAAAAAA==",
        "_self": "dbs/+qI9AA==/colls/+qI9AL5k7vY=/docs/+qI9AL5k7vYBAAAAAAAAAA==/",
        "_etag": '"00000000-0000-0000-794c-37981eb601d9"',
        "_attachments": "attachments/",
        "_ts": 1682629624,
    }
]


def test_invalid_input():
    """Test invalid input"""
    req = create_form_func_request({}, "http://localhost:7071/api/data/get_user_data")

    result = main(req)
    assert result.status_code == 400
    assert (
        result.get_body()
        == b'{"status": "Please pass a name on the query string or in the request body"}'
    )


@patch("shared_code.cosmosdb_module.cosmosdb_container")
def test_valid_request(cosmosdb_container):
    """Test valid request"""
    req = create_form_func_request(
        {
            "userId": "1",
        },
        "http://localhost:7071/api/data/get_user_data",
    )

    cosmosdb_container.return_value.query_items.return_value = mock_container_response

    result = main(req)
    body = json.loads(result.get_body().decode("utf-8"))
    assert result.status_code == 200
    assert body == mock_container_response[0]


@patch("shared_code.cosmosdb_module.cosmosdb_container")
def test_no_data_in_cosmosdb(cosmosdb_container):
    """Test no data in cosmosdb"""
    req = create_form_func_request(
        {
            "userId": "1",
        },
        "http://localhost:7071/api/data/get_user_data",
    )

    cosmosdb_container.return_value.query_items.return_value = []

    result = main(req)
    assert result.status_code == 400
    assert result.get_body() == b'{"status": "No data found"}'
