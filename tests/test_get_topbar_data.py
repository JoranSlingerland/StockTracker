"""Test the get_topbar_data function."""

import json
from copy import deepcopy
from unittest.mock import patch

import time_machine

from get_topbar_data import main
from shared_code.utils import create_form_func_request

mock_end_data = [
    {
        "date": "2023-04-02",
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
        "date": "2023-04-01",
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


@time_machine.travel("2023-04-02")
def test_empty_request():
    """Test empty request."""

    req = create_form_func_request(
        {}, "https://localhost:7071/api/data/get_topbar_data"
    )
    result = main(req)
    assert (
        result.get_body()
        == b'{"status": "Please pass a name on the query string or in the request body"}'
    )
    assert result.status_code == 400


@time_machine.travel("2023-04-02")
@patch("shared_code.cosmosdb_module.cosmosdb_container")
def test_max_request(mock_cosmosdb_container):
    """Test max request."""

    req = create_form_func_request(
        {"userId": "123", "dataToGet": "max"},
        "https://localhost:7071/api/data/get_topbar_data",
    )

    mock_cosmosdb_container.return_value.query_items.return_value = mock_end_data

    expected_body = {
        "total_value_gain": 1541.132028,
        "total_value_gain_percentage": 1,
        "total_pl": 165.9880280000002,
        "total_pl_percentage": 0.16450746085232926,
        "total_dividends": 0,
        "transaction_cost": 6,
    }

    result = main(req)
    assert result.status_code == 200
    assert json.loads(result.get_body()) == expected_body


@time_machine.travel("2023-04-02")
@patch("shared_code.cosmosdb_module.cosmosdb_container")
def test_week_request(mock_cosmosdb_container):
    """Test week request."""

    req = create_form_func_request(
        {"userId": "123", "dataToGet": "week"},
        "https://localhost:7071/api/data/get_topbar_data",
    )

    mock_cosmosdb_container.return_value.query_items.return_value = mock_end_data

    expected_body = {
        "total_value_gain": -10.971360000000232,
        "total_value_gain_percentage": -0.007068704369067604,
        "total_pl": -10.971360000000232,
        "total_pl_percentage": -0.007068704369067604,
        "total_dividends": 0,
        "transaction_cost": 0,
    }

    result = main(req)
    assert result.status_code == 200
    assert json.loads(result.get_body()) == expected_body


@time_machine.travel("2023-04-02")
@patch("shared_code.cosmosdb_module.cosmosdb_container")
def test_ytd_request(mock_cosmosdb_container):
    """Test ytd request."""

    req = create_form_func_request(
        {"userId": "123", "dataToGet": "ytd"},
        "https://localhost:7071/api/data/get_topbar_data",
    )

    single_mock_end_data = deepcopy(mock_end_data[0])
    single_mock_end_data["date"] = "2022-04-01"
    mock_end_data.append(single_mock_end_data)

    single_mock_end_data = deepcopy(mock_end_data[0])
    single_mock_end_data["date"] = "2023-01-01"
    mock_end_data.append(single_mock_end_data)

    mock_cosmosdb_container.return_value.query_items.return_value = mock_end_data

    expected_body = {
        "total_value_gain": 0.0,
        "total_value_gain_percentage": 0.0,
        "total_pl": 0.0,
        "total_pl_percentage": 0.0,
        "total_dividends": 0,
        "transaction_cost": 0,
    }

    result = main(req)
    # result = json.loads(result.get_body())
    assert result.status_code == 200
    assert json.loads(result.get_body()) == expected_body


@time_machine.travel("2023-04-02")
@patch("shared_code.cosmosdb_module.cosmosdb_container")
def test_empty_database(mock_cosmosdb_container):
    """Test week request."""

    req = create_form_func_request(
        {"userId": "123", "dataToGet": "week"},
        "https://localhost:7071/api/data/get_topbar_data",
    )

    mock_cosmosdb_container.return_value.query_items.return_value = []

    result = main(req)
    assert result.status_code == 500
    assert result.get_body() == b'{"status": "No data found"}'
