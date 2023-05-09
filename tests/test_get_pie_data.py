"""Test get_pie_data.py"""

import json
from pathlib import Path
from unittest.mock import patch

import time_machine

from get_pie_data import main
from shared_code.utils import create_form_func_request

with open(Path(__file__).parent / "data" / "stocks_held_data.json", "r") as f:
    mock_stocks_held_data = json.load(f)


def add_meta_data(result, container):
    """ "Add meta data to result"""
    for item in result:
        item["meta"] = {
            "country": "test",
            "sector": "test",
        }
    return result


class TestValidRequest:
    """Valid request class"""

    @time_machine.travel("2023-04-02")
    @patch("shared_code.cosmosdb_module.cosmosdb_container")
    @patch("shared_code.utils.add_meta_data_to_stock_data")
    def test_datatype_stocks(
        self, mock_add_meta_data_to_stock_data, mock_cosmosdb_container
    ):
        """Test datatype of stocks"""

        mock_cosmosdb_container.return_value.query_items.return_value = (
            mock_stocks_held_data
        )
        mock_add_meta_data_to_stock_data.side_effect = add_meta_data

        req = create_form_func_request(
            {
                "userId": "123",
                "dataType": "stocks",
            },
            "http://localhost:7071/api/data/get_pie_data",
        )
        expected_body = {
            "labels": ["AMD", "MSFT"],
            "data": [1493.7020429999998, 0],
        }

        result = main(req)
        body = json.loads(result.get_body().decode("utf-8"))
        assert result.status_code == 200
        assert body["labels"] == expected_body["labels"]
        assert body["data"] == expected_body["data"]

    @time_machine.travel("2023-04-02")
    @patch("shared_code.cosmosdb_module.cosmosdb_container")
    @patch("shared_code.utils.add_meta_data_to_stock_data")
    def test_datatype_currency(
        self, mock_add_meta_data_to_stock_data, mock_cosmosdb_container
    ):
        """Test datatype of currency"""

        mock_cosmosdb_container.return_value.query_items.return_value = (
            mock_stocks_held_data
        )
        mock_add_meta_data_to_stock_data.side_effect = add_meta_data

        req = create_form_func_request(
            {
                "userId": "123",
                "dataType": "currency",
            },
            "http://localhost:7071/api/data/get_pie_data",
        )

        expected_body = {
            "labels": ["USD"],
            "data": [1493.7020429999998],
        }

        result = main(req)
        body = json.loads(result.get_body().decode("utf-8"))
        assert result.status_code == 200
        assert body["labels"] == expected_body["labels"]
        assert body["data"] == expected_body["data"]

    @time_machine.travel("2023-04-02")
    @patch("shared_code.cosmosdb_module.cosmosdb_container")
    @patch("shared_code.utils.add_meta_data_to_stock_data")
    def test_datatype_country(
        self, mock_add_meta_data_to_stock_data, mock_cosmosdb_container
    ):
        """Test datatype of country"""

        mock_cosmosdb_container.return_value.query_items.return_value = (
            mock_stocks_held_data
        )
        mock_add_meta_data_to_stock_data.side_effect = add_meta_data

        req = create_form_func_request(
            {
                "userId": "123",
                "dataType": "country",
            },
            "http://localhost:7071/api/data/get_pie_data",
        )

        expected_body = {
            "labels": ["test"],
            "data": [1493.7020429999998],
        }

        result = main(req)
        body = json.loads(result.get_body().decode("utf-8"))
        assert result.status_code == 200
        assert body["labels"] == expected_body["labels"]
        assert body["data"] == expected_body["data"]

    @time_machine.travel("2023-04-02")
    @patch("shared_code.cosmosdb_module.cosmosdb_container")
    @patch("shared_code.utils.add_meta_data_to_stock_data")
    def test_datatype_sector(
        self, mock_add_meta_data_to_stock_data, mock_cosmosdb_container
    ):
        """Test datatype of sector"""

        mock_cosmosdb_container.return_value.query_items.return_value = (
            mock_stocks_held_data
        )
        mock_add_meta_data_to_stock_data.side_effect = add_meta_data

        req = create_form_func_request(
            {
                "userId": "123",
                "dataType": "sector",
            },
            "http://localhost:7071/api/data/get_pie_data",
        )

        expected_body = {
            "labels": ["test"],
            "data": [1493.7020429999998],
        }

        result = main(req)
        body = json.loads(result.get_body().decode("utf-8"))
        assert result.status_code == 200
        assert body["labels"] == expected_body["labels"]
        assert body["data"] == expected_body["data"]


class TestInvalidRequest:
    """Test invalid requests"""

    @time_machine.travel("2023-04-02")
    def test_invalid_input(self):
        """Test invalid input"""
        req = create_form_func_request(
            {}, "http://localhost:7071/api/data/get_pie_data"
        )

        result = main(req)
        assert result.status_code == 400
        assert (
            result.get_body()
            == b'{"status": "Please pass a name on the query string or in the request body"}'
        )

    @time_machine.travel("2023-04-02")
    @patch("shared_code.cosmosdb_module.cosmosdb_container")
    @patch("shared_code.utils.add_meta_data_to_stock_data")
    def test_invalid_datatype(
        self, mock_add_meta_data_to_stock_data, mock_cosmosdb_container
    ):
        """Test invalid datatype"""

        mock_cosmosdb_container.return_value.query_items.return_value = (
            mock_stocks_held_data
        )
        mock_add_meta_data_to_stock_data.side_effect = add_meta_data

        req = create_form_func_request(
            {
                "userId": "123",
                "dataType": "invalid",
            },
            "http://localhost:7071/api/data/get_pie_data",
        )

        result = main(req)
        assert result.status_code == 400
        assert (
            result.get_body()
            == b'{"status": Please pass a valid name on the query string or in the request body"}'
        )


class TestEdgeCases:
    """Test edge cases"""

    @time_machine.travel("2023-04-02")
    @patch("shared_code.cosmosdb_module.cosmosdb_container")
    @patch("shared_code.utils.add_meta_data_to_stock_data")
    def test_no_data_in_cosmosdb(
        self, mock_add_meta_data_to_stock_data, mock_cosmosdb_container
    ):
        """Test no data in cosmosdb"""

        mock_cosmosdb_container.return_value.query_items.return_value = []
        mock_add_meta_data_to_stock_data.side_effect = add_meta_data

        req = create_form_func_request(
            {
                "userId": "123",
                "dataType": "sector",
            },
            "http://localhost:7071/api/data/get_pie_data",
        )

        result = main(req)
        assert result.status_code == 400
        assert (
            result.get_body()
            == b'{"status": Please pass a valid name on the query string or in the request body"}'
        )
