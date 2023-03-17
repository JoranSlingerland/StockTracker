"""Test get_pie_data.py"""
#pylint: disable=line-too-long

from unittest.mock import Mock, patch
from copy import deepcopy
import json
from urllib3 import encode_multipart_formdata
import azure.functions as func
from get_pie_data import main


def test_invalid_input():
    """Test invalid input"""
    body, header = encode_multipart_formdata({})
    header = {"Content-Type": header}

    mock_request = func.HttpRequest(
        method="POST",
        body=body,
        url="http://localhost:7071/api/data/get_pie_data",
        headers=header,
    )

    excepected_response = func.HttpResponse(
        body='{"status": "Please pass a name on the query string or in the request body"}',
        mimetype="application/json",
        status_code=400,
    )

    result = main(mock_request)
    assert result.status_code == excepected_response.status_code
    assert result.get_body() == excepected_response.get_body()


mock_container_response = [
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
            "open_value": 50,
            "high_value": 50,
            "low_value": 50,
            "close_value": 50,
            "total_value": 50,
            "total_pl": 50,
            "total_pl_percentage": 0.7046374400000002,
        },
        "combined": {
            "total_pl": 34.73187200000001,
            "total_pl_percentage": 0.6946374400000002,
        },
        "userid": "2e43b4a359f8d5bb81550495b114e9e3",
        "id": "0ab0b327-85c1-4e07-960e-70545591ddd7",
        "_rid": "+qI9AKgOiKMFAAAAAAAAAA==",
        "_self": "dbs/+qI9AA==/colls/+qI9AKgOiKM=/docs/+qI9AKgOiKMFAAAAAAAAAA==/",
        "_etag": '"00000000-0000-0000-5829-e912ca6b01d9"',
        "_attachments": "attachments/",
        "_ts": 1678986501,
    },
    {
        "date": "2023-03-16",
        "symbol": "AAPL",
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
            "open_value": 50,
            "high_value": 50,
            "low_value": 50,
            "close_value": 50,
            "total_value": 50,
            "total_pl": 50,
            "total_pl_percentage": 0.50,
        },
        "combined": {
            "total_pl": 34.73187200000001,
            "total_pl_percentage": 0.6946374400000002,
        },
        "userid": "2e43b4a359f8d5bb81550495b114e9e3",
        "id": "0ab0b327-85c1-4e07-960e-70545591ddd7",
        "_rid": "+qI9AKgOiKMFAAAAAAAAAA==",
        "_self": "dbs/+qI9AA==/colls/+qI9AKgOiKM=/docs/+qI9AKgOiKMFAAAAAAAAAA==/",
        "_etag": '"00000000-0000-0000-5829-e912ca6b01d9"',
        "_attachments": "attachments/",
        "_ts": 1678986501,
    },
]
mock_add_meta_data_response = deepcopy(mock_container_response)
mock_add_meta_data_response[0].update(
    {
        "meta": {
            "symbol": "AMD",
            "name": "AMD",
            "description": "Welcome to AMD's official site! Revolutionize your gaming experience with latest graphics processors, software technologies and drivers. Visit now and explore!",
            "country": "United States",
            "sector": "Information Technology",
            "domain": "amd.com",
            "logo": "https://logo.uplead.com/amd.com",
            "id": "1e35b293-5d71-415c-9f24-419fb63db02e",
            "_rid": "+qI9AIeCF8cBAAAAAAAAAA==",
            "_self": "dbs/+qI9AA==/colls/+qI9AIeCF8c=/docs/+qI9AIeCF8cBAAAAAAAAAA==/",
            "_etag": '"00000000-0000-0000-54f9-30607ecf01d9"',
            "_attachments": "attachments/",
            "_ts": 1678635721,
        },
    }
)
mock_add_meta_data_response[1].update(
    {
        "meta": {
            "symbol": "AAPL",
            "name": "Apple",
            "description": "Welcome to AMD's official site! Revolutionize your gaming experience with latest graphics processors, software technologies and drivers. Visit now and explore!",
            "country": "United States",
            "sector": "Information Technology",
            "domain": "apple.com",
            "logo": "https://logo.uplead.com/apple.com",
            "id": "1e35b293-5d71-415c-9f24-419fb63db02e",
            "_rid": "+qI9AIeCF8cBAAAAAAAAAA==",
            "_self": "dbs/+qI9AA==/colls/+qI9AIeCF8c=/docs/+qI9AIeCF8cBAAAAAAAAAA==/",
            "_etag": '"00000000-0000-0000-54f9-30607ecf01d9"',
            "_attachments": "attachments/",
            "_ts": 1678635721,
        },
    }
)


