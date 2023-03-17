"""Create sql tables"""

import logging

import azure.functions as func
from azure.cosmos import exceptions

from shared_code import cosmosdb_module, get_config


def main(req: func.HttpRequest) -> func.HttpResponse:
    """Main function"""
    logging.info("Creating sql tables")

    # get config
    containers_to_delete = req.form.get("containersToDelete")
    containers = (get_config.get_containers())["containers"]

    if not containers_to_delete:
        logging.error("No containers_to_delete provided")
        return func.HttpResponse(
            body='{"result": "Please pass a name on the query string or in the request body"}',
            mimetype="application/json",
            status_code=400,
        )

    # get database
    database = cosmosdb_module.cosmosdb_database()

    # delete containers
    if containers_to_delete == "all":
        for container in containers:
            try:
                database.delete_container(container["container_name"])
            except exceptions.CosmosResourceNotFoundError:
                logging.info(f"Container {container['container_name']} does not exist")
    elif containers_to_delete == "output_only":
        for container in containers:
            if container["candelete"]:
                try:
                    database.delete_container(container["container_name"])
                except exceptions.CosmosResourceNotFoundError:
                    logging.info(
                        f"Container {container['container_name']} does not exist"
                    )
    else:
        logging.error("No valid containers_to_delete provided")
        return func.HttpResponse(
            body='{"result": "Please pass a valid name on the query string or in the request body"}',
            mimetype="application/json",
            status_code=400,
        )

    return func.HttpResponse(
        body='{"result": "done"}',
        mimetype="application/json",
        status_code=200,
    )
