"""Test the get_topbar_data function."""

import json
from unittest.mock import patch

from get_topbar_data import main
from shared_code.utils import create_form_func_request

mock_end_data = [
    {
        "date": "2023-04-02",
        "id": "123",
        "total_value": 100,
        "total_pl": 100,
        "total_pl_percentage": 100,
        "total_dividends": 100,
        "transaction_cost": 100,
    },
    {
        "date": "2023-04-01",
        "id": "123",
        "total_value": 80,
        "total_pl": 80,
        "total_pl_percentage": 80,
        "total_dividends": 80,
        "transaction_cost": 80,
    },
]


def test_empty_request():
    """Test empty request."""

    req = create_form_func_request(
        {}, "https://localhost:7071/api/data/get_topbar_data"
    )
    result = main(req)
    assert (
        result.get_body()
        == b'{"status": "Please pass a name on the query string or in the request body"}'
    )
    assert result.status_code == 400


@patch("shared_code.cosmosdb_module.cosmosdb_container")
def test_max_request(mock_cosmosdb_container):
    """Test max request."""

    req = create_form_func_request(
        {"userId": "123", "dataToGet": "max"},
        "https://localhost:7071/api/data/get_topbar_data",
    )

    mock_cosmosdb_container.return_value.query_items.return_value = mock_end_data

    expected_body = {
        "total_value_gain": 100,
        "total_value_gain_percentage": 1,
        "total_pl": 100,
        "total_pl_percentage": 100,
        "total_dividends": 100,
        "transaction_cost": 100,
    }

    result = main(req)
    assert result.status_code == 200
    assert json.loads(result.get_body()) == expected_body


@patch("shared_code.cosmosdb_module.cosmosdb_container")
def test_week_request(mock_cosmosdb_container):
    """Test week request."""

    req = create_form_func_request(
        {"userId": "123", "dataToGet": "week"},
        "https://localhost:7071/api/data/get_topbar_data",
    )

    mock_cosmosdb_container.return_value.query_items.return_value = mock_end_data

    expected_body = {
        "total_value_gain": 20,
        "total_value_gain_percentage": 0.25,
        "total_pl": 20,
        "total_pl_percentage": 0.25,
        "total_dividends": 20,
        "transaction_cost": 20,
    }

    result = main(req)
    assert result.status_code == 200
    assert json.loads(result.get_body()) == expected_body
