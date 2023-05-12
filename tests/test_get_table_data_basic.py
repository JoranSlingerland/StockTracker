"""Test get_table_data_basic"""

import json
from copy import deepcopy
from pathlib import Path
from unittest.mock import patch

import time_machine

from get_table_data_basic import main
from shared_code.utils import create_form_func_request

with open(Path(__file__).parent / "data" / "get_user_data.json", "r") as f:
    mock_get_user_data = json.load(f)


def add_meta_data(result, container_name, userid):
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

mock_result = [
    {
        "id": "456",
        "date": "2023-01-06",
    }
]


class TestValidRequest:
    """Valid request class"""

    @patch("shared_code.utils.get_user")
    @patch("shared_code.cosmosdb_module.cosmosdb_container")
    @patch("shared_code.utils.add_meta_data_to_stock_data")
    def test_valid_input_transactions(
        self, add_meta_data_to_stock_data, cosmosdb_container, get_user
    ):
        """Test valid input transactions"""
        mock_data_copy = deepcopy(mock_data)

        for item in mock_data_copy:
            item["cost_per_share"] = 10
            item["quantity"] = 10

        cosmosdb_container.return_value.query_items.return_value = []
        cosmosdb_container.return_value.read_all_items.return_value = mock_data_copy
        add_meta_data_to_stock_data.side_effect = add_meta_data
        get_user.return_value = mock_get_user_data
        expected_result = add_meta_data(mock_data_copy, "", "")
        for item in expected_result:
            item["total_cost"] = 100

        expected_result = sorted(expected_result, key=lambda x: x["date"], reverse=True)

        req = create_form_func_request(
            {"containerName": "input_transactions"},
            "http://localhost:7071/api/data/get_table_data_basic",
        )

        result = main(req)
        assert result.status_code == 200
        assert result.get_body() == json.dumps(expected_result).encode()
        cosmosdb_container.return_value.query_items.assert_not_called()
        cosmosdb_container.return_value.read_all_items.assert_called_once()

    @time_machine.travel("2023-04-02")
    @patch("shared_code.utils.get_user")
    @patch("shared_code.cosmosdb_module.cosmosdb_container")
    @patch("shared_code.utils.add_meta_data_to_stock_data")
    def test_valid_input_stocks_held(
        self, add_meta_data_to_stock_data, cosmosdb_container, get_user
    ):
        """Test valid input single day"""

        cosmosdb_container.return_value.query_items.return_value = mock_data
        cosmosdb_container.return_value.read_all_items.return_value = []
        add_meta_data_to_stock_data.side_effect = add_meta_data
        get_user.return_value = mock_get_user_data

        excepted_result = add_meta_data(
            mock_result,
            "",
            "",
        )

        req = create_form_func_request(
            {"containerName": "stocks_held"},
            "http://localhost:7071/api/data/get_table_data_basic",
        )

        result = main(req)
        assert result.status_code == 200
        assert result.get_body() == json.dumps(excepted_result).encode()
        cosmosdb_container.return_value.query_items.assert_called_once()
        cosmosdb_container.return_value.read_all_items.assert_not_called()
        cosmosdb_container.return_value.query_items.assert_called_once_with(
            query="select * from c where c.userid = @userid and c.date > @start_date and c.date < @end_date",
            parameters=[
                {"name": "@userid", "value": "123"},
                {"name": "@fully_realized", "value": None},
                {"name": "@partial_realized", "value": None},
                {"name": "@start_date", "value": "2023-03-03"},
                {"name": "@end_date", "value": "2023-04-02"},
            ],
            enable_cross_partition_query=True,
        )

    @time_machine.travel("2023-04-02")
    @patch("shared_code.utils.get_user")
    @patch("shared_code.cosmosdb_module.cosmosdb_container")
    @patch("shared_code.utils.add_meta_data_to_stock_data")
    def test_valid_input_stocks_held_fully_realized(
        self, add_meta_data_to_stock_data, cosmosdb_container, get_user
    ):
        """Test valid input single day"""

        cosmosdb_container.return_value.query_items.return_value = mock_data
        cosmosdb_container.return_value.read_all_items.return_value = []
        add_meta_data_to_stock_data.side_effect = add_meta_data
        get_user.return_value = mock_get_user_data

        excepted_result = add_meta_data(mock_result, "", "")
        req = create_form_func_request(
            {"containerName": "stocks_held", "fullyRealized": "true"},
            "http://localhost:7071/api/data/get_table_data_basic",
        )

        result = main(req)
        assert result.status_code == 200
        assert result.get_body() == json.dumps(excepted_result).encode()
        cosmosdb_container.return_value.query_items.assert_called_once()
        cosmosdb_container.return_value.read_all_items.assert_not_called()
        cosmosdb_container.return_value.query_items.assert_called_once_with(
            query="select * from c where c.fully_realized = @fully_realized and c.userid = @userid and c.date > @start_date and c.date < @end_date",
            parameters=[
                {"name": "@userid", "value": "123"},
                {"name": "@fully_realized", "value": True},
                {"name": "@partial_realized", "value": None},
                {"name": "@start_date", "value": "2023-03-03"},
                {"name": "@end_date", "value": "2023-04-02"},
            ],
            enable_cross_partition_query=True,
        )

    @time_machine.travel("2023-04-02")
    @patch("shared_code.utils.get_user")
    @patch("shared_code.cosmosdb_module.cosmosdb_container")
    @patch("shared_code.utils.add_meta_data_to_stock_data")
    def test_valid_input_stocks_held_partial_realized(
        self, add_meta_data_to_stock_data, cosmosdb_container, get_user
    ):
        """Test valid input single day"""

        cosmosdb_container.return_value.query_items.return_value = mock_data
        cosmosdb_container.return_value.read_all_items.return_value = []
        add_meta_data_to_stock_data.side_effect = add_meta_data
        get_user.return_value = mock_get_user_data

        excepted_result = add_meta_data(mock_result, "", "")

        req = create_form_func_request(
            {
                "containerName": "stocks_held",
                "partialRealized": "true",
            },
            "http://localhost:7071/api/data/get_table_data_basic",
        )

        result = main(req)
        assert result.status_code == 200
        assert result.get_body() == json.dumps(excepted_result).encode()
        cosmosdb_container.return_value.query_items.assert_called_once()
        cosmosdb_container.return_value.read_all_items.assert_not_called()
        cosmosdb_container.return_value.query_items.assert_called_once_with(
            query="select * from c where c.partial_realized = @partial_realized and c.userid = @userid and c.date > @start_date and c.date < @end_date",
            parameters=[
                {"name": "@userid", "value": "123"},
                {"name": "@fully_realized", "value": None},
                {"name": "@partial_realized", "value": True},
                {"name": "@start_date", "value": "2023-03-03"},
                {"name": "@end_date", "value": "2023-04-02"},
            ],
            enable_cross_partition_query=True,
        )

    @time_machine.travel("2023-04-02")
    @patch("shared_code.utils.get_user")
    @patch("shared_code.cosmosdb_module.cosmosdb_container")
    @patch("shared_code.utils.add_meta_data_to_stock_data")
    def test_valid_input_stocks_held_or(
        self, add_meta_data_to_stock_data, cosmosdb_container, get_user
    ):
        """Test valid input single day"""

        cosmosdb_container.return_value.query_items.return_value = mock_data
        cosmosdb_container.return_value.read_all_items.return_value = []
        add_meta_data_to_stock_data.side_effect = add_meta_data
        get_user.return_value = mock_get_user_data

        excepted_result = add_meta_data(
            mock_result,
            "",
            "",
        )

        req = create_form_func_request(
            {
                "containerName": "stocks_held",
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
            query="select * from c where (c.partial_realized = @partial_realized or c.fully_realized = @fully_realized) and c.userid = @userid and c.date > @start_date and c.date < @end_date",
            parameters=[
                {"name": "@userid", "value": "123"},
                {"name": "@fully_realized", "value": True},
                {"name": "@partial_realized", "value": True},
                {"name": "@start_date", "value": "2023-03-03"},
                {"name": "@end_date", "value": "2023-04-02"},
            ],
            enable_cross_partition_query=True,
        )

    @time_machine.travel("2023-04-02")
    @patch("shared_code.utils.get_user")
    @patch("shared_code.cosmosdb_module.cosmosdb_container")
    @patch("shared_code.utils.add_meta_data_to_stock_data")
    def test_valid_input_stocks_held_and(
        self, add_meta_data_to_stock_data, cosmosdb_container, get_user
    ):
        """Test valid input single day"""

        cosmosdb_container.return_value.query_items.return_value = mock_data
        cosmosdb_container.return_value.read_all_items.return_value = []
        add_meta_data_to_stock_data.side_effect = add_meta_data
        get_user.return_value = mock_get_user_data

        excepted_result = add_meta_data(
            mock_result,
            "",
            "",
        )

        req = create_form_func_request(
            {
                "containerName": "stocks_held",
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
            query="select * from c where c.partial_realized = @partial_realized and c.fully_realized = @fully_realized and c.userid = @userid and c.date > @start_date and c.date < @end_date",
            parameters=[
                {"name": "@userid", "value": "123"},
                {"name": "@fully_realized", "value": True},
                {"name": "@partial_realized", "value": True},
                {"name": "@start_date", "value": "2023-03-03"},
                {"name": "@end_date", "value": "2023-04-02"},
            ],
            enable_cross_partition_query=True,
        )


class TestInvalidRequest:
    """Invalid request class"""

    def test_missing_parameters(self):
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

    @patch("shared_code.utils.get_user")
    def test_invalid_parameters(self, get_user):
        """Test invalid parameters"""

        get_user.return_value = mock_get_user_data

        req = create_form_func_request(
            {"containerName": "invalid"},
            "http://localhost:7071/api/data/get_table_data_basic",
        )

        result = main(req)
        assert result.status_code == 400
        assert (
            result.get_body()
            == b'{"status": "Please pass a valid name on the query string or in the request body"}'
        )


class TestEdgeCases:
    """Edge cases class"""

    @patch("shared_code.utils.get_user")
    @patch("shared_code.cosmosdb_module.cosmosdb_container")
    @patch("shared_code.utils.add_meta_data_to_stock_data")
    def test_empty_cosmosdb(
        self, add_meta_data_to_stock_data, cosmosdb_container, get_user
    ):
        """Test empty cosmosdb"""

        cosmosdb_container.return_value.query_items.return_value = []
        cosmosdb_container.return_value.read_all_items.return_value = []
        add_meta_data_to_stock_data.return_value = []
        get_user.return_value = mock_get_user_data

        req = create_form_func_request(
            {"containerName": "input_invested", "userId": "123"},
            "http://localhost:7071/api/data/get_table_data_basic",
        )

        result = main(req)
        assert result.status_code == 200
        assert result.get_body() == b"{[]}"
        cosmosdb_container.return_value.read_all_items.assert_called_once()
        cosmosdb_container.return_value.query_items.assert_not_called()
