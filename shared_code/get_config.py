"""Get required environment variables"""

# Imports
import os

from dotenv import load_dotenv


# functions
def get_cosmosdb() -> dict[str, str]:
    """Get cosmosdb"""

    load_dotenv()

    return {
        "endpoint": os.environ["COSMOSDB_ENDPOINT"],
        "key": os.environ["COSMOSDB_KEY"],
        "database": os.environ["COSMOSDB_DATABASE"],
    }
