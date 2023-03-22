"""Test get_table_data_basic"""

import json
from unittest.mock import patch

from get_table_data_basic import main
from shared_code.utils import create_form_func_request


def add_meta_data(result, container):
    """ "Add meta data to result"""
    for item in result:
        item["meta"] = {
            "test": "test",
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


def test_missing_parameters():
    """Test missing parameters"""

    req = create_form_func_request(
        {},
        "http://localhost:7071/api/data/get_table_data_basic",
    )

    result = main(req)
    assert result.status_code == 400
    assert (
        result.get_body()
        == b'{"status": "Please pass a name on the query string or in the request body"}'
    )


def test_invalid_parameters():
    """Test invalid parameters"""

    req = create_form_func_request(
        {"containerName": "invalid", "userId": "123"},
        "http://localhost:7071/api/data/get_table_data_basic",
    )

    result = main(req)
    assert result.status_code == 400
    assert (
        result.get_body()
        == b'{"status": "Please pass a valid name on the query string or in the request body"}'
    )


@patch("shared_code.cosmosdb_module.cosmosdb_container")
@patch("shared_code.utils.add_meta_data_to_stock_data")
def test_empty_cosmosdb(add_meta_data_to_stock_data, cosmosdb_container):
    """Test empty cosmosdb"""

    cosmosdb_container.return_value.query_items.return_value = []
    cosmosdb_container.return_value.read_all_items.return_value = []
    add_meta_data_to_stock_data.return_value = []

    req = create_form_func_request(
        {"containerName": "input_invested", "userId": "123"},
        "http://localhost:7071/api/data/get_table_data_basic",
    )

    result = main(req)
    assert result.status_code == 200
    assert result.get_body() == b"{[]}"
    cosmosdb_container.return_value.read_all_items.assert_called_once()
    cosmosdb_container.return_value.query_items.assert_not_called()


@patch("shared_code.cosmosdb_module.cosmosdb_container")
@patch("shared_code.utils.add_meta_data_to_stock_data")
def test_valid_input_transactions(add_meta_data_to_stock_data, cosmosdb_container):
    """Test valid input transactions"""

    cosmosdb_container.return_value.query_items.return_value = []
    cosmosdb_container.return_value.read_all_items.return_value = mock_data
    add_meta_data_to_stock_data.side_effect = add_meta_data
    expected_result = add_meta_data(mock_data, "")
    expected_result = sorted(expected_result, key=lambda x: x["date"], reverse=True)

    req = create_form_func_request(
        {"containerName": "input_transactions", "userId": "123"},
        "http://localhost:7071/api/data/get_table_data_basic",
    )

    result = main(req)
    assert result.status_code == 200
    assert result.get_body() == json.dumps(expected_result).encode()
    cosmosdb_container.return_value.query_items.assert_not_called()
    cosmosdb_container.return_value.read_all_items.assert_called_once()


@patch("shared_code.cosmosdb_module.cosmosdb_container")
@patch("shared_code.utils.add_meta_data_to_stock_data")
def test_valid_input_single_day(add_meta_data_to_stock_data, cosmosdb_container):
    """Test valid input single day"""

    cosmosdb_container.return_value.query_items.return_value = mock_data
    cosmosdb_container.return_value.read_all_items.return_value = []
    add_meta_data_to_stock_data.side_effect = add_meta_data

    excepted_result = add_meta_data(mock_data, "")

    req = create_form_func_request(
        {"containerName": "single_day", "userId": "123"},
        "http://localhost:7071/api/data/get_table_data_basic",
    )

    result = main(req)
    assert result.status_code == 200
    assert result.get_body() == json.dumps(excepted_result).encode()
    cosmosdb_container.return_value.query_items.assert_called_once()
    cosmosdb_container.return_value.read_all_items.assert_not_called()
    cosmosdb_container.return_value.query_items.assert_called_once_with(
        query="select * from c where c.userid = @userid",
        parameters=[
            {"name": "@userid", "value": "123"},
            {"name": "@fully_realized", "value": None},
            {"name": "@partial_realized", "value": None},
        ],
        enable_cross_partition_query=True,
    )


@patch("shared_code.cosmosdb_module.cosmosdb_container")
@patch("shared_code.utils.add_meta_data_to_stock_data")
def test_valid_input_single_day_fully_realized(
    add_meta_data_to_stock_data, cosmosdb_container
):
    """Test valid input single day"""

    cosmosdb_container.return_value.query_items.return_value = mock_data
    cosmosdb_container.return_value.read_all_items.return_value = []
    add_meta_data_to_stock_data.side_effect = add_meta_data

    excepted_result = add_meta_data(mock_data, "")

    req = create_form_func_request(
        {"containerName": "single_day", "userId": "123", "fullyRealized": "true"},
        "http://localhost:7071/api/data/get_table_data_basic",
    )

    result = main(req)
    assert result.status_code == 200
    assert result.get_body() == json.dumps(excepted_result).encode()
    cosmosdb_container.return_value.query_items.assert_called_once()
    cosmosdb_container.return_value.read_all_items.assert_not_called()
    cosmosdb_container.return_value.query_items.assert_called_once_with(
        query="select * from c where c.fully_realized = @fully_realized and c.userid = @userid",
        parameters=[
            {"name": "@userid", "value": "123"},
            {"name": "@fully_realized", "value": True},
            {"name": "@partial_realized", "value": None},
        ],
        enable_cross_partition_query=True,
    )


@patch("shared_code.cosmosdb_module.cosmosdb_container")
@patch("shared_code.utils.add_meta_data_to_stock_data")
def test_valid_input_single_day_partial_realized(
    add_meta_data_to_stock_data, cosmosdb_container
):
    """Test valid input single day"""

    cosmosdb_container.return_value.query_items.return_value = mock_data
    cosmosdb_container.return_value.read_all_items.return_value = []
    add_meta_data_to_stock_data.side_effect = add_meta_data

    excepted_result = add_meta_data(mock_data, "")

    req = create_form_func_request(
        {"containerName": "single_day", "userId": "123", "partialRealized": "true"},
        "http://localhost:7071/api/data/get_table_data_basic",
    )

    result = main(req)
    assert result.status_code == 200
    assert result.get_body() == json.dumps(excepted_result).encode()
    cosmosdb_container.return_value.query_items.assert_called_once()
    cosmosdb_container.return_value.read_all_items.assert_not_called()
    cosmosdb_container.return_value.query_items.assert_called_once_with(
        query="select * from c where c.partial_realized = @partial_realized and c.userid = @userid",
        parameters=[
            {"name": "@userid", "value": "123"},
            {"name": "@fully_realized", "value": None},
            {"name": "@partial_realized", "value": "true"},
        ],
        enable_cross_partition_query=True,
    )


@patch("shared_code.cosmosdb_module.cosmosdb_container")
@patch("shared_code.utils.add_meta_data_to_stock_data")
def test_valid_input_single_day_or(add_meta_data_to_stock_data, cosmosdb_container):
    """Test valid input single day"""

    cosmosdb_container.return_value.query_items.return_value = mock_data
    cosmosdb_container.return_value.read_all_items.return_value = []
    add_meta_data_to_stock_data.side_effect = add_meta_data

    excepted_result = add_meta_data(mock_data, "")

    req = create_form_func_request(
        {
            "containerName": "single_day",
            "userId": "123",
            "partialRealized": "true",
            "fullyRealized": "true",
            "andOr": "or",
        },
        "http://localhost:7071/api/data/get_table_data_basic",
    )

    result = main(req)
    assert result.status_code == 200
    assert result.get_body() == json.dumps(excepted_result).encode()
    cosmosdb_container.return_value.query_items.assert_called_once()
    cosmosdb_container.return_value.read_all_items.assert_not_called()
    cosmosdb_container.return_value.query_items.assert_called_once_with(
        query="select * from c where c.partial_realized = @partial_realized or c.fully_realized = @fully_realized and c.userid = @userid",
        parameters=[
            {"name": "@userid", "value": "123"},
            {"name": "@fully_realized", "value": True},
            {"name": "@partial_realized", "value": "true"},
        ],
        enable_cross_partition_query=True,
    )


@patch("shared_code.cosmosdb_module.cosmosdb_container")
@patch("shared_code.utils.add_meta_data_to_stock_data")
def test_valid_input_single_day_and(add_meta_data_to_stock_data, cosmosdb_container):
    """Test valid input single day"""

    cosmosdb_container.return_value.query_items.return_value = mock_data
    cosmosdb_container.return_value.read_all_items.return_value = []
    add_meta_data_to_stock_data.side_effect = add_meta_data

    excepted_result = add_meta_data(mock_data, "")

    req = create_form_func_request(
        {
            "containerName": "single_day",
            "userId": "123",
            "partialRealized": "true",
            "fullyRealized": "true",
            "andOr": "and",
        },
        "http://localhost:7071/api/data/get_table_data_basic",
    )

    result = main(req)
    assert result.status_code == 200
    assert result.get_body() == json.dumps(excepted_result).encode()
    cosmosdb_container.return_value.query_items.assert_called_once()
    cosmosdb_container.return_value.read_all_items.assert_not_called()
    cosmosdb_container.return_value.query_items.assert_called_once_with(
        query="select * from c where c.partial_realized = @partial_realized and c.fully_realized = @fully_realized and c.userid = @userid",
        parameters=[
            {"name": "@userid", "value": "123"},
            {"name": "@fully_realized", "value": True},
            {"name": "@partial_realized", "value": "true"},
        ],
        enable_cross_partition_query=True,
    )
