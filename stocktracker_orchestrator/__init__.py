"""main Orchestrator function"""
# pylint: disable=too-many-locals

import azure.functions as func
import azure.durable_functions as df


def orchestrator_function(context: df.DurableOrchestrationContext):
    """Orchestrator function"""
    # step 0: get the input
    days_to_update = context.get_input()[0]
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

    # step 1.1 - Get the input from the sql database
    transactions = yield context.call_activity("get_transactions", "Go")

    # Step 2.1 - Get data for stocks via the API
    provisioning_tasks = []
    id_ = 0
    child_id = f"{context.instance_id}:{id_}"
    provision_task = context.call_sub_orchestrator(
        "get_stock_data_orchestrator", transactions, child_id
    )
    provisioning_tasks.append(provision_task)
    stock_data = (yield context.task_all(provisioning_tasks))[0]

    # Step 2.2 - Get forex data via the API
    provisioning_tasks = []
    id_ += 1
    child_id = f"{context.instance_id}:{id_}"
    provision_task = context.call_sub_orchestrator(
        "get_forex_data_orchestrator", transactions, child_id
    )
    provisioning_tasks.append(provision_task)
    forex_data = (yield context.task_all(provisioning_tasks))[0]

    # Step 2.3 - Get stock meta data via the API
    stock_meta_data = yield context.call_activity("get_stock_meta_data", [transactions])

    # Step 2.4 - Get dividend data via the API
    provisioning_tasks = []
    id_ = 0
    id_ += 1
    child_id = f"{context.instance_id}:{id_}"
    provision_task = context.call_sub_orchestrator(
        "get_dividend_data_orchestrator", transactions, child_id
    )
    provisioning_tasks.append(provision_task)
    dividend_data = (yield context.task_all(provisioning_tasks))[0]

    # Step 3 - Rebuild the transactions object
    transactions = yield context.call_activity(
        "rebuild_transactions", [transactions, forex_data]
    )

    # step 4 - Compute transactions
    stock_held = yield context.call_activity(
        "compute_transactions", [transactions, days_to_update]
    )

    # step 5 - Get invested data
    invested = yield context.call_activity(
        "get_invested_data", [transactions, days_to_update]
    )

    # step 6 - add stock_data to stock_held
    data = yield context.call_activity(
        "add_data_to_stocks_held",
        [
            stock_held,
            stock_data,
            forex_data,
            stock_meta_data,
            dividend_data,
            transactions,
        ],
    )

    # step 7 - Calulate totals
    data = yield context.call_activity(
        "calculate_totals",
        [data, invested, transactions, days_to_update],
    )

    # step 8 recreate containers / remove items
    result = yield context.call_activity("delete_cosmosdb_items", days_to_update)

    # step 9.1 - output single_day_data to cosmosdb
    result = yield context.call_activity("output_singleday_to_cosmosdb", data)

    # step 9.2 - output everything else to cosmosdb
    for container_name, items in data.items():
        result = yield context.call_activity(
            "output_to_cosmosdb", [container_name, items]
        )

    return result


main = df.Orchestrator.create(orchestrator_function)
