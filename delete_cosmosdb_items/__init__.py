"""Function to delete CosmosDB items"""

import logging
from functools import partial

from shared_code import aio_helper, cosmosdb_module


async def main(payload: list[str, list]) -> str:
    """Function to output data to CosmosDB"""
    logging.info("Delete CosmosDB items function started")

    # suppress logger output
    logger = logging.getLogger("azure")
    logger.setLevel(logging.CRITICAL)

    # get config
    container_name: str = payload[0]
    items: list = payload[1]

    container_client = cosmosdb_module.cosmosdb_container(container_name)

    tasks = []

    for item in items:
        logging.debug(item)
        tasks.append(
            cosmosdb_module.container_function_with_back_off(
                partial(container_client.delete_item, item, partition_key=item["id"])
            )
        )
    await aio_helper.gather_with_concurrency(50, *tasks)

    return '{"status": "Done"}'
