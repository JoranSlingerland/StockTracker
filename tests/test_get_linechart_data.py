"""Test get_linechart_data.py"""

import json
from pathlib import Path
from unittest.mock import patch

import time_machine

from get_linechart_data import main
from shared_code.utils import create_form_func_request

with open(Path(__file__).parent / "data" / "totals_data.json", "r") as f:
    mock_totals_data = json.load(f)

with open(Path(__file__).parent / "data" / "get_user_data.json", "r") as f:
    mock_get_user_data = json.load(f)


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
                "userId": "123",
                "dataType": "total_gains",
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
                "userId": "123",
                "dataType": "total_gains",
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
                "userId": "123",
                "dataType": "total_gains",
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
                "userId": "123",
                "dataType": "total_gains",
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
    def test_empty_container_max(self, mock_cosmosdb_container, mock_get_user):
        """Test empty container"""
        req = create_form_func_request(
            {
                "userId": "123",
                "dataType": "invested_and_value",
                "allData": "true",
            },
            "http://localhost:7071/api/data/get_linechart_data",
        )

        mock_cosmosdb_container.return_value.query_items.return_value = []
        mock_get_user.return_value = mock_get_user_data

        response = main(req)
        assert (
            response.get_body()
            == b'{"status": No data found in database for this time frame"}'
        )
        assert response.status_code == 500

    @patch("shared_code.utils.get_user")
    @patch("shared_code.cosmosdb_module.cosmosdb_container")
    def test_empty_container_year(self, mock_cosmosdb_container, mock_get_user):
        """Test empty container"""
        req = create_form_func_request(
            {
                "userId": "123",
                "dataType": "invested_and_value",
                "startDate": "2023-05-01",
                "endDate": "2024-05-01",
            },
            "http://localhost:7071/api/data/get_linechart_data",
        )

        mock_cosmosdb_container.return_value.query_items.return_value = []
        mock_get_user.return_value = mock_get_user_data

        response = main(req)
        assert (
            response.get_body()
            == b'{"status": No data found in database for this time frame"}'
        )
        assert response.status_code == 500


class TestValidRequest:
    """Test valid request"""

    @time_machine.travel("2023-05-04")
    @patch("shared_code.utils.get_user")
    @patch("shared_code.cosmosdb_module.cosmosdb_container")
    def test_total_gains(self, mock_cosmosdb_container, mock_get_user):
        """Test total gains"""
        req = create_form_func_request(
            {
                "userId": "123",
                "dataType": "total_gains",
                "allData": "true",
            },
            "http://localhost:7071/api/data/get_linechart_data",
        )

        mock_cosmosdb_container.return_value.query_items.return_value = mock_totals_data
        mock_get_user.return_value = mock_get_user_data

        expected_body = {
            "labels": ["2023-05-03", "2023-05-04"],
            "datasets": [{"label": "Gains", "data": [26.140808000000334, 118.558043]}],
        }

        response = main(req)
        assert response.get_body() == json.dumps(expected_body).encode("utf-8")
        assert response.status_code == 200

    @time_machine.travel("2023-05-04")
    @patch("shared_code.utils.get_user")
    @patch("shared_code.cosmosdb_module.cosmosdb_container")
    def test_invested_and_value(self, mock_cosmosdb_container, mock_get_user):
        """Test invested and value"""
        req = create_form_func_request(
            {
                "userId": "123",
                "dataType": "invested_and_value",
                "allData": "true",
            },
            "http://localhost:7071/api/data/get_linechart_data",
        )

        mock_cosmosdb_container.return_value.query_items.return_value = mock_totals_data
        mock_get_user.return_value = mock_get_user_data

        expected_body = {
            "labels": ["2023-05-03", "2023-05-04"],
            "datasets": [
                {
                    "label": "Value",
                    "data": [1401.284808, 1493.7020429999998],
                },
                {"label": "Invested", "data": [1009, 1009]},
            ],
        }

        response = main(req)
        assert response.get_body() == json.dumps(expected_body).encode("utf-8")
        assert response.status_code == 200