def test_datatype_stocks():
    """Test datatype of stocks"""
    body, header = encode_multipart_formdata(
        {
            "userId": "123",
            "dataType": "stocks",
        }
    )
    header = {"Content-Type": header}

    mock_request = func.HttpRequest(
        method="POST",
        body=body,
        url="http://localhost:7071/api/data/get_pie_data",
        headers=header,
    )

    expected_body = {
        "labels": ["AMD", "AAPL"],
        "data": [50, 50],
    }

    mock_container = Mock()
    mock_container.query_items.return_value = mock_container_response

    with patch(
        "shared_code.cosmosdb_module.cosmosdb_container", return_value=mock_container
    ), patch(
        "shared_code.utils.add_meta_data_to_stock_data",
        return_value=mock_add_meta_data_response,
    ):
        result = main(mock_request)
        body = json.loads(result.get_body().decode("utf-8"))
        assert result.status_code == 200
        assert body["labels"] == expected_body["labels"]
        assert body["data"] == expected_body["data"]


def test_datatype_currency():
    """Test datatype of currency"""
    body, header = encode_multipart_formdata(
        {
            "userId": "123",
            "dataType": "currency",
        }
    )
    header = {"Content-Type": header}

    mock_request = func.HttpRequest(
        method="POST",
        body=body,
        url="http://localhost:7071/api/data/get_pie_data",
        headers=header,
    )

    expected_body = {
        "labels": ["USD"],
        "data": [100],
    }

    mock_container = Mock()
    mock_container.query_items.return_value = mock_container_response

    with patch(
        "shared_code.cosmosdb_module.cosmosdb_container", return_value=mock_container
    ), patch(
        "shared_code.utils.add_meta_data_to_stock_data",
        return_value=mock_add_meta_data_response,
    ):
        result = main(mock_request)
        body = json.loads(result.get_body().decode("utf-8"))
        assert result.status_code == 200
        assert body["labels"] == expected_body["labels"]
        assert body["data"] == expected_body["data"]


def test_datatype_country():
    """Test datatype of country"""
    body, header = encode_multipart_formdata(
        {
            "userId": "123",
            "dataType": "country",
        }
    )
    header = {"Content-Type": header}

    mock_request = func.HttpRequest(
        method="POST",
        body=body,
        url="http://localhost:7071/api/data/get_pie_data",
        headers=header,
    )

    expected_body = {
        "labels": ["United States"],
        "data": [100],
    }

    mock_container = Mock()
    mock_container.query_items.return_value = mock_container_response

    with patch(
        "shared_code.cosmosdb_module.cosmosdb_container", return_value=mock_container
    ), patch(
        "shared_code.utils.add_meta_data_to_stock_data",
        return_value=mock_add_meta_data_response,
    ):
        result = main(mock_request)
        body = json.loads(result.get_body().decode("utf-8"))
        assert result.status_code == 200
        assert body["labels"] == expected_body["labels"]
        assert body["data"] == expected_body["data"]


def test_datatype_sector():
    """Test datatype of sector"""
    body, header = encode_multipart_formdata(
        {
            "userId": "123",
            "dataType": "sector",
        }
    )
    header = {"Content-Type": header}

    mock_request = func.HttpRequest(
        method="POST",
        body=body,
        url="http://localhost:7071/api/data/get_pie_data",
        headers=header,
    )

    expected_body = {
        "labels": ["Information Technology"],
        "data": [100],
    }

    mock_container = Mock()
    mock_container.query_items.return_value = mock_container_response

    with patch(
        "shared_code.cosmosdb_module.cosmosdb_container", return_value=mock_container
    ), patch(
        "shared_code.utils.add_meta_data_to_stock_data",
        return_value=mock_add_meta_data_response,
    ):
        result = main(mock_request)
        body = json.loads(result.get_body().decode("utf-8"))
        assert result.status_code == 200
        assert body["labels"] == expected_body["labels"]
        assert body["data"] == expected_body["data"]


def test_no_data_in_cosmosdb():
    """Test no data in cosmosdb"""

    body, header = encode_multipart_formdata(
        {
            "userId": "123",
            "dataType": "sector",
        }
    )
    header = {"Content-Type": header}

    mock_request = func.HttpRequest(
        method="POST",
        body=body,
        url="http://localhost:7071/api/data/get_pie_data",
        headers=header,
    )

    mock_container = Mock()
    mock_container.query_items.return_value = []

    with patch(
        "shared_code.cosmosdb_module.cosmosdb_container", return_value=mock_container
    ), patch(
        "shared_code.utils.add_meta_data_to_stock_data",
        return_value=[],
    ):
        result = main(mock_request)
        assert result.status_code == 400
