"""Function to output data to CosmosDB"""
# pylint: disable=logging-fstring-interpolation
# pylint: disable=consider-using-from-import

import logging

import azure.functions as func
import azure.durable_functions as df
from shared_code import cosmosdb_module


def orchestrator_function(context: df.DurableOrchestrationContext):
    """Function to output data to CosmosDB"""
    logging.info("Outputting data to CosmosDB")

    # suppress logger output
    logger = logging.getLogger("azure")
    logger.setLevel(logging.CRITICAL)

    container_name = context.get_input()[0]
    items = context.get_input()[1]

    container = cosmosdb_module.cosmosdb_container(container_name)
    for item in items:
        container.upsert_item(item)

    return '{"status": "Done"}'


main = df.Orchestrator.create(orchestrator_function)
