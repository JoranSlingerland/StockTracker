"""Test the output_singleday_to_cosmosdb module."""

from datetime import date
from unittest.mock import call, patch

from output_singleday_to_cosmosdb import main

mock_payload = {
    "stocks_held": [
        {
            "date": "2021-01-01",
        },
        {
            "date": date.today().strftime("%Y-%m-%d"),
        },
    ],
    "totals": [
        {
            "date": "2021-01-01",
        },
        {
            "date": date.today().strftime("%Y-%m-%d"),
        },
    ],
}


@patch("shared_code.cosmosdb_module.cosmosdb_container")
def test_main(cosmosdb_container):
    """Test the main function."""

    main(mock_payload)

    container_calls = [
        call("single_day"),
        call().upsert_item({"date": date.today().strftime("%Y-%m-%d")}),
        call("single_day_totals"),
        call().upsert_item({"date": date.today().strftime("%Y-%m-%d")}),
    ]

    cosmosdb_container.assert_has_calls(container_calls)
