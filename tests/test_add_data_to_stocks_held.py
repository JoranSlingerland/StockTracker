"""Test add data to stocks held."""
import json
from pathlib import Path

from add_data_to_stocks_held import main


def test_all():
    """Test with all input"""
    with open(Path(__file__).parent / "data" / "transactions.json", "r") as f:
        mock_transactions = json.load(f)

    with open(Path(__file__).parent / "data" / "forex_data.json", "r") as f:
        mock_forex_data = json.load(f)

    with open(Path(__file__).parent / "data" / "stock_data.json", "r") as f:
        mock_stock_data = json.load(f)

    with open(Path(__file__).parent / "data" / "stocks_held_by_day.json", "r") as f:
        mock_stocks_held = json.load(f)

    with open(
        Path(__file__).parent / "data" / "add_data_to_stocks_held.json", "r"
    ) as f:
        expected_result = json.load(f)

    result = main(
        [
            mock_stocks_held,
            mock_stock_data,
            mock_forex_data,
            mock_transactions,
            "all",
            "123",
        ]
    )

    assert result[0] is None
    assert result[1] is None
    for d in result[2]:
        d.pop("id")

    assert result[2] == expected_result
