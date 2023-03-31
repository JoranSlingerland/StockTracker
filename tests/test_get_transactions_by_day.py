"""Test the get_transactions_by_day function."""
import json
from pathlib import Path

from get_transactions_by_day import main

invested_result = [
    {
        "date": "2023-03-27",
        "invested": 2000,
    },
    {
        "date": "2023-03-28",
        "invested": 1000,
    },
    {
        "date": "2023-03-29",
        "invested": 1000,
    },
]


def test_main_function():
    """Test main function."""

    with open(Path(__file__).parent / "data" / "transactions.json", "r") as f:
        transactions = json.load(f)

    with open(Path(__file__).parent / "data" / "forex_data.json", "r") as f:
        forex_data = json.load(f)

    with open(Path(__file__).parent / "data" / "stocks_held_by_day.json", "r") as f:
        stocks_held_result = json.load(f)

    payload = [transactions, forex_data]

    result = main(payload)

    assert "stock_held" in result
    assert "invested" in result
    for d in result["invested"]:
        d.pop("id")
    assert result["invested"] == invested_result
    assert result["stock_held"] == stocks_held_result
