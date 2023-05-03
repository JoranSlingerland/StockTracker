"""Orchestrator function for output_to_cosmosdb"""

import logging

import azure.durable_functions as df


def orchestrator_function(context: df.DurableOrchestrationContext):
    """Orchestrator function"""
    logging.info("Delete CosmosDB items orchestrator function started")
    days_to_update = context.get_input()[0]
    userid = context.get_input()[1]

    data = yield context.call_activity("items_to_delete", [days_to_update, userid])
    result = '{"status": "No items to delete"}'

    for container_name, items in data.items():
        items = [items[i : i + 5000] for i in range(0, len(items), 5000)]
        for batch in items:
            result = yield context.call_activity(
                "delete_cosmosdb_items", [container_name, batch]
            )

    return result


main = df.Orchestrator.create(orchestrator_function)
