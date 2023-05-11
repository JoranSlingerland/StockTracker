"""Orchestrator function for output_to_cosmosdb"""

import azure.durable_functions as df


def orchestrator_function(context: df.DurableOrchestrationContext):
    """Orchestrator function"""
    data = context.get_input()[0]
    days_to_update: str | int = context.get_input()[1]
    userid: str = context.get_input()[2]

    result = {"status": "No data to process"}

    # Delete old data
    items_to_delete = yield context.call_activity(
        "get_cosmosdb_items", [days_to_update, userid, ["stocks_held", "totals"]]
    )

    for container_name, items in items_to_delete.items():
        items = [items[i : i + 5000] for i in range(0, len(items), 5000)]
        for batch in items:
            result = yield context.call_activity(
                "delete_cosmosdb_items", [container_name, batch]
            )

    # Output new data
    for container_name, items in data.items():
        items = [items[i : i + 5000] for i in range(0, len(items), 5000)]
        for batch in items:
            result = yield context.call_activity(
                "output_to_cosmosdb", [container_name, batch]
            )

    return result


main = df.Orchestrator.create(orchestrator_function)
