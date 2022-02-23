"""Get required environment variables"""

# Imports
import os
from dotenv import load_dotenv

#functions
def get_tables() -> dict:
    """Get tables"""
    tables = {
        "tables": [
            {"table_name": "cash_held", "columns": {"date": "DATE", "amount": "MONEY"}},
            {
                "table_name": "stocks_held",
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
                "columns": {
                    "date": "DATE",
                    "total_cost": "MONEY",
                    "total_value": "MONEY",
                },
            },
            {
                "table_name": "single_day",
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
