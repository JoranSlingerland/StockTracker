"""Test the calculate_totals function."""

from calculate_totals import main

stocks_held = [
    {
        "date": "2023-03-27",
        "unrealized": {
            "total_cost": 100,
            "total_value": 200,
            "value_pl": 100,
            "forex_pl": -1,
            "total_pl": 99,
        },
        "realized": {
            "total_dividends": 0,
            "transaction_cost": 0,
            "value_pl": 50,
            "forex_pl": 5,
            "total_pl": 55,
        },
    },
    {
        "date": "2023-03-28",
        "unrealized": {
            "total_cost": 100,
            "total_value": 200,
            "value_pl": 100,
            "forex_pl": -1,
            "total_pl": 99,
        },
        "realized": {
            "total_dividends": 2,
            "transaction_cost": 0.5,
            "value_pl": 50,
            "forex_pl": 5,
            "total_pl": 56.5,
        },
    },
    {
        "date": "2023-03-28",
        "unrealized": {
            "total_cost": 100,
            "total_value": 200,
            "value_pl": 100,
            "forex_pl": 1,
            "total_pl": 99,
        },
        "realized": {
            "total_dividends": 5,
            "transaction_cost": 2,
            "value_pl": 50,
            "forex_pl": -5,
            "total_pl": 52,
        },
    },
    {
        "date": "2023-03-29",
        "unrealized": {
            "total_cost": 100,
            "total_value": 200,
            "value_pl": 100,
            "forex_pl": 1,
            "total_pl": 101,
        },
        "realized": {
            "total_dividends": 2,
            "transaction_cost": 0,
            "value_pl": 50,
            "forex_pl": -5,
            "total_pl": 47,
        },
    },
    {
        "date": "2023-03-29",
        "unrealized": {
            "total_cost": 100,
            "total_value": 200,
            "value_pl": 100,
            "forex_pl": 1,
            "total_pl": 101,
        },
        "realized": {
            "total_dividends": 0,
            "transaction_cost": 0,
            "value_pl": 50,
            "forex_pl": -5,
            "total_pl": 45,
        },
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
        "total_invested": 100,
        "realized": {
            "dividends": 0,
            "transaction_cost": 0,
            "value_pl": 50,
            "forex_pl": 5,
            "total_pl": 55,
            "dividends_percentage": 0.0,
            "transaction_cost_percentage": 0.0,
            "value_pl_percentage": 0.5,
            "forex_pl_percentage": 0.05,
            "total_pl_percentage": 0.55,
        },
        "unrealized": {
            "total_cost": 100,
            "total_value": 200,
            "value_pl": 100,
            "forex_pl": -1,
            "total_pl": 99,
            "value_pl_percentage": 1.0,
            "forex_pl_percentage": -0.01,
            "total_pl_percentage": 0.99,
        },
        "combined": {
            "value_pl": 150,
            "forex_pl": 4,
            "total_pl": 154,
            "value_pl_percentage": 1.5,
            "forex_pl_percentage": 0.04,
            "total_pl_percentage": 1.54,
        },
        "userid": "123",
    },
    {
        "date": "2023-03-28",
        "total_invested": 100,
        "realized": {
            "dividends": 7,
            "transaction_cost": 2.5,
            "value_pl": 100,
            "forex_pl": 0,
            "total_pl": 108.5,
            "dividends_percentage": 0.07,
            "transaction_cost_percentage": 0.025,
            "value_pl_percentage": 1.0,
            "forex_pl_percentage": 0.0,
            "total_pl_percentage": 1.085,
        },
        "unrealized": {
            "total_cost": 200,
            "total_value": 400,
            "value_pl": 200,
            "forex_pl": 0,
            "total_pl": 198,
            "value_pl_percentage": 2.0,
            "forex_pl_percentage": 0.0,
            "total_pl_percentage": 1.98,
        },
        "combined": {
            "value_pl": 300,
            "forex_pl": 0,
            "total_pl": 306.5,
            "value_pl_percentage": 3.0,
            "forex_pl_percentage": 0.0,
            "total_pl_percentage": 3.065,
        },
        "userid": "123",
    },
    {
        "date": "2023-03-29",
        "total_invested": 100,
        "realized": {
            "dividends": 2,
            "transaction_cost": 0,
            "value_pl": 100,
            "forex_pl": -10,
            "total_pl": 92,
            "dividends_percentage": 0.02,
            "transaction_cost_percentage": 0.0,
            "value_pl_percentage": 1.0,
            "forex_pl_percentage": -0.1,
            "total_pl_percentage": 0.92,
        },
        "unrealized": {
            "total_cost": 200,
            "total_value": 400,
            "value_pl": 200,
            "forex_pl": 2,
            "total_pl": 202,
            "value_pl_percentage": 2.0,
            "forex_pl_percentage": 0.02,
            "total_pl_percentage": 2.02,
        },
        "combined": {
            "value_pl": 300,
            "forex_pl": -8,
            "total_pl": 294,
            "value_pl_percentage": 3.0,
            "forex_pl_percentage": -0.08,
            "total_pl_percentage": 2.94,
        },
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
