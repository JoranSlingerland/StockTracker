"""Test add_item_to_input.py"""
import datetime
import json
from unittest.mock import MagicMock, patch

from freezegun import freeze_time

from get_barchart_data import main
from shared_code.utils import create_form_func_request

mock_data_container_input_transactions = [
    {
        "symbol": "AMD",
        "date": "2023-03-16",
        "cost": 100,
        "quantity": 1,
        "transaction_type": "Buy",
        "transaction_cost": 0.5,
        "currency": "USD",
        "domain": "amd.com",
        "userid": "2e43b4a359f8d5bb81550495b114e9e3",
        "id": "9fc598da-546e-4bfb-8953-74ffdee70d79",
        "_rid": "+qI9ALp3obACAAAAAAAAAA==",
        "_self": "dbs/+qI9AA==/colls/+qI9ALp3obA=/docs/+qI9ALp3obACAAAAAAAAAA==/",
        "_etag": '"00000000-0000-0000-5850-d0a83f4901d9"',
        "_attachments": "attachments/",
        "_ts": 1679003210,
    },
    {
        "symbol": "AMD",
        "date": "2023-03-16",
        "cost": 100,
        "quantity": 1,
        "transaction_type": "Buy",
        "transaction_cost": 0.5,
        "currency": "USD",
        "domain": "amd.com",
        "userid": "2e43b4a359f8d5bb81550495b114e9e3",
        "id": "9fc598da-546e-4bfb-8953-74ffdee70d79",
        "_rid": "+qI9ALp3obACAAAAAAAAAA==",
        "_self": "dbs/+qI9AA==/colls/+qI9ALp3obA=/docs/+qI9ALp3obACAAAAAAAAAA==/",
        "_etag": '"00000000-0000-0000-5850-d0a83f4901d9"',
        "_attachments": "attachments/",
        "_ts": 1679003210,
    },
    {
        "symbol": "AMD",
        "date": "2023-03-16",
        "cost": 100,
        "quantity": 1,
        "transaction_type": "Buy",
        "transaction_cost": 0.5,
        "currency": "USD",
        "domain": "amd.com",
        "userid": "2e43b4a359f8d5bb81550495b114e9e3",
        "id": "a4c175d3-0328-4c02-8358-91a88b9f3762",
        "_rid": "+qI9ALp3obADAAAAAAAAAA==",
        "_self": "dbs/+qI9AA==/colls/+qI9ALp3obA=/docs/+qI9ALp3obADAAAAAAAAAA==/",
        "_etag": '"00000000-0000-0000-5850-dbe1f07a01d9"',
        "_attachments": "attachments/",
        "_ts": 1679003229,
    },
    {
        "symbol": "AMD",
        "date": "2023-03-16",
        "cost": 100,
        "quantity": 1,
        "transaction_type": "Buy",
        "transaction_cost": 0.5,
        "currency": "USD",
        "domain": "amd.com",
        "userid": "2e43b4a359f8d5bb81550495b114e9e3",
        "id": "17b81644-10f0-48cb-b1d9-1da46e4b5768",
        "_rid": "+qI9ALp3obAEAAAAAAAAAA==",
        "_self": "dbs/+qI9AA==/colls/+qI9ALp3obA=/docs/+qI9ALp3obAEAAAAAAAAAA==/",
        "_etag": '"00000000-0000-0000-5850-e0c997d901d9"',
        "_attachments": "attachments/",
        "_ts": 1679003237,
    },
]

