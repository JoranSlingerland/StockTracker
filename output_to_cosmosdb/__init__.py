"""Function to output data to CosmosDB"""
# pylint: disable=broad-except

import logging
import asyncio
import random
from azure.cosmos.aio import CosmosClient
from shared_code import get_config, aio_helper


async def main(payload: str) -> str:
    """Function to output data to CosmosDB"""

    # suppress logger output
    logger = logging.getLogger("azure")
    logger.setLevel(logging.CRITICAL)

    # get config
    container_name = payload[0]
    items = payload[1]

    logging.info(f"Outputting to container {container_name}")

    # get cosmosdb config
    cosmosdb_config = get_config.get_cosmosdb()
    url = cosmosdb_config["endpoint"]
    key = cosmosdb_config["key"]
    comosdb = cosmosdb_config["database"]
    client = CosmosClient(url, credential=key)
    database = client.get_database_client(comosdb)

    tasks = []
    container = database.get_container_client(container_name)
    for item in items:
        # fill event loop list
        tasks.append(insert_item_with_backoff(container, item))
    # wait for all tasks to complete
    await aio_helper.gather_with_concurrency(50, *tasks)
    await client.close()
    return '{"status": "Done"}'


async def insert_item_with_backoff(container, item):
    """async fill with backoff"""
    max_retries = 10
    retry_count = 0
    delay = random.uniform(0.2, 0.25)
    max_delay = 60
    while retry_count < max_retries:
        try:
            await container.create_item(item)
            break
        except Exception as err:
            logging.debug(err)
            logging.info(f"Retrying in {delay} seconds")
            await asyncio.sleep(delay)
            delay = min(delay * 2, max_delay) + (
                random.uniform(0, 0.25) * min(retry_count, 1)
            )
            retry_count += 1
    if retry_count == max_retries:
        # throw terminal error
        raise Exception("Max retries exceeded")
