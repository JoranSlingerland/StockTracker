"""Test get_table_data_performance.py"""

import json
from unittest.mock import patch

from freezegun import freeze_time

from get_table_data_performance import main
from shared_code.utils import create_form_func_request


def add_meta_data(result, container):
    """ "Add meta data to result"""
    for item in result:
        item["meta"] = {
            "test": "test",
            "logo": "https://example.com/logo.png",
        }
    return result


mock_data = [
    {
        "id": "123",
        "date": "2023-01-01",
    },
    {
        "id": "456",
        "date": "2023-01-06",
    },
    {
        "id": "789",
        "date": "2023-01-03",
    },
]

# start date 7 days before end date
mock_data_start = [
    {
        "id": "123",
        "date": "2023-01-01",
        "symbol": "AAPL",
        "realized": {
            "transaction_cost": 80,
            "total_dividends": 80,
        },
        "unrealized": {
            "total_pl": 80,
            "total_value": 80,
        },
    },
    {
        "id": "456",
        "date": "2023-01-06",
        "symbol": "AMD",
        "realized": {
            "transaction_cost": 80,
            "total_dividends": 80,
        },
        "unrealized": {
            "total_pl": 80,
            "total_value": 80,
        },
    },
]

mock_data_end = [
    {
        "id": "123",
        "date": "2023-01-01",
        "symbol": "AAPL",
        "realized": {
            "transaction_cost": 100,
            "total_dividends": 100,
        },
        "unrealized": {
            "total_pl": 100,
            "total_value": 100,
        },
    },
    {
        "id": "456",
        "date": "2023-01-06",
        "symbol": "AMD",
        "realized": {
            "transaction_cost": 100,
            "total_dividends": 100,
        },
        "unrealized": {
            "total_pl": 100,
            "total_value": 100,
        },
    },
    {
        "id": "789",
        "date": "2023-01-03",
        "symbol": "MSFT",
        "realized": {
            "transaction_cost": 80,
            "total_dividends": 80,
        },
        "unrealized": {
            "total_pl": 80,
            "total_value": 80,
            "total_pl_percentage": 0.5,
        },
    },
]


def test_empty_request():
    """Test empty request"""

    req = create_form_func_request(
        {},
        "https://localhost:7071/api/data/get_table_data_performance",
    )

    result = main(req)
    assert result.status_code == 400
    assert (
        result.get_body()
        == b'{"status": "Please pass a name on the query string or in the request body"}'
    )


def test_invalid_request():
    """Test invalid request"""

    req = create_form_func_request(
        {"userId": "123", "dataToGet": "invalid"},
        "https://localhost:7071/api/data/get_table_data_performance",
    )

    result = main(req)
    assert result.status_code == 400
    assert (
        result.get_body()
        == b'{"status": "Please pass a valid name on the query string or in the request body"}'
    )


@freeze_time("2023-04-02")
@patch("shared_code.cosmosdb_module.cosmosdb_container")
@patch("shared_code.utils.add_meta_data_to_stock_data")
def test_max(mock_add_meta_data_to_stock_data, mock_cosmosdb_container):
    """Test max"""

    mock_add_meta_data_to_stock_data.side_effect = add_meta_data

    mock_cosmosdb_container.return_value.query_items.return_value = mock_data

    req = create_form_func_request(
        {"userId": "123", "dataToGet": "max"},
        "https://localhost:7071/api/data/get_table_data_performance",
    )

    expected_body = [
        {
            "id": "456",
            "date": "2023-01-06",
            "meta": {"test": "test", "logo": "https://example.com/logo.png"},
        },
    ]

    result = main(req)
    assert result.status_code == 200
    assert result.get_body() == json.dumps(expected_body).encode("utf-8")


@patch("shared_code.cosmosdb_module.cosmosdb_container")
@patch("shared_code.utils.add_meta_data_to_stock_data")
def test_no_end_data(mock_add_meta_data_to_stock_data, mock_cosmosdb_container):
    """Test no end data"""

    mock_add_meta_data_to_stock_data.side_effect = add_meta_data

    mock_cosmosdb_container.return_value.query_items.return_value = []

    req = create_form_func_request(
        {"userId": "123", "dataToGet": "week"},
        "https://localhost:7071/api/data/get_table_data_performance",
    )

    result = main(req)
    assert result.status_code == 400
    assert result.get_body() == b'{"status": "No data found for this date range"}'


@patch("shared_code.cosmosdb_module.cosmosdb_container")
@patch("shared_code.utils.add_meta_data_to_stock_data")
def test_week_request(mock_add_meta_data_to_stock_data, mock_cosmosdb_container):
    """Test week request"""

    req = create_form_func_request(
        {"userId": "123", "dataToGet": "week"},
        "https://localhost:7071/api/data/get_table_data_performance",
    )

    mock_add_meta_data_to_stock_data.side_effect = add_meta_data
    mock_cosmosdb_container.return_value.query_items.side_effect = [
        mock_data_start,
        mock_data_end,
    ]

    expected_body = [
        {
            "symbol": "AAPL",
            "realized": {"transaction_cost": 20, "total_dividends": 20},
            "unrealized": {"total_pl": 20, "total_pl_percentage": 0.25},
            "meta": {"logo": "https://example.com/logo.png"},
        },
        {
            "symbol": "AMD",
            "realized": {"transaction_cost": 20, "total_dividends": 20},
            "unrealized": {"total_pl": 20, "total_pl_percentage": 0.25},
            "meta": {"logo": "https://example.com/logo.png"},
        },
        {
            "symbol": "MSFT",
            "realized": {"transaction_cost": 80, "total_dividends": 80},
            "unrealized": {"total_pl": 80, "total_pl_percentage": 0.5},
            "meta": {"logo": "https://example.com/logo.png"},
        },
    ]

    result = main(req)
    assert result.status_code == 200
    assert (
        sorted(json.loads(result.get_body()), key=lambda k: k["symbol"])
        == expected_body
    )
