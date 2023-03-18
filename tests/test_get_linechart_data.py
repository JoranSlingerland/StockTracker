"""Test get_linechart_data.py"""

import json
from unittest.mock import MagicMock, patch

import azure.functions as func
from urllib3 import encode_multipart_formdata

from get_linechart_data import main

mock_data_container_totals = [
    {
        "date": "2023-03-17",
        "total_cost": 350,
        "total_value": 368.700256,
        "total_invested": 50,
        "total_pl": 318.700256,
        "total_pl_percentage": 6.3740051200000005,
        "total_dividends": 0,
        "transaction_cost": 2,
        "userid": "2e43b4a359f8d5bb81550495b114e9e3",
        "id": "907f8bda-bb92-4e40-b660-dce648268156",
        "_rid": "+qI9AMSGUAtbFAAAAAAAAA==",
        "_self": "dbs/+qI9AA==/colls/+qI9AMSGUAs=/docs/+qI9AMSGUAtbFAAAAAAAAA==/",
        "_etag": '"00000000-0000-0000-5925-1001a9d301d9"',
        "_attachments": "attachments/",
        "_ts": 1679094370,
    },
    {
        "date": "2023-03-18",
        "total_cost": 350,
        "total_value": 368.700256,
        "total_invested": 50,
        "total_pl": 318.700256,
        "total_pl_percentage": 6.3740051200000005,
        "total_dividends": 0,
        "transaction_cost": 2,
        "userid": "2e43b4a359f8d5bb81550495b114e9e3",
        "id": "d1ff60c2-f51f-40ec-93a6-8533124834cd",
        "_rid": "+qI9AMSGUAteFAAAAAAAAA==",
        "_self": "dbs/+qI9AA==/colls/+qI9AMSGUAs=/docs/+qI9AMSGUAteFAAAAAAAAA==/",
        "_etag": '"00000000-0000-0000-5925-11373c9f01d9"',
        "_attachments": "attachments/",
        "_ts": 1679094372,
    },
]


def test_empty_body():
    """Test empty body"""
    body, header = encode_multipart_formdata({})
    header = {"Content-Type": header}

    req = func.HttpRequest(
        method="POST",
        url="http://localhost:7071/api/data/get_linechart_data",
        headers=header,
        body=body,
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
    body, header = encode_multipart_formdata(
        {
            "userId": "2e43b4a359f8d5bb81550495b114e9e3",
            "dataType": "invested_and_value",
            "dataToGet": "max",
        }
    )
    header = {"Content-Type": header}

    req = func.HttpRequest(
        method="POST",
        url="http://localhost:7071/api/data/get_linechart_data",
        headers=header,
        body=body,
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
    body, header = encode_multipart_formdata(
        {
            "userId": "2e43b4a359f8d5bb81550495b114e9e3",
            "dataType": "invested_and_value",
            "dataToGet": "year",
        }
    )
    header = {"Content-Type": header}

    req = func.HttpRequest(
        method="POST",
        url="http://localhost:7071/api/data/get_linechart_data",
        headers=header,
        body=body,
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
    body, header = encode_multipart_formdata(
        {
            "userId": "2e43b4a359f8d5bb81550495b114e9e3",
            "dataType": "invalid",
            "dataToGet": "max",
        }
    )
    header = {"Content-Type": header}

    req = func.HttpRequest(
        method="POST",
        url="http://localhost:7071/api/data/get_linechart_data",
        headers=header,
        body=body,
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
    body, header = encode_multipart_formdata(
        {
            "userId": "2e43b4a359f8d5bb81550495b114e9e3",
            "dataType": "total_gains",
            "dataToGet": "max",
        }
    )
    header = {"Content-Type": header}

    req = func.HttpRequest(
        method="POST",
        url="http://localhost:7071/api/data/get_linechart_data",
        headers=header,
        body=body,
    )

    mock_cosmosdb_container.return_value = MagicMock()
    mock_cosmosdb_container.return_value.query_items.return_value = (
        mock_data_container_totals
    )

    expected_body = {
        "labels": ["2023-03-17", "2023-03-18"],
        "datasets": [
            {
                "label": "Gains",
                "borderColor": "#0e8505",
                "data": [318.700256, 318.700256],
            }
        ],
    }

    response = main(req)
    assert response.get_body() == json.dumps(expected_body).encode("utf-8")
    assert response.status_code == 200


@patch("shared_code.cosmosdb_module.cosmosdb_container")
def test_invested_and_value(mock_cosmosdb_container):
    """Test invested and value"""
    body, header = encode_multipart_formdata(
        {
            "userId": "2e43b4a359f8d5bb81550495b114e9e3",
            "dataType": "invested_and_value",
            "dataToGet": "max",
        }
    )
    header = {"Content-Type": header}

    req = func.HttpRequest(
        method="POST",
        url="http://localhost:7071/api/data/get_linechart_data",
        headers=header,
        body=body,
    )

    mock_cosmosdb_container.return_value = MagicMock()
    mock_cosmosdb_container.return_value.query_items.return_value = (
        mock_data_container_totals
    )

    expected_body = {
        "labels": ["2023-03-17", "2023-03-18"],
        "datasets": [
            {
                "label": "Value",
                "borderColor": "#0e8505",
                "data": [368.700256, 368.700256],
            },
            {"label": "Invested", "borderColor": "#090a09", "data": [50, 50]},
        ],
    }

    response = main(req)
    assert response.get_body() == json.dumps(expected_body).encode("utf-8")
    assert response.status_code == 200
