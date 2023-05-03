"""Test get_linechart_data.py"""

import datetime
import json
from unittest.mock import MagicMock, patch

from get_linechart_data import main
from shared_code.utils import create_form_func_request

mock_data_container_totals = [
    {
        "date": "2023-03-17",
        "total_invested": 1009,
        "realized": {
            "dividends": 0,
            "transaction_cost": 6,
            "value_pl": 75.872,
            "forex_pl": 5.1414668000000106,
            "total_pl": 75.01346680000002,
            "dividends_percentage": 0,
            "transaction_cost_percentage": 0.005946481665014866,
            "value_pl_percentage": 0.07519524281466798,
            "forex_pl_percentage": 0.005095606342913787,
            "total_pl_percentage": 0.07434436749256691,
        },
        "unrealized": {
            "total_cost": 1375.1439999999998,
            "total_value": 1541.132028,
            "value_pl": 161.58002800000017,
            "forex_pl": 3.987917600000018,
            "total_pl": 165.9880280000002,
            "value_pl_percentage": 0.16013877898909828,
            "forex_pl_percentage": 0.003952346481665032,
            "total_pl_percentage": 0.16450746085232926,
        },
        "combined": {
            "value_pl": 237.45202800000015,
            "forex_pl": 9.129384400000028,
            "total_pl": 241.00149480000022,
            "value_pl_percentage": 0.23533402180376625,
            "forex_pl_percentage": 0.009047952824578818,
            "total_pl_percentage": 0.23885182834489616,
        },
        "userid": "123",
        "id": "ced537b3-1034-49b9-b80f-dfd24deb24c2",
    },
    {
        "date": "2023-03-18",
        "total_invested": 1009,
        "realized": {
            "dividends": 0,
            "transaction_cost": 6,
            "value_pl": 75.872,
            "forex_pl": 5.1414668000000106,
            "total_pl": 75.01346680000002,
            "dividends_percentage": 0,
            "transaction_cost_percentage": 0.005946481665014866,
            "value_pl_percentage": 0.07519524281466798,
            "forex_pl_percentage": 0.005095606342913787,
            "total_pl_percentage": 0.07434436749256691,
        },
        "unrealized": {
            "total_cost": 1375.1439999999998,
            "total_value": 1552.1033880000002,
            "value_pl": 167.6873879999999,
            "forex_pl": 8.388378400000143,
            "total_pl": 176.95938800000044,
            "value_pl_percentage": 0.16619166303270555,
            "forex_pl_percentage": 0.008313556392467931,
            "total_pl_percentage": 0.17538095936570905,
        },
        "combined": {
            "value_pl": 243.5593879999999,
            "forex_pl": 13.529845200000153,
            "total_pl": 251.97285480000045,
            "value_pl_percentage": 0.24138690584737355,
            "forex_pl_percentage": 0.013409162735381718,
            "total_pl_percentage": 0.24972532685827598,
        },
        "userid": "123",
        "id": "8b269758-4359-4d15-b27c-df99e02d0395",
    },
]


def test_empty_body():
    """Test empty body"""
    req = create_form_func_request(
        {}, "http://localhost:7071/api/data/get_linechart_data"
    )

    response = main(req)
    assert (
        response.get_body()
        == b'{"status": "Please pass a name on the query string or in the request body"}'
    )
    assert response.status_code == 400


@patch("shared_code.cosmosdb_module.cosmosdb_container")
def test_empty_container_max(mock_cosmosdb_container):
    """Test empty container"""
    req = create_form_func_request(
        {
            "userId": "123",
            "dataType": "invested_and_value",
            "dataToGet": "max",
        },
        "http://localhost:7071/api/data/get_linechart_data",
    )

    mock_cosmosdb_container.return_value = MagicMock()
    mock_cosmosdb_container.return_value.query_items.return_value = []

    response = main(req)
    assert (
        response.get_body()
        == b'{"status": No data found in database for this timeframe"}'
    )
    assert response.status_code == 500


@patch("shared_code.cosmosdb_module.cosmosdb_container")
def test_empty_container_year(mock_cosmosdb_container):
    """Test empty container"""
    req = create_form_func_request(
        {
            "userId": "123",
            "dataType": "invested_and_value",
            "dataToGet": "year",
        },
        "http://localhost:7071/api/data/get_linechart_data",
    )

    mock_cosmosdb_container.return_value = MagicMock()
    mock_cosmosdb_container.return_value.query_items.return_value = []

    response = main(req)
    assert (
        response.get_body()
        == b'{"status": No data found in database for this timeframe"}'
    )
    assert response.status_code == 500


@patch("shared_code.cosmosdb_module.cosmosdb_container")
def test_invalid_datatype(mock_cosmosdb_container):
    """Test invalid datatype"""
    req = create_form_func_request(
        {
            "userId": "123",
            "dataType": "invalid",
            "dataToGet": "max",
        },
        "http://localhost:7071/api/data/get_linechart_data",
    )

    mock_cosmosdb_container.return_value = MagicMock()
    mock_cosmosdb_container.return_value.query_items.return_value = (
        mock_data_container_totals
    )

    response = main(req)
    assert response.get_body() == b'{"status": Invalid datatype provided"}'
    assert response.status_code == 400


@patch("shared_code.cosmosdb_module.cosmosdb_container")
def test_total_gains(mock_cosmosdb_container):
    """Test total gains"""
    req = create_form_func_request(
        {
            "userId": "123",
            "dataType": "total_gains",
            "dataToGet": "max",
        },
        "http://localhost:7071/api/data/get_linechart_data",
    )

    mock_cosmosdb_container.return_value = MagicMock()
    mock_cosmosdb_container.return_value.query_items.return_value = (
        mock_data_container_totals
    )

    start_date = datetime.datetime(2023, 3, 17)
    end_date = datetime.datetime.now()
    dates = [
        start_date + datetime.timedelta(days=x)
        for x in range((end_date - start_date).days + 1)
    ]

    expected_body = {
        "labels": [date.strftime("%Y-%m-%d") for date in dates],
        "datasets": [
            {
                "label": "Gains",
                "data": [165.9880280000002, 176.95938800000044],
            }
        ],
    }

    response = main(req)
    assert response.get_body() == json.dumps(expected_body).encode("utf-8")
    assert response.status_code == 200


@patch("shared_code.cosmosdb_module.cosmosdb_container")
def test_invested_and_value(mock_cosmosdb_container):
    """Test invested and value"""
    req = create_form_func_request(
        {
            "userId": "123",
            "dataType": "invested_and_value",
            "dataToGet": "max",
        },
        "http://localhost:7071/api/data/get_linechart_data",
    )

    mock_cosmosdb_container.return_value = MagicMock()
    mock_cosmosdb_container.return_value.query_items.return_value = (
        mock_data_container_totals
    )

    start_date = datetime.datetime(2023, 3, 17)
    end_date = datetime.datetime.now()
    dates = [
        start_date + datetime.timedelta(days=x)
        for x in range((end_date - start_date).days + 1)
    ]

    expected_body = {
        "labels": [date.strftime("%Y-%m-%d") for date in dates],
        "datasets": [
            {
                "label": "Value",
                "data": [1541.132028, 1552.1033880000002],
            },
            {"label": "Invested", "data": [1009, 1009]},
        ],
    }

    response = main(req)
    # response = json.loads(response.get_body().decode("utf-8"))s
    assert response.get_body() == json.dumps(expected_body).encode("utf-8")
    assert response.status_code == 200
