"""Test the get_input_data module."""

from datetime import date
from unittest.mock import patch

import pandas as pd

from get_input_data import main

transactions_data = [
    {
        "symbol": "AMD",
        "date": "2021-01-01",
        "cost": 50,
        "quantity": 1,
        "transaction_type": "Buy",
        "transaction_cost": 0.5,
        "currency": "USD",
        "domain": "amd.com",
        "userid": "123",
        "id": "01d9b061-c616-4279-b04d-b148a99c7a10",
        "_rid": "+qI9ALp3obABAAAAAAAAAA==",
        "_self": "dbs/+qI9AA==/colls/+qI9ALp3obA=/docs/+qI9ALp3obABAAAAAAAAAA==/",
        "_etag": '"00000000-0000-0000-54f9-0febd00f01d9"',
        "_attachments": "attachments/",
        "_ts": 1678635667,
    },
    {
        "symbol": "MSFT",
        "date": "2022-01-01",
        "cost": 50,
        "quantity": 1,
        "transaction_type": "Buy",
        "transaction_cost": 0.5,
        "currency": "USD",
        "domain": "microsoft.com",
        "userid": "123",
        "id": "01d9b061-c616-4279-b04d-b148a99c7a10",
        "_rid": "+qI9ALp3obABAAAAAAAAAA==",
        "_self": "dbs/+qI9AA==/colls/+qI9ALp3obA=/docs/+qI9ALp3obABAAAAAAAAAA==/",
        "_etag": '"00000000-0000-0000-54f9-0febd00f01d9"',
        "_attachments": "attachments/",
        "_ts": 1678635667,
    },
]

invested_data = [
    {
        "date": "2020-03-01",
        "amount": 50,
        "transaction_type": "Deposit",
        "userid": "123",
        "id": "0feed671-78af-43b4-95d1-9a166d827d1d",
        "_rid": "+qI9AKFTQkoBAAAAAAAAAA==",
        "_self": "dbs/+qI9AA==/colls/+qI9AKFTQko=/docs/+qI9AKFTQkoBAAAAAAAAAA==/",
        "_etag": '"00000000-0000-0000-54f9-1b78100b01d9"',
        "_attachments": "attachments/",
        "_ts": 1678635686,
    }
]
user_data = [
    {
        "id": "123",
        "dark_mode": True,
        "clearbit_api_key": "123",
        "alpha_vantage_api_key": "123",
        "_rid": "+qI9AL5k7vYCAAAAAAAAAA==",
        "_self": "dbs/+qI9AA==/colls/+qI9AL5k7vY=/docs/+qI9AL5k7vYCAAAAAAAAAA==/",
        "_etag": '"00000000-0000-0000-7956-ed2637b301d9"',
        "_attachments": "attachments/",
        "_ts": 1682634223,
    }
]


@patch("shared_code.cosmosdb_module.cosmosdb_container")
def test_get_transactions(cosmosdb_container_mock):
    """Test the get_transactions module."""

    cosmosdb_container_mock.return_value.query_items.side_effect = [
        transactions_data,
        invested_data,
        user_data,
    ]
    start_date = date.fromisoformat("2021-01-01")
    end_date = date.today()
    daterange = [d.strftime("%Y-%m-%d") for d in pd.date_range(start_date, end_date)]

    payload = ["123"]

    result = main(payload)

    assert result["transactions"] == [
        {
            "symbol": "AMD",
            "date": "2021-01-01",
            "cost": 50,
            "quantity": 1,
            "transaction_type": "Buy",
            "transaction_cost": 0.5,
            "currency": "USD",
            "domain": "amd.com",
            "userid": "123",
            "id": "01d9b061-c616-4279-b04d-b148a99c7a10",
        },
        {
            "symbol": "MSFT",
            "date": "2022-01-01",
            "cost": 50,
            "quantity": 1,
            "transaction_type": "Buy",
            "transaction_cost": 0.5,
            "currency": "USD",
            "domain": "microsoft.com",
            "userid": "123",
            "id": "01d9b061-c616-4279-b04d-b148a99c7a10",
        },
    ]
    assert result["invested"] == [
        {
            "date": "2020-03-01",
            "amount": 50,
            "transaction_type": "Deposit",
            "userid": "123",
            "id": "0feed671-78af-43b4-95d1-9a166d827d1d",
        }
    ]
    assert result["daterange"] == daterange
    assert result["symbols"] == ["AMD", "MSFT"]
    assert result["user_data"] == {
        "id": "123",
        "dark_mode": True,
        "clearbit_api_key": "123",
        "alpha_vantage_api_key": "123",
    }
    assert cosmosdb_container_mock.return_value.query_items.call_count == 3
    assert cosmosdb_container_mock.return_value.query_items.call_args_list[0][1] == {
        "query": "SELECT * FROM c WHERE c.userid = @userid",
        "parameters": [{"name": "@userid", "value": "123"}],
        "enable_cross_partition_query": True,
    }
    assert cosmosdb_container_mock.return_value.query_items.call_args_list[1][1] == {
        "query": "SELECT * FROM c WHERE c.userid = @userid",
        "parameters": [{"name": "@userid", "value": "123"}],
        "enable_cross_partition_query": True,
    }
    assert cosmosdb_container_mock.return_value.query_items.call_args_list[2][1] == {
        "query": "SELECT * FROM c WHERE c.id = @userid",
        "parameters": [{"name": "@userid", "value": "123"}],
        "enable_cross_partition_query": True,
    }
