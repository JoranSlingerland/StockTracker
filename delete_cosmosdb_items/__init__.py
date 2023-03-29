"""Function to delete CosmosDB items"""

import logging
from datetime import date, timedelta
from functools import partial

from shared_code import aio_helper, cosmosdb_module, get_config


async def main(payload: str) -> str:
    """Function to output data to CosmosDB"""
    logging.info("Delete CosmosDB items function started")

    # suppress logger output
    logger = logging.getLogger("azure")
    logger.setLevel(logging.CRITICAL)

    days_to_update = payload[0]
    userid = payload[1]

    containers = (get_config.get_containers())["containers"]

    if days_to_update == "all":
        query = "SELECT * FROM c WHERE c.userid = @userid"
        parameters = [{"name": "@userid", "value": userid}]
    else:
        today = date.today()
        end_date = today.strftime("%Y-%m-%d")
        start_date = (today - timedelta(days=days_to_update)).strftime("%Y-%m-%d")

        query = "SELECT * FROM c WHERE c.date >= @start_date and c.date <= @end_date and c.userid = @userid"
        parameters = [
            {"name": "@start_date", "value": start_date},
            {"name": "@end_date", "value": end_date},
            {"name": "@userid", "value": userid},
        ]

    tasks = []

    for container in containers:
        if container["output_container"] and container["container_name"] != "meta_data":
            container_client = cosmosdb_module.cosmosdb_container(
                container["container_name"]
            )
            items = container_client.query_items(
                query=query,
                parameters=parameters,
                enable_cross_partition_query=True,
            )

            for item in items:
                logging.debug(item)
                tasks.append(
                    cosmosdb_module.container_function_with_back_off(
                        partial(
                            container_client.delete_item, item, partition_key=item["id"]
                        )
                    )
                )
    await aio_helper.gather_with_concurrency(50, *tasks)

    return '{"status": "Done"}'
