"""main Orchestrator function"""
# pylint: disable=unused-variable

import logging
import json

import azure.functions as func
import azure.durable_functions as df


def orchestrator_function(context: df.DurableOrchestrationContext):
    """Orchestrator function"""

    # step 1.1 - Get the input from the sql database
    transactions = yield context.call_activity("get_transactions", "Go")

    # step 1.2 - Get last uid from sql
    highest_uids = yield context.call_activity("get_highest_uid", "Go")

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

    # step 8 - add invested to data
    data.update(**invested)
    # step 9 - Output to sql
    provisioning_tasks = []
    id_ += 1
    child_id = f"{context.instance_id}:{id_}"
    provision_task = context.call_sub_orchestrator(
        "output_to_sql_orchestrator", data, child_id
    )
    provisioning_tasks.append(provision_task)
    result = (yield context.task_all(provisioning_tasks))[0]
    return [result]


main = df.Orchestrator.create(orchestrator_function)
