"""Create sql tables"""

import logging

import azure.functions as func
from azure.cosmos import exceptions

from shared_code import cosmosdb_module, get_config


def main(req: func.HttpRequest) -> func.HttpResponse:
    """Main function"""
    logging.info("Creating sql tables")
    errors = 0
    calls = 0

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
                calls += 1
                database.delete_container(container["container_name"])
            except exceptions.CosmosResourceNotFoundError:
                logging.info(f"Container {container['container_name']} does not exist")
                errors += 1
    elif containers_to_delete == "output_only":
        for container in containers:
            if container["candelete"]:
                try:
                    calls += 1
                    database.delete_container(container["container_name"])
                except exceptions.CosmosResourceNotFoundError:
                    logging.info(
                        f"Container {container['container_name']} does not exist"
                    )
                    errors += 1
    else:
        logging.error("No valid containers_to_delete provided")
        return func.HttpResponse(
            body='{"result": "Please pass a valid name on the query string or in the request body"}',
            mimetype="application/json",
            status_code=400,
        )

    if errors > 0:
        return func.HttpResponse(
            body=f'{{"result": "deleted {calls-errors} out of {calls} containers"}}',
            mimetype="application/json",
            status_code=500,
        )

    return func.HttpResponse(
        body='{"result": "done"}',
        mimetype="application/json",
        status_code=200,
    )
