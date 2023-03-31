"""Test the calculate_totals function."""

from calculate_totals import main

stocks_held = [
    {
        "date": "2023-03-27",
        "unrealized": {
            "total_cost": 100,
            "total_value": 200,
        },
        "realized": {
            "total_dividends": 0,
            "transaction_cost": 0,
        },
        "fully_realized": False,
    },
    {
        "date": "2023-03-28",
        "unrealized": {
            "total_cost": 100,
            "total_value": 200,
        },
        "realized": {
            "total_dividends": 2,
            "transaction_cost": 0.5,
        },
        "fully_realized": False,
    },
    {
        "date": "2023-03-28",
        "unrealized": {
            "total_cost": 100,
            "total_value": 200,
        },
        "realized": {
            "total_dividends": 5,
            "transaction_cost": 2,
        },
        "fully_realized": False,
    },
    {
        "date": "2023-03-29",
        "unrealized": {
            "total_cost": 100,
            "total_value": 200,
        },
        "realized": {
            "total_dividends": 2,
            "transaction_cost": 0,
        },
        "fully_realized": False,
    },
    {
        "date": "2023-03-29",
        "unrealized": {
            "total_cost": 100,
            "total_value": 200,
        },
        "realized": {
            "total_dividends": 0,
            "transaction_cost": 0,
        },
        "fully_realized": True,
    },
]

invested = [
    {
        "date": "2023-03-27",
        "invested": 100,
    },
    {
        "date": "2023-03-28",
        "invested": 100,
    },
    {
        "date": "2023-03-29",
        "invested": 100,
    },
]

mock_transactions = {"daterange": ["2023-03-27", "2023-03-28", "2023-03-29"]}

userid = "123"

expected_totals = [
    {
        "date": "2023-03-27",
        "total_cost": 100,
        "total_value": 200,
        "total_invested": 100,
        "total_pl": 100,
        "total_pl_percentage": 1.0,
        "total_dividends": 0,
        "transaction_cost": 0,
        "userid": "123",
    },
    {
        "date": "2023-03-28",
        "total_cost": 200,
        "total_value": 400,
        "total_invested": 100,
        "total_pl": 300,
        "total_pl_percentage": 3.0,
        "total_dividends": 7,
        "transaction_cost": 2.5,
        "userid": "123",
    },
    {
        "date": "2023-03-29",
        "total_cost": 100,
        "total_value": 200,
        "total_invested": 100,
        "total_pl": 100,
        "total_pl_percentage": 1.0,
        "total_dividends": 2,
        "transaction_cost": 0,
        "userid": "123",
    },
]


def test_main():
    """Test the main function."""
    result = main([stocks_held, invested, mock_transactions, userid])

    assert result[0] is None
    assert result[1] is None
    assert result[2]["stocks_held"] == stocks_held
    for d in result[2]["totals"]:
        d.pop("id")
    assert result[2]["totals"] == expected_totals