mock_data_container_stocks_held = [
    {
        "date": "2023-03-16",
        "symbol": "AMD",
        "currency": "USD",
        "fully_realized": False,
        "partial_realized": False,
        "realized": {
            "cost_per_share_buy": 0,
            "cost_per_share_sell": 0,
            "buy_price": 0,
            "sell_price": 0,
            "average_buy_fx_rate": 0,
            "average_sell_fx_rate": 0,
            "quantity": 0,
            "transaction_cost": 2,
            "dividend": 0,
            "total_dividends": 0,
            "value_change": 0,
            "total_pl": -2,
            "value_change_percentage": 0,
            "total_pl_percentage": -0.005465086513412525,
        },
        "unrealized": {
            "cost_per_share": 87.5,
            "total_cost": 350,
            "average_fx_rate": 0.9258714285714286,
            "quantity": 4,
            "open_value": 84.97381200000001,
            "high_value": 91.57509900000001,
            "low_value": 84.310842,
            "close_value": 91.48986,
            "total_value": 365.95944,
            "total_pl": 15.959439999999972,
            "total_pl_percentage": 0.04559839999999992,
        },
        "combined": {
            "total_pl": 13.959439999999972,
            "total_pl_percentage": 0.03988411428571421,
        },
        "userid": "2e43b4a359f8d5bb81550495b114e9e3",
        "id": "4ad41752-4d66-4fb7-a43f-42fa63f367e4",
        "_rid": "+qI9AMKjpVxtEQAAAAAAAA==",
        "_self": "dbs/+qI9AA==/colls/+qI9AMKjpVw=/docs/+qI9AMKjpVxtEQAAAAAAAA==/",
        "_etag": '"00000000-0000-0000-58db-a9d9809401d9"',
        "_attachments": "attachments/",
        "_ts": 1679062845,
    },
    {
        "date": "2023-03-15",
        "symbol": "AMD",
        "currency": "USD",
        "fully_realized": False,
        "partial_realized": False,
        "realized": {
            "cost_per_share_buy": 0,
            "cost_per_share_sell": 0,
            "buy_price": 0,
            "sell_price": 0,
            "average_buy_fx_rate": 0,
            "average_sell_fx_rate": 0,
            "quantity": 0,
            "transaction_cost": 0.5,
            "dividend": 0,
            "total_dividends": 0,
            "value_change": 0,
            "total_pl": -0.5,
            "value_change_percentage": 0,
            "total_pl_percentage": -0.005866350090257315,
        },
        "unrealized": {
            "cost_per_share": 50,
            "total_cost": 50,
            "average_fx_rate": 0.8297,
            "quantity": 1,
            "open_value": 82.466208,
            "high_value": 85.935168,
            "low_value": 81.938736,
            "close_value": 85.23187200000001,
            "total_value": 85.23187200000001,
            "total_pl": 35.23187200000001,
            "total_pl_percentage": 0.7046374400000002,
        },
        "combined": {
            "total_pl": 34.73187200000001,
            "total_pl_percentage": 0.6946374400000002,
        },
        "userid": "2e43b4a359f8d5bb81550495b114e9e3",
        "id": "4cf73224-b55e-401f-80c4-0b380181111b",
        "_rid": "+qI9AMKjpVxqEQAAAAAAAA==",
        "_self": "dbs/+qI9AA==/colls/+qI9AMKjpVw=/docs/+qI9AMKjpVxqEQAAAAAAAA==/",
        "_etag": '"00000000-0000-0000-58db-a9d7278f01d9"',
        "_attachments": "attachments/",
        "_ts": 1679062845,
    },
    {
        "date": "2023-03-17",
        "symbol": "AMD",
        "currency": "USD",
        "fully_realized": False,
        "partial_realized": False,
        "realized": {
            "cost_per_share_buy": 0,
            "cost_per_share_sell": 0,
            "buy_price": 0,
            "sell_price": 0,
            "average_buy_fx_rate": 0,
            "average_sell_fx_rate": 0,
            "quantity": 0,
            "transaction_cost": 2,
            "dividend": 0,
            "total_dividends": 0,
            "value_change": 0,
            "total_pl": -2,
            "value_change_percentage": 0,
            "total_pl_percentage": -0.005465086513412525,
        },
        "unrealized": {
            "cost_per_share": 87.5,
            "total_cost": 350,
            "average_fx_rate": 0.9258714285714286,
            "quantity": 4,
            "open_value": 84.97381200000001,
            "high_value": 91.57509900000001,
            "low_value": 84.310842,
            "close_value": 91.48986,
            "total_value": 365.95944,
            "total_pl": 15.959439999999972,
            "total_pl_percentage": 0.04559839999999992,
        },
        "combined": {
            "total_pl": 13.959439999999972,
            "total_pl_percentage": 0.03988411428571421,
        },
        "userid": "2e43b4a359f8d5bb81550495b114e9e3",
        "id": "094d4f32-3677-425b-be76-47542671176b",
        "_rid": "+qI9AMKjpVxuEQAAAAAAAA==",
        "_self": "dbs/+qI9AA==/colls/+qI9AMKjpVw=/docs/+qI9AMKjpVxuEQAAAAAAAA==/",
        "_etag": '"00000000-0000-0000-58db-a9d99e0b01d9"',
        "_attachments": "attachments/",
        "_ts": 1679062845,
    },
]

