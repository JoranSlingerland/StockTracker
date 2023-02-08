"""Function to output data to CosmosDB"""

import logging
from azure.cosmos.aio import CosmosClient
from shared_code import get_config, aio_helper

# global variable


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
        tasks.append(insert_item(container, item))
    # wait for all tasks to complete
    await aio_helper.gather_with_concurrency(5, *tasks)
    await client.close()
    return '{"status": "Done"}'


async def insert_item(container, item):
    """async fill"""

    await container.create_item(item)
