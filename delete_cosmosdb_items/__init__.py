"""Function to output data to CosmosDB"""
# pylint: disable=logging-fstring-interpolation
# pylint: disable=consider-using-from-import

import logging
from datetime import date, timedelta
import azure.cosmos.exceptions as exceptions
from azure.cosmos.partition_key import PartitionKey
from shared_code import get_config, cosmosdb_module


def main(payload: str) -> str:
    """Function to output data to CosmosDB"""
    logging.info("Outputting data to CosmosDB")

    days_to_update = payload

    containers = (get_config.get_containers())["containers"]

    if days_to_update == "all":
        recreate_containers(containers)
    else:
        drop_selected_dates(containers, days_to_update)

    return '{"status": "Done"}'


def recreate_containers(containers):
    """Function to recreate containers"""
    logging.info("Recreating containers")

    database = cosmosdb_module.cosmosdb_database()
    for container in containers:
        if container["output_container"]:
            try:
                database.delete_container(container["container_name"])
            except exceptions.CosmosResourceNotFoundError:
                logging.info(f"Container {container['container_name']} does not exist")

    for container in containers:
        if container["output_container"]:
            database.create_container_if_not_exists(
                id=container["container_name"],
                partition_key=PartitionKey(path=container["partition_key"]),
            )


def drop_selected_dates(containers, days_to_update):
    """Function to drop selected dates"""
    logging.info("Dropping selected dates")
    today = date.today()
    end_date = today.strftime("%Y-%m-%d")
    start_date = (today - timedelta(days=days_to_update)).strftime("%Y-%m-%d")
    for container in containers:
        if (
            container["output_container"]
            and container["container_name"] != "single_day"
        ):
            container_client = cosmosdb_module.cosmosdb_container(
                container["container_name"]
            )
            for item in container_client.query_items(
                query=f"SELECT * FROM c WHERE c.date >= '{start_date}' and c.date <= '{end_date}'",
                enable_cross_partition_query=True,
            ):
                logging.info(item)
                container_client.delete_item(item, partition_key=item["id"])

    database = cosmosdb_module.cosmosdb_database()
    single_day_container_setup = [
        d for d in containers if d["container_name"] == "single_day"
    ]
    try:
        database.delete_container(single_day_container_setup[0]["container_name"])
    except exceptions.CosmosResourceNotFoundError:
        logging.info("Container single_day does not exist")
    database.create_container_if_not_exists(
        id=single_day_container_setup[0]["container_name"],
        partition_key=PartitionKey(path=single_day_container_setup[0]["partition_key"]),
    )


def create_items(data):
    """Function to create items"""
    logging.info("Creating items")
    stocks_held = data["stocks_held"]
    totals = data["totals"]
    invested = data["invested"]

    container = cosmosdb_module.cosmosdb_container("stocks_held")
    for item in stocks_held:
        container.upsert_item(item)

    container = cosmosdb_module.cosmosdb_container("totals")
    for item in totals:
        container.upsert_item(item)

    container = cosmosdb_module.cosmosdb_container("invested")
    for item in invested:
        container.upsert_item(item)

    today = date.today().strftime("%Y-%m-%d")
    single_day_stocks = [d for d in stocks_held if d["date"] == today]
    container = cosmosdb_module.cosmosdb_container("single_day")
    for item in single_day_stocks:
        container.upsert_item(item)
