"""Function to delete CosmosDB items"""

import logging
from datetime import date, timedelta

from shared_code import cosmosdb_module, get_config


def main(payload: list[str | int, str]) -> str:
    """Function to output data to CosmosDB"""
    logging.info("Delete CosmosDB items function started")

    # suppress logger output
    logger = logging.getLogger("azure")
    logger.setLevel(logging.CRITICAL)

    # get config
    days_to_update: str | int = payload[0]
    userid: str = payload[1]

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

    data = {}

    for container in containers:
        if container["output_container"] and container["container_name"] != "meta_data":
            container_client = cosmosdb_module.cosmosdb_container(
                container["container_name"]
            )
            items = list(
                container_client.query_items(
                    query=query,
                    parameters=parameters,
                    enable_cross_partition_query=True,
                )
            )
            data[container["container_name"]] = items

    return data
