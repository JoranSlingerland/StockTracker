"""CosmosDB Helper Functions"""


import asyncio
import logging
import random
from typing import Callable

from azure.cosmos import cosmos_client, errors

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


async def container_function_with_back_off(
    function: Callable,
    max_retries=10,
    delay=random.uniform(0.0, 0.2),
    max_delay=5,
):
    """Async fill with backoff"""
    retry_count = 0
    while True:
        try:
            await function()
            break
        except errors.CosmosResourceExistsError:
            logging.debug("Item already exists")
            break
        except errors.CosmosHttpResponseError as err:
            if err.status_code == 404:
                logging.debug("Item not found")
                break
        except Exception as err:
            if retry_count >= max_retries:
                logging.error("Max retries reached")
                raise err
            logging.debug(err)
            logging.debug(f"Retrying in {delay} seconds")
            await asyncio.sleep(delay)
            delay = min(delay * 2, max_delay) + (
                random.uniform(0, 1) * min(retry_count, 1)
            )
            retry_count += 1
