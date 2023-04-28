"""Test the delete_cosmosdb_items function."""

from unittest.mock import MagicMock, call, patch

import time_machine
from azure.cosmos import ContainerProxy

from items_to_delete import main

mock_items_1 = [
    {
        "id": "1",
    }
]

mock_items_2 = [
    {
        "id": "2",
    }
]


@time_machine.travel("2023-04-08")
@patch("shared_code.cosmosdb_module.cosmosdb_container")
def test_all(cosmosdb_container_mock):
    """Test the main function."""

    cosmosdb_container_mock.return_value = MagicMock(spec=ContainerProxy)

    cosmosdb_container_mock.return_value.query_items.side_effect = [
        mock_items_1,
        mock_items_2,
    ]

    result = main(["all", "123"])

    assert result == {
        "stocks_held": mock_items_1,
        "totals": mock_items_2,
    }

    cosmosdb_container_mock.assert_has_calls(
        [
            call("stocks_held"),
            call("totals"),
        ],
        any_order=True,
    )
    cosmosdb_container_mock.return_value.query_items.assert_has_calls(
        [
            call(
                query="SELECT * FROM c WHERE c.userid = @userid",
                parameters=[{"name": "@userid", "value": "123"}],
                enable_cross_partition_query=True,
            ),
            call(
                query="SELECT * FROM c WHERE c.userid = @userid",
                parameters=[{"name": "@userid", "value": "123"}],
                enable_cross_partition_query=True,
            ),
        ]
    )


@time_machine.travel("2023-04-08")
@patch("shared_code.cosmosdb_module.cosmosdb_container")
def test_days(cosmosdb_container_mock):
    """Test the main function."""

    cosmosdb_container_mock.return_value = MagicMock(spec=ContainerProxy)

    cosmosdb_container_mock.return_value.query_items.side_effect = [
        mock_items_1,
        mock_items_2,
    ]

    result = main([1, "123"])

    assert result == {
        "stocks_held": mock_items_1,
        "totals": mock_items_2,
    }

    cosmosdb_container_mock.assert_has_calls(
        [
            call("stocks_held"),
            call("totals"),
        ],
        any_order=True,
    )
    cosmosdb_container_mock.return_value.query_items.assert_has_calls(
        [
            call(
                query="SELECT * FROM c WHERE c.date >= @start_date and c.date <= @end_date and c.userid = @userid",
                parameters=[
                    {"name": "@start_date", "value": "2023-04-07"},
                    {"name": "@end_date", "value": "2023-04-08"},
                    {"name": "@userid", "value": "123"},
                ],
                enable_cross_partition_query=True,
            ),
            call(
                query="SELECT * FROM c WHERE c.date >= @start_date and c.date <= @end_date and c.userid = @userid",
                parameters=[
                    {"name": "@start_date", "value": "2023-04-07"},
                    {"name": "@end_date", "value": "2023-04-08"},
                    {"name": "@userid", "value": "123"},
                ],
                enable_cross_partition_query=True,
            ),
        ]
    )
