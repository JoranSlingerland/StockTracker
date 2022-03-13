"""main Orchestrator function"""

import logging
import json

import azure.functions as func
import azure.durable_functions as df


def orchestrator_function(context: df.DurableOrchestrationContext):
    """Orchestrator function"""

    # step 1 - Get the input from the sql database
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

    # Step 3 - Rebuild the transactions object
    transactions = yield context.call_activity(
        "rebuild_transactions", [transactions, forex_data]
    )

    # step 4 - Compute transactions
    stock_held = yield context.call_activity("compute_transactions", transactions)

    # step 5 - Get invested data
    invested = yield context.call_activity("get_invested_data", transactions)

    # step 6 - add stock_data to stock_held
    data = yield context.call_activity(
        "add_stock_data_to_stocks_held", [stock_held, stock_data, forex_data]
    )

    # step 7 - Calulate totals
    data = yield context.call_activity("calculate_totals", data)

    # step 8 add invested to data
    invested = json.loads(invested)
    data = json.loads(data)
    data.update(**invested)
    data = json.dumps(data)

    # Step 7 - Run main function
    result = yield context.call_activity("stocktracker", data)
    return [result]


main = df.Orchestrator.create(orchestrator_function)
