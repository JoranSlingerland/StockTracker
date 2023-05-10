"""test get_table_data_performance_v2.py"""

import json
from pathlib import Path
from unittest.mock import patch

from get_table_data_performance import main
from shared_code.utils import create_form_func_request

with open(Path(__file__).parent / "data" / "totals_data.json", "r") as f:
    mock_totals_data = json.load(f)

with open(Path(__file__).parent / "data" / "stocks_held_data.json", "r") as f:
    mock_stocks_held_data = json.load(f)

with open(Path(__file__).parent / "data" / "get_user_data.json", "r") as f:
    mock_get_user_data = json.load(f)


def add_meta_data(result, container):
    """ "Add meta data to result"""
    for item in result:
        item["meta"] = {
            "test": "test",
        }
    return result


class TestInvalidRequest:
    """Test invalid request."""

    def test_invalid_start_date(self):
        """Test invalid request."""

        req = create_form_func_request(
            {
                "userId": "123",
                "containerName": "totals",
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
                "containerName": "totals",
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
                "containerName": "totals",
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
                "containerName": "totals",
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


class TestValidRequest:
    """Test valid request."""

    @patch("shared_code.utils.get_user")
    @patch("shared_code.cosmosdb_module.cosmosdb_container")
    def test_max_totals(self, mock_cosmosdb_container, mock_get_user):
        """Text max totals."""

        mock_cosmosdb_container.return_value.query_items.return_value = mock_totals_data
        mock_get_user.return_value = mock_get_user_data

        req = create_form_func_request(
            {
                "userId": "123",
                "containerName": "totals",
                "allData": "true",
            },
            "https://localhost:7071/api/data/get_table_data_performance_v2",
        )

        result = main(req)

        assert result.status_code == 200
        result_body = json.loads(result.get_body().decode("utf-8"))
        assert result_body == [mock_totals_data[1]]

    @patch("shared_code.utils.get_user")
    @patch("shared_code.cosmosdb_module.cosmosdb_container")
    def test_totals_with_dates(self, mock_cosmosdb_container, mock_get_user):
        """Test totals with dates."""

        mock_cosmosdb_container.return_value.query_items.return_value = mock_totals_data
        mock_get_user.return_value = mock_get_user_data

        req = create_form_func_request(
            {
                "userId": "123",
                "containerName": "totals",
                "startDate": "2023-05-03",
                "endDate": "2023-05-04",
            },
            "https://localhost:7071/api/data/get_table_data_performance_v2",
        )

        result = main(req)

        expected_result = {
            "date": "2023-05-04",
            "total_invested": 1009,
            "realized": {
                "dividends": 0,
                "transaction_cost": 0,
                "value_pl": 0.0,
                "forex_pl": 0.0,
                "total_pl": 0.0,
                "dividends_percentage": 0.0,
                "transaction_cost_percentage": 0,
                "value_pl_percentage": 0,
                "forex_pl_percentage": 0,
                "total_pl_percentage": 0,
            },
            "unrealized": {
                "total_cost": 1375.1439999999998,
                "total_value": 1493.7020429999998,
                "value_pl": 86.18523499999975,
                "forex_pl": 5.638090399999989,
                "total_pl": 92.41723499999966,
                "value_pl_percentage": 0.08541648662041601,
                "forex_pl_percentage": 0.005587800198216045,
                "total_pl_percentage": 0.09159289890981136,
            },
            "combined": {
                "value_pl": 86.18523499999975,
                "forex_pl": 5.63809039999999,
                "total_pl": 92.41723499999965,
                "value_pl_percentage": 0.08541648662041601,
                "forex_pl_percentage": 0.0055878001982160455,
                "total_pl_percentage": 0.09159289890981134,
            },
            "userid": "123",
            "id": "b2954b62-849e-4957-818c-196fa81ea55f",
            "_rid": "+qI9AO2pFabSXAAAAAAAAA==",
            "_self": "dbs/+qI9AA==/colls/+qI9AO2pFaY=/docs/+qI9AO2pFabSXAAAAAAAAA==/",
            "_etag": '"00000000-0000-0000-7ec8-fba9b53501d9"',
            "_attachments": "attachments/",
            "_ts": 1683232966,
        }

        assert result.status_code == 200
        result_body = json.loads(result.get_body().decode("utf-8"))
        assert result_body == [expected_result]

    @patch("shared_code.utils.get_user")
    @patch("shared_code.cosmosdb_module.cosmosdb_container")
    @patch("shared_code.utils.add_meta_data_to_stock_data")
    def test_stock_data(
        self, mock_add_meta_data_to_stock_data, mock_cosmosdb_container, mock_get_user
    ):
        """Test stock data."""

        mock_cosmosdb_container.return_value.query_items.return_value = (
            mock_stocks_held_data
        )
        mock_add_meta_data_to_stock_data.side_effect = add_meta_data
        mock_get_user.return_value = mock_get_user_data

        req = create_form_func_request(
            {
                "userId": "123",
                "containerName": "stocks_held",
                "startDate": "2023-05-03",
                "endDate": "2023-05-04",
            },
            "https://localhost:7071/api/data/get_table_data_performance_v2",
        )

        result = main(req)

        expected_result = [
            {
                "date": "2023-05-04",
                "symbol": "MSFT",
                "currency": "USD",
                "fully_realized": True,
                "partial_realized": False,
                "realized": {
                    "cost_per_share_buy": 182.5,
                    "cost_per_share_buy_foreign": 200,
                    "cost_per_share_sell": 265.552,
                    "cost_per_share_sell_foreign": 280,
                    "buy_price": 0.0,
                    "buy_price_foreign": 200,
                    "sell_price": 0.0,
                    "sell_price_foreign": 280,
                    "average_buy_fx_rate": 0.9125,
                    "average_sell_fx_rate": 0.9484,
                    "quantity": 0,
                    "transaction_cost": 0.0,
                    "dividend": 0,
                    "total_dividends": 0,
                    "value_pl": 0.0,
                    "forex_pl": 0.0,
                    "total_pl": 0.0,
                    "value_pl_percentage": 0.0,
                    "forex_pl_percentage": 0.0,
                    "total_pl_percentage": 0.0,
                },
                "unrealized": {
                    "cost_per_share": 0,
                    "cost_per_share_foreign": 0,
                    "total_cost": 0,
                    "total_cost_foreign": 0,
                    "average_fx_rate": 0,
                    "quantity": 0,
                    "open_value": 277.974048,
                    "high_value": 279.353752,
                    "low_value": 275.39617999999996,
                    "close_value": 277.220657,
                    "total_value": 0,
                    "value_pl": 0,
                    "forex_pl": 0,
                    "total_pl": 0,
                    "total_pl_percentage": 0,
                    "value_pl_percentage": 0,
                    "forex_pl_percentage": 0,
                },
                "combined": {
                    "value_pl": 0.0,
                    "forex_pl": 0.0,
                    "total_pl": 0.0,
                    "value_pl_percentage": 0,
                    "forex_pl_percentage": 0,
                    "dividend_pl_percentage": 0,
                    "transaction_cost_percentage": 0.0027397260273972603,
                    "total_pl_percentage": 0,
                },
                "userid": "123",
                "id": "564faf16-d658-4542-940f-a25c59416726",
                "_rid": "+qI9AO8k4CsHNgAAAAAAAA==",
                "_self": "dbs/+qI9AA==/colls/+qI9AO8k4Cs=/docs/+qI9AO8k4CsHNgAAAAAAAA==/",
                "_etag": '"00000000-0000-0000-7ec8-f4cc056001d9"',
                "_attachments": "attachments/",
                "_ts": 1683232954,
                "meta": {"test": "test"},
            },
            {
                "date": "2023-05-04",
                "symbol": "AMD",
                "currency": "USD",
                "fully_realized": False,
                "partial_realized": True,
                "realized": {
                    "cost_per_share_buy": 73.03200000000007,
                    "cost_per_share_buy_foreign": 80,
                    "cost_per_share_sell": 72.52,
                    "cost_per_share_sell_foreign": 80,
                    "buy_price": 0.0,
                    "buy_price_foreign": 240,
                    "sell_price": 0.0,
                    "sell_price_foreign": 240,
                    "average_buy_fx_rate": 0.9129368276919706,
                    "average_sell_fx_rate": 0.9065,
                    "quantity": 0,
                    "transaction_cost": 0.0,
                    "dividend": 0,
                    "total_dividends": 0,
                    "value_pl": 0,
                    "forex_pl": 0.0,
                    "total_pl": 0.0,
                    "value_pl_percentage": 0.0,
                    "forex_pl_percentage": 0.0,
                    "total_pl_percentage": 0.0,
                },
                "unrealized": {
                    "cost_per_share": 72.37599999999999,
                    "cost_per_share_foreign": 80,
                    "total_cost": 1375.1439999999998,
                    "total_cost_foreign": 1520,
                    "average_fx_rate": 0.9047,
                    "quantity": 19,
                    "open_value": 74.04108899999999,
                    "high_value": 83.18162799999999,
                    "low_value": 73.623547,
                    "close_value": 78.61589699999999,
                    "total_value": 1493.7020429999998,
                    "value_pl": 86.18523499999975,
                    "forex_pl": 5.638090399999989,
                    "total_pl": 92.41723499999966,
                    "total_pl_percentage": 0.06595178544174987,
                    "value_pl_percentage": 0.06150443828974969,
                    "forex_pl_percentage": 0.004023514968414607,
                },
                "combined": {
                    "value_pl": 86.18523499999975,
                    "forex_pl": 5.638090399999989,
                    "total_pl": 92.41723499999966,
                    "value_pl_percentage": 0.06150443828974969,
                    "forex_pl_percentage": 0.004023514968414607,
                    "dividend_pl_percentage": 0,
                    "transaction_cost_percentage": 0.003449919710959454,
                    "total_pl_percentage": 0.06595178544174987,
                },
                "userid": "123",
                "id": "b8913991-067d-42d6-871d-71f0b434f9ed",
                "_rid": "+qI9AO8k4CsINgAAAAAAAA==",
                "_self": "dbs/+qI9AA==/colls/+qI9AO8k4Cs=/docs/+qI9AO8k4CsINgAAAAAAAA==/",
                "_etag": '"00000000-0000-0000-7ec8-f4ce55fd01d9"',
                "_attachments": "attachments/",
                "_ts": 1683232954,
                "meta": {"test": "test"},
            },
        ]

        assert result.status_code == 200
        result_body = json.loads(result.get_body().decode("utf-8"))
        assert result_body == expected_result


class TestEdgeCases:
    """Test edge cases."""

    @patch("shared_code.utils.get_user")
    @patch("shared_code.cosmosdb_module.cosmosdb_container")
    def test_no_data_max(self, mock_cosmosdb_container, mock_get_user):
        """Test no data."""

        mock_cosmosdb_container.return_value.query_items.return_value = []
        mock_get_user.return_value = mock_get_user_data

        req = create_form_func_request(
            {
                "userId": "123",
                "containerName": "totals",
                "allData": "true",
            },
            "https://localhost:7071/api/data/get_table_data_performance_v2",
        )

        result = main(req)

        assert result.status_code == 200
        result_body = json.loads(result.get_body().decode("utf-8"))
        assert result_body == []

    @patch("shared_code.utils.get_user")
    @patch("shared_code.cosmosdb_module.cosmosdb_container")
    def test_no_data_dates(self, mock_cosmosdb_container, mock_get_user):
        """Test no data."""

        mock_cosmosdb_container.return_value.query_items.return_value = []
        mock_get_user.return_value = mock_get_user_data

        req = create_form_func_request(
            {
                "userId": "123",
                "containerName": "totals",
                "startDate": "2021-12-02",
                "endDate": "2022-12-02",
            },
            "https://localhost:7071/api/data/get_table_data_performance_v2",
        )

        result = main(req)

        assert result.status_code == 200
        result_body = json.loads(result.get_body().decode("utf-8"))
        assert result_body == []

    @patch("shared_code.utils.get_user")
    @patch("shared_code.cosmosdb_module.cosmosdb_container")
    def test_no_data_stocks_held(self, mock_cosmosdb_container, mock_get_user):
        """Test no data."""

        mock_cosmosdb_container.return_value.query_items.return_value = []
        mock_get_user.return_value = mock_get_user_data

        req = create_form_func_request(
            {
                "userId": "123",
                "containerName": "stocks_held",
                "startDate": "2021-12-02",
                "endDate": "2022-12-02",
            },
            "https://localhost:7071/api/data/get_table_data_performance_v2",
        )

        result = main(req)

        assert result.status_code == 200
        result_body = json.loads(result.get_body().decode("utf-8"))
        assert result_body == []