end_date = datetime.datetime(2023, 3, 17)


def test_invalid_input():
    """ "Test get_barchart_data with invalid input"""
    req = create_form_func_request(
        {"invalid": "input"}, "http://localhost/api/data/get_barchart_data"
    )

    response = main(req)
    assert response.status_code == 400
    assert (
        response.get_body()
        == b'{"status": "Please pass a name on the query string or in the request body"}'
    )


@freeze_time("2023-03-17")
@patch("shared_code.cosmosdb_module.cosmosdb_container")
def test_input_transactions_max(mock_cosmosdb_container):
    """ "Test get_barchart_data with valid input"""
    req = create_form_func_request(
        {
            "userId": "2e43b4a359f8d5bb81550495b114e9e3",
            "dataType": "transaction_cost",
            "dataToGet": "max",
        },
        "http://localhost/api/data/get_barchart_data",
    )

    mock_cosmosdb_container.return_value = MagicMock()
    mock_cosmosdb_container.return_value.query_items.return_value = (
        mock_data_container_input_transactions
    )

    response = main(req)
    assert response.status_code == 200
    assert (
        response.get_body() == b'[{"date": "Q1 2023", "value": 2.0, "category": "AMD"}]'
    )


@patch("shared_code.date_time_helper.datatogetswitch")
@patch("shared_code.cosmosdb_module.cosmosdb_container")
def test_input_transactions_year(mock_cosmosdb_container, mock_datatogetswitch):
    """Test get_barchart_data with valid input"""
    req = create_form_func_request(
        {
            "userId": "2e43b4a359f8d5bb81550495b114e9e3",
            "dataType": "transaction_cost",
            "dataToGet": "year",
        },
        "http://localhost/api/data/get_barchart_data",
    )

    mock_cosmosdb_container.return_value = MagicMock()
    mock_cosmosdb_container.return_value.query_items.return_value = (
        mock_data_container_input_transactions
    )
    start_date = end_date - datetime.timedelta(days=365)
    mock_datatogetswitch.return_value = (start_date, end_date)

    response_body = [
        {"date": "2022 March", "value": 0.0, "category": "AMD"},
        {"date": "2022 April", "value": 0.0, "category": "AMD"},
        {"date": "2022 May", "value": 0.0, "category": "AMD"},
        {"date": "2022 June", "value": 0.0, "category": "AMD"},
        {"date": "2022 July", "value": 0.0, "category": "AMD"},
        {"date": "2022 August", "value": 0.0, "category": "AMD"},
        {"date": "2022 September", "value": 0.0, "category": "AMD"},
        {"date": "2022 October", "value": 0.0, "category": "AMD"},
        {"date": "2022 November", "value": 0.0, "category": "AMD"},
        {"date": "2022 December", "value": 0.0, "category": "AMD"},
        {"date": "2023 January", "value": 0.0, "category": "AMD"},
        {"date": "2023 February", "value": 0.0, "category": "AMD"},
        {"date": "2023 March", "value": 2.0, "category": "AMD"},
    ]

    response = main(req)
    assert response.status_code == 200
    # response.get_body()
    assert response.get_body() == json.dumps(response_body).encode()


