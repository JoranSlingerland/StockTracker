"""Create sql tables"""
# pylint: disable=unused-argument
# pylint: disable=consider-using-from-import

import logging
import azure.functions as func
import azure.cosmos.cosmos_client as cosmos_client
import azure.cosmos.exceptions as exceptions
from azure.cosmos.partition_key import PartitionKey
from shared_code import get_config


def main(req: func.HttpRequest) -> func.HttpResponse:
    """Main function"""
    logging.info("Creating sql tables")

    # get config
    containers = (get_config.get_containers())["containers"]
    cosmosdb_config = get_config.get_cosmosdb()
    client = cosmos_client.CosmosClient(
        cosmosdb_config["endpoint"], cosmosdb_config["key"]
    )

    # create database
    database = client.create_database_if_not_exists(
        id=cosmosdb_config["database"],
        offer_throughput=cosmosdb_config["offer_throughput"],
    )

    # create container
    for container in containers:
        database.create_container_if_not_exists(
            id=container["container_name"],
            partition_key=PartitionKey(path=container["partition_key"]),
        )

    return func.HttpResponse(
        body='{"result": "done"}',
        mimetype="application/json",
        status_code=200,
    )
