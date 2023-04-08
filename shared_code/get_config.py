"""Get required environment variables"""

# Imports
import os

from dotenv import load_dotenv


# functions
def get_api_key() -> str:
    """Get api key"""

    load_dotenv()

    return os.environ["API_KEY"]


def get_clearbit_api_key() -> str:
    """Get clearbit api key"""

    load_dotenv()

    return os.environ["CLEARBIT_API_KEY"]


def get_cosmosdb() -> dict[str, str]:
    """Get cosmosdb"""

    load_dotenv()

    return {
        "endpoint": os.environ["COSMOSDB_ENDPOINT"],
        "key": os.environ["COSMOSDB_KEY"],
        "database": os.environ["COSMOSDB_DATABASE"],
        "offer_throughput": os.environ["COSMOSDB_OFFER_THROUGHPUT"],
    }


def get_containers() -> dict[str, list[dict[str, str | bool]]]:
    """Get containers"""

    return {
        "containers": [
            {
                "container_name": "stocks_held",
                "partition_key": "/id",
                "candelete": True,
                "input_container": False,
                "output_container": True,
            },
            {
                "container_name": "totals",
                "partition_key": "/id",
                "candelete": True,
                "input_container": False,
                "output_container": True,
            },
            {
                "container_name": "input_transactions",
                "partition_key": "/id",
                "candelete": False,
                "input_container": True,
                "output_container": False,
            },
            {
                "container_name": "input_invested",
                "partition_key": "/id",
                "candelete": False,
                "input_container": True,
                "output_container": False,
            },
            {
                "container_name": "meta_data",
                "partition_key": "/id",
                "candelete": True,
                "input_container": False,
                "output_container": True,
            },
        ]
    }