@patch("shared_code.date_time_helper.datatogetswitch")
@patch("shared_code.cosmosdb_module.cosmosdb_container")
def test_input_transactions_month(mock_cosmosdb_container, mock_datatogetswitch):
    """Test get_barchart_data with valid input"""
    req = create_form_func_request(
        {
            "userId": "2e43b4a359f8d5bb81550495b114e9e3",
            "dataType": "transaction_cost",
            "dataToGet": "month",
        },
        "http://localhost/api/data/get_barchart_data",
    )

    mock_cosmosdb_container.return_value = MagicMock()
    mock_cosmosdb_container.return_value.query_items.return_value = (
        mock_data_container_input_transactions
    )
    start_date = end_date - datetime.timedelta(days=30)
    mock_datatogetswitch.return_value = (start_date, end_date)

    response_body = [
        {"date": "2023 08", "value": 0.0, "category": "AMD"},
        {"date": "2023 09", "value": 0.0, "category": "AMD"},
        {"date": "2023 10", "value": 0.0, "category": "AMD"},
        {"date": "2023 11", "value": 0.0, "category": "AMD"},
        {"date": "2023 12", "value": 2.0, "category": "AMD"},
    ]

    response = main(req)
    assert response.status_code == 200
    assert response.get_body() == json.dumps(response_body).encode()


@patch("shared_code.cosmosdb_module.cosmosdb_container")
def test_no_data(mock_cosmosdb_container):
    """Test get_barchart_data with no data"""
    req = create_form_func_request(
        {
            "userId": "2e43b4a359f8d5bb81550495b114e9e3",
            "dataType": "invalid",
            "dataToGet": "invalid",
        },
        "http://localhost/api/data/get_barchart_data",
    )

    mock_cosmosdb_container.return_value = MagicMock()
    mock_cosmosdb_container.return_value.query_items.return_value = []

    response = main(req)
    assert response.status_code == 400
    assert (
        response.get_body()
        == b'{"status": Please pass a valid name on the query string or in the request body"}'
    )


@freeze_time("2023-03-17")
@patch("shared_code.cosmosdb_module.cosmosdb_container")
def test_dividend_max(mock_cosmosdb_container):
    """Test get_barchart_data with valid input"""
    req = create_form_func_request(
        {
            "userId": "2e43b4a359f8d5bb81550495b114e9e3",
            "dataType": "dividend",
            "dataToGet": "max",
        },
        "http://localhost/api/data/get_barchart_data",
    )

    mock_cosmosdb_container.return_value = MagicMock()
    mock_cosmosdb_container.return_value.query_items.return_value = (
        mock_data_container_stocks_held
    )

    response_body = [{"date": "Q1 2023", "value": 0, "category": "AMD"}]

    response = main(req)
    assert response.status_code == 200
    assert json.loads(response.get_body().decode("utf-8")) == response_body


@patch("shared_code.date_time_helper.datatogetswitch")
@patch("shared_code.cosmosdb_module.cosmosdb_container")
def test_dividend_week(mock_cosmosdb_container, mock_datatogetswitch):
    """Test get_barchart_data with valid input"""
    req = create_form_func_request(
        {
            "userId": "2e43b4a359f8d5bb81550495b114e9e3",
            "dataType": "dividend",
            "dataToGet": "week",
        },
        "http://localhost/api/data/get_barchart_data",
    )

    mock_cosmosdb_container.return_value = MagicMock()
    mock_cosmosdb_container.return_value.query_items.return_value = (
        mock_data_container_stocks_held
    )
    start_date = end_date - datetime.timedelta(days=7)
    mock_datatogetswitch.return_value = (start_date, end_date)

    response_body = [
        {"date": "2023 11", "value": 0.0, "category": "AMD"},
        {"date": "2023 12", "value": 0, "category": "AMD"},
    ]

    response = main(req)
    assert response.status_code == 200
    assert response.get_body() == json.dumps(response_body).encode()
