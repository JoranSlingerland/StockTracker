"""Test add_item_to_input.py"""

import json
from copy import deepcopy
from pathlib import Path
from unittest.mock import patch

import time_machine

from get_barchart_data import main
from shared_code.utils import create_form_func_request

with open(Path(__file__).parent / "data" / "stocks_held_data.json", "r") as f:
    mock_stocks_held_data = json.load(f)

with open(Path(__file__).parent / "data" / "input_transactions_data.json", "r") as f:
    mock_input_transactions_data = json.load(f)

with open(Path(__file__).parent / "data" / "get_user_data.json", "r") as f:
    mock_get_user_data = json.load(f)

dividend_req = create_form_func_request(
    {
        "dataType": "dividend",
        "allData": "true",
    },
    "http://localhost/api/data/get_barchart_data",
)

transaction_cost_req = create_form_func_request(
    {
        "dataType": "transaction_cost",
        "allData": "true",
    },
    "http://localhost/api/data/get_barchart_data",
)


class TestInvalidRequest:
    """Invalid request class"""

    def test_empty_body(self):
        """Test empty body"""
        req = create_form_func_request(
            {}, "http://localhost:7071/api/data/get_linechart_data"
        )

        response = main(req)
        assert (
            response.get_body()
            == b'{"status": "Invalid combination of parameters. Please pass a valid name in the request body"}'
        )
        assert response.status_code == 400

    def test_invalid_start_date(self):
        """Test invalid request."""

        req = create_form_func_request(
            {
                "dataType": "transaction_cost",
                "startDate": "2021-13-02",
                "endDate": "2022-02-02",
            },
            "https://localhost:7071/api/data/get_table_data_performance_v2",
        )

        result = main(req)

        assert result.status_code == 400
        assert (
            result.get_body()
            == b'{"status": "Start date is not in the correct format"}'
        )

    def test_invalid_end_date(self):
        """Test invalid request."""

        req = create_form_func_request(
            {
                "dataType": "transaction_cost",
                "startDate": "2021-12-02",
                "endDate": "2022-13-02",
            },
            "https://localhost:7071/api/data/get_table_data_performance_v2",
        )

        result = main(req)

        assert result.status_code == 400
        assert (
            result.get_body() == b'{"status": "End date is not in the correct format"}'
        )

    def test_end_date_before_start_date(self):
        """Test invalid request."""

        req = create_form_func_request(
            {
                "dataType": "transaction_cost",
                "startDate": "2023-12-02",
                "endDate": "2022-12-02",
            },
            "https://localhost:7071/api/data/get_table_data_performance_v2",
        )

        result = main(req)

        assert result.status_code == 400
        assert result.get_body() == b'{"status": "Start date is after end date"}'

    def test_invalid_combination(self):
        """Test invalid request."""

        req = create_form_func_request(
            {
                "dataType": "transaction_cost",
                "startDate": "2021-12-02",
                "endDate": "2022-12-02",
                "allData": "true",
            },
            "https://localhost:7071/api/data/get_table_data_performance_v2",
        )

        result = main(req)

        assert result.status_code == 400
        assert (
            result.get_body()
            == b'{"status": "Invalid combination of parameters. Please pass a valid name in the request body"}'
        )


class TestEdgeCases:
    """Edge cases class"""

    @patch("shared_code.utils.get_user")
    @patch("shared_code.cosmosdb_module.cosmosdb_container")
    def test_no_data(self, mock_cosmosdb_container, mock_get_user):
        """Test get_barchart_data with no data"""
        req = create_form_func_request(
            {
                "dataType": "transaction_cost",
                "startDate": "2021-12-02",
                "endDate": "2022-02-02",
            },
            "http://localhost/api/data/get_barchart_data",
        )

        mock_get_user.return_value = mock_get_user_data
        mock_cosmosdb_container.return_value.query_items.return_value = []

        response = main(req)
        assert response.status_code == 500
        assert (
            response.get_body()
            == b'{"status": No data found in database for this time frame"}'
        )


