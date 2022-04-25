"""CosmosDB Helper Functions"""
# pylint: disable=unused-argument
# pylint: disable=consider-using-from-import

import azure.cosmos.cosmos_client as cosmos_client
from shared_code import get_config


def cosmosdb_client() -> cosmos_client.CosmosClient:
    """CosmosDB client"""
    cosmosdb_config = get_config.get_cosmosdb()
    client = cosmos_client.CosmosClient(
        cosmosdb_config["endpoint"], cosmosdb_config["key"]
    )
    return client


def cosmosdb_database():
    """CosmosDB database"""
    cosmosdb_config = get_config.get_cosmosdb()
    client = cosmosdb_client()
    database = client.get_database_client(cosmosdb_config["database"])
    return database


def cosmosdb_container(container_name: str):
    """CosmosDB container"""
    database = cosmosdb_database()
    container = database.get_container_client(container_name)
    return container
