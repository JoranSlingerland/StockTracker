"""Get required environment variables"""

# Imports
import os

from dotenv import load_dotenv


# functions
def get_api_key() -> str:
    """Get api key"""

    load_dotenv()

    api_key = os.environ["API_KEY"]

    return api_key


def get_clearbit_api_key() -> str:
    """Get clearbit api key"""

    load_dotenv()

    clearbit_api_key = os.environ["CLEARBIT_API_KEY"]

    return clearbit_api_key


def get_cosmosdb() -> dict:
    """Get cosmosdb"""

    load_dotenv()

    cosmosdb = {
        "endpoint": os.environ["COSMOSDB_ENDPOINT"],
        "key": os.environ["COSMOSDB_KEY"],
        "database": os.environ["COSMOSDB_DATABASE"],
        "offer_throughput": os.environ["COSMOSDB_OFFER_THROUGHPUT"],
    }
    return cosmosdb


def get_containers() -> dict:
    """Get containers"""

    load_dotenv()

    containers = {
        "containers": [
            {
                "container_name": "stocks_held",
                "partition_key": "/id",
                "candelete": True,
                "cantruncate": True,
                "input_container": False,
                "output_container": True,
            },
            {
                "container_name": "totals",
                "partition_key": "/id",
                "candelete": True,
                "cantruncate": True,
                "input_container": False,
                "output_container": True,
            },
            {
                "container_name": "single_day",
                "partition_key": "/id",
                "candelete": True,
                "cantruncate": True,
                "input_container": False,
                "output_container": True,
            },
            {
                "container_name": "single_day_totals",
                "partition_key": "/id",
                "candelete": True,
                "cantruncate": True,
                "input_container": False,
                "output_container": True,
            },
            {
                "container_name": "input_transactions",
                "partition_key": "/id",
                "candelete": False,
                "cantruncate": False,
                "input_container": True,
                "output_container": False,
            },
            {
                "container_name": "input_invested",
                "partition_key": "/id",
                "candelete": False,
                "cantruncate": False,
                "input_container": True,
                "output_container": False,
            },
            {
                "container_name": "meta_data",
                "partition_key": "/id",
                "candelete": True,
                "cantruncate": True,
                "input_container": False,
                "output_container": True,
            },
        ]
    }

    return containers