class TestValidRequest:
    """Valid request class"""

    @time_machine.travel("2024-04-04")
    @patch("shared_code.utils.get_user")
    @patch("shared_code.cosmosdb_module.cosmosdb_container")
    def test_dividends_quarter_interval(self, mock_cosmosdb_container, mock_get_user):
        """Test get_barchart_data with valid input"""
        temp_copy = deepcopy(mock_stocks_held_data)
        temp_copy[0]["date"] = "2023-04-03"

        mock_cosmosdb_container.return_value.query_items.return_value = temp_copy
        expected_result = [
            {"date": "Q2 2023", "value": 0, "category": "MSFT"},
            {"date": "Q2 2023", "value": 0, "category": "AMD"},
            {"date": "Q3 2023", "value": 0.0, "category": "MSFT"},
            {"date": "Q3 2023", "value": 0.0, "category": "AMD"},
            {"date": "Q4 2023", "value": 0.0, "category": "MSFT"},
            {"date": "Q4 2023", "value": 0.0, "category": "AMD"},
            {"date": "Q1 2024", "value": 0.0, "category": "MSFT"},
            {"date": "Q1 2024", "value": 0.0, "category": "AMD"},
            {"date": "Q2 2024", "value": 0.0, "category": "MSFT"},
            {"date": "Q2 2024", "value": 0.0, "category": "AMD"},
        ]

        mock_get_user.return_value = mock_get_user_data

        response = main(dividend_req)
        assert response.status_code == 200
        assert response.get_body() == json.dumps(expected_result).encode("utf-8")

    @time_machine.travel("2022-12-03")
    @patch("shared_code.utils.get_user")
    @patch("shared_code.cosmosdb_module.cosmosdb_container")
    def test_input_transactions_quarter_interval(
        self, mock_cosmosdb_container, mock_get_user
    ):
        """Test get_barchart_data with valid input"""

        temp_copy = deepcopy(mock_input_transactions_data)
        temp_copy[0]["date"] = "2021-12-02"
        temp_copy[1]["date"] = "2021-12-03"

        mock_cosmosdb_container.return_value.query_items.return_value = temp_copy

        expected_result = [
            {"date": "Q4 2021", "value": 0.5, "category": "AMD"},
            {"date": "Q4 2021", "value": 0.5, "category": "MSFT"},
            {"date": "Q1 2022", "value": 0.0, "category": "AMD"},
            {"date": "Q1 2022", "value": 0.0, "category": "MSFT"},
            {"date": "Q2 2022", "value": 0.0, "category": "AMD"},
            {"date": "Q2 2022", "value": 0.0, "category": "MSFT"},
            {"date": "Q3 2022", "value": 0.0, "category": "AMD"},
            {"date": "Q3 2022", "value": 0.0, "category": "MSFT"},
            {"date": "Q4 2022", "value": 0.0, "category": "AMD"},
            {"date": "Q4 2022", "value": 0.0, "category": "MSFT"},
        ]

        mock_get_user.return_value = mock_get_user_data

        response = main(transaction_cost_req)
        assert response.status_code == 200
        assert response.get_body() == json.dumps(expected_result).encode("utf-8")

    @time_machine.travel("2022-01-04")
    @patch("shared_code.utils.get_user")
    @patch("shared_code.cosmosdb_module.cosmosdb_container")
    def test_input_transactions_month_interval(
        self, mock_cosmosdb_container, mock_get_user
    ):
        """Test get_barchart_data with valid input"""

        temp_copy = deepcopy(mock_input_transactions_data)
        temp_copy[0]["date"] = "2021-12-02"
        temp_copy[1]["date"] = "2021-12-03"

        mock_cosmosdb_container.return_value.query_items.return_value = temp_copy

        expected_result = [
            {"date": "2021 December", "value": 0.5, "category": "AMD"},
            {"date": "2021 December", "value": 0.5, "category": "MSFT"},
            {"date": "2022 January", "value": 0.0, "category": "AMD"},
            {"date": "2022 January", "value": 0.0, "category": "MSFT"},
        ]

        mock_get_user.return_value = mock_get_user_data

        response = main(transaction_cost_req)
        assert response.status_code == 200
        assert response.get_body() == json.dumps(expected_result).encode("utf-8")

    @time_machine.travel("2023-05-04")
    @patch("shared_code.utils.get_user")
    @patch("shared_code.cosmosdb_module.cosmosdb_container")
    def test_dividends_month_interval(self, mock_cosmosdb_container, mock_get_user):
        """Test get_barchart_data with valid input"""

        temp_copy = deepcopy(mock_stocks_held_data)
        temp_copy[0]["date"] = "2023-04-03"

        mock_cosmosdb_container.return_value.query_items.return_value = temp_copy
        expected_result = [
            {"date": "2023 April", "value": 0, "category": "MSFT"},
            {"date": "2023 April", "value": 0.0, "category": "AMD"},
            {"date": "2023 May", "value": 0, "category": "MSFT"},
            {"date": "2023 May", "value": 0, "category": "AMD"},
        ]

        mock_get_user.return_value = mock_get_user_data

        response = main(dividend_req)
        assert response.status_code == 200
        assert response.get_body() == json.dumps(expected_result).encode("utf-8")

    @time_machine.travel("2023-05-04")
    @patch("shared_code.utils.get_user")
    @patch("shared_code.cosmosdb_module.cosmosdb_container")
    def test_dividends_week_interval(self, mock_cosmosdb_container, mock_get_user):
        """Test get_barchart_data with valid input"""

        mock_cosmosdb_container.return_value.query_items.return_value = (
            mock_stocks_held_data
        )
        expected_result = [
            {"date": "2023 19", "value": 0, "category": "MSFT"},
            {"date": "2023 19", "value": 0, "category": "AMD"},
        ]

        mock_get_user.return_value = mock_get_user_data

        response = main(dividend_req)
        assert response.status_code == 200
        assert response.get_body() == json.dumps(expected_result).encode("utf-8")

    @time_machine.travel("2021-12-03")
    @patch("shared_code.utils.get_user")
    @patch("shared_code.cosmosdb_module.cosmosdb_container")
    def test_input_transactions_week_interval(
        self, mock_cosmosdb_container, mock_get_user
    ):
        """Test get_barchart_data with valid input"""

        temp_copy = deepcopy(mock_input_transactions_data)
        temp_copy[0]["date"] = "2021-12-02"
        temp_copy[1]["date"] = "2021-12-03"

        mock_cosmosdb_container.return_value.query_items.return_value = temp_copy

        mock_get_user.return_value = mock_get_user_data

        expected_result = [
            {"date": "2021 49", "value": 0.5, "category": "AMD"},
            {"date": "2021 49", "value": 0.5, "category": "MSFT"},
        ]

        response = main(transaction_cost_req)
        assert response.status_code == 200
        assert response.get_body() == json.dumps(expected_result).encode("utf-8")
