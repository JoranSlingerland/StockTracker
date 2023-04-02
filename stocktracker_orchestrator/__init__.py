"""main Orchestrator function"""


import logging

import azure.durable_functions as df


def orchestrator_function(context: df.DurableOrchestrationContext):
    """Orchestrator function"""
    # step 0: get the input
    logging.info("Step 0: Getting input")
    days_to_update = context.get_input()[0]
    userid = context.get_input()[1]
    if days_to_update != "all":
        if isinstance(days_to_update, str):
            try:
                days_to_update = int(days_to_update)
            except ValueError:
                return "days_to_update must be an integer or the value of 'all'"
        if days_to_update <= 0:
            return (
                "days_to_update must have a value greater than 0 or the value of 'all'"
            )

        days_to_update = days_to_update - 1

    # step 1 - Get the input from the sql database
    logging.info("Step 1: Getting transactions")
    transactions = yield context.call_activity("get_transactions", [userid])

    # Step 2 - Get api data
    logging.info("Step 2.1: Getting api data")
    provisioning_tasks = []
    id_ = 0
    child_id = f"{context.instance_id}:{id_}"
    provision_task = context.call_sub_orchestrator(
        "get_api_data", transactions, child_id
    )
    provisioning_tasks.append(provision_task)
    api_data = (yield context.task_all(provisioning_tasks))[0]

    # step 3 recreate containers / remove items
    logging.info("Step 3: Delete cosmosdb items")
    result = yield context.call_activity(
        "delete_cosmosdb_items", [days_to_update, userid]
    )

    # step 4 - output meta data to cosmosdb
    logging.info("Step 4: Output meta data to cosmosdb")
    result = yield context.call_activity(
        "output_to_cosmosdb", ["meta_data", api_data["stock_meta_data"]]
    )

    # Step 5 - Rebuild the transactions object
    logging.info("Step 5: Get transactions by day")
    day_by_day = yield context.call_activity(
        "get_transactions_by_day", [transactions, api_data["forex_data"]]
    )

    # step 6 - add stock_data to stock_held
    logging.info("Step 6: Add data to stocks held")
    (
        day_by_day["stock_held"],
        api_data,
        data,  # Only used for return value everything else gets a None value to free up memory
    ) = yield context.call_activity(
        "add_data_to_stocks_held",
        [
            day_by_day["stock_held"],
            api_data["stock_data"],
            api_data["forex_data"],
            transactions,
            days_to_update,
            userid,
        ],
    )

    # step 7 - Calulate totals
    logging.info("Step 7: Calculate totals")
    (
        day_by_day["invested"],
        transactions,
        data,  # Only used for return value everything else gets a None value to free up memory
    ) = yield context.call_activity(
        "calculate_totals",
        [data, day_by_day["invested"], transactions, userid],
    )

    # step 8 - output to cosmosdb
    logging.info("Step 8: Output to cosmosdb")
    provisioning_tasks = []
    id_ = 1
    child_id = f"{context.instance_id}:{id_}"
    provision_task = context.call_sub_orchestrator(
        "output_to_cosmosdb_orchestrator", data, child_id
    )
    provisioning_tasks.append(provision_task)
    result = (yield context.task_all(provisioning_tasks))[0]

    logging.info("Step 9: Returning result")
    return result


main = df.Orchestrator.create(orchestrator_function)
