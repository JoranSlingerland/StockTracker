"""Function to output data to CosmosDB"""


import logging
from functools import partial

from shared_code import aio_helper, cosmosdb_module


async def main(payload: str) -> str:
    """Function to output data to CosmosDB"""

    # suppress logger output
    logger = logging.getLogger("azure")
    logger.setLevel(logging.CRITICAL)

    # get config
    container_name = payload[0]
    items = payload[1]

    logging.info(f"Outputting to container {container_name}")

    tasks = []
    container = cosmosdb_module.cosmosdb_container(container_name)

    for item in items:
        # fill event loop list
        tasks.append(
            cosmosdb_module.container_function_with_back_off(
                partial(container.create_item, item)
            )
        )

    await aio_helper.gather_with_concurrency(50, *tasks)

    return '{"status": "Done"}'
