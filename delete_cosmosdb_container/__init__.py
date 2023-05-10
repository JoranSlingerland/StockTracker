"""Delete cosmosdb container"""

import logging

import azure.functions as func
from azure.cosmos import exceptions

from shared_code import cosmosdb_module, get_config, utils


def main(req: func.HttpRequest) -> func.HttpResponse:
    """Main function"""
    logging.info("Creating sql tables")

    # get config
    containers_to_delete = req.form.get("containersToDelete")

    if containers_to_delete not in ["all", "output_only"]:
        logging.error("No valid containers_to_delete provided")
        return func.HttpResponse(
            body='{"result": "Please pass a valid name on the query string or in the request body"}',
            mimetype="application/json",
            status_code=400,
        )
    if not utils.is_admin(req):
        return func.HttpResponse(
            body='{"result": "Not authorized"}',
            mimetype="application/json",
            status_code=401,
        )

    errors, calls = delete_container(containers_to_delete)

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


def delete_container(containers_to_delete):
    """Delete container"""
    # get database
    containers = (get_config.get_containers())["containers"]
    database = cosmosdb_module.cosmosdb_database()
    errors = 0
    calls = 0

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

    return errors, calls
