"""Get required environment variables"""

# Imports
import os
from dotenv import load_dotenv

# functions
def get_tables() -> dict:
    """Get tables"""
    tables = {
        "tables": [
            {
                "table_name": "invested",
                "candelete": True,
                "cantruncate": True,
                "input_table": False,
                "output_table": True,
                "columns": {"date": "DATE", "amount": "MONEY"},
            },
            {
                "table_name": "stocks_held",
                "candelete": True,
                "cantruncate": True,
                "input_table": False,
                "output_table": True,
                "columns": {
                    "date": "DATE",
                    "symbol": "TEXT",
                    "average_cost": "MONEY",
                    "total_cost": "MONEY",
                    "quantity": "DECIMAL(38,2)",
                    "transaction_cost": "MONEY",
                    "currency": "TEXT",
                    "close_value": "MONEY",
                    "high_value": "MONEY",
                    "low_value": "MONEY",
                    "open_value": "MONEY",
                    "volume": "DECIMAL(38,2)",
                    "total_value": "MONEY",
                },
            },
            {
                "table_name": "totals",
                "candelete": True,
                "cantruncate": True,
                "input_table": False,
                "output_table": True,
                "columns": {
                    "date": "DATE",
                    "total_cost": "MONEY",
                    "total_value": "MONEY",
                },
            },
            {
                "table_name": "single_day",
                "candelete": True,
                "cantruncate": True,
                "input_table": False,
                "output_table": True,
                "columns": {
                    "symbol": "TEXT",
                    "average_cost": "MONEY",
                    "total_cost": "MONEY",
                    "quantity": "DECIMAL(38,2)",
                    "transaction_cost": "MONEY",
                    "currency": "TEXT",
                    "close_value": "MONEY",
                    "high_value": "MONEY",
                    "low_value": "MONEY",
                    "open_value": "MONEY",
                    "volume": "DECIMAL(38,2)",
                    "total_value": "MONEY",
                },
            },
            {
                "table_name": "input_transactions",
                "candelete": False,
                "cantruncate": False,
                "input_table": True,
                "output_table": False,
                "columns": {
                    "symbol": "TEXT",
                    "transaction_date": "DATE",
                    "cost": "MONEY",
                    "quantity": "DECIMAL(38,2)",
                    "transaction_type": "TEXT",
                    "transaction_cost": "MONEY",
                    "currency": "TEXT",
                },
            },
            {
                "table_name": "input_invested",
                "candelete": False,
                "cantruncate": False,
                "input_table": True,
                "output_table": False,
                "columns": {
                    "transaction_date": "DATE",
                    "transaction_type": "TEXT",
                    "amount": "MONEY",
                },
            },
        ]
    }

    return tables


def get_sqlserver() -> dict:
    """Get sqlserver"""

    load_dotenv()

    sql_server = {
        "sql_server": {
            "server": os.environ["SERVER"],
            "database": os.environ["DATABASE"],
            "user": os.environ["USER"],
            "password": os.environ["PASSWORD"],
        }
    }
    return sql_server


def get_api_key() -> str:
    """Get api key"""

    load_dotenv()

    api_key = os.environ["API_KEY"]

    return api_key
