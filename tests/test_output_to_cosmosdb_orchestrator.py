"""Test the output_to_cosmosdb_orchestrator.py file."""
from unittest.mock import patch

import azure.durable_functions as df

from output_to_cosmosdb_orchestrator import orchestrator_function


def output_to_cosmosdb_side_effect(name: str, items: list) -> str:
    """Mock side effect for output_to_cosmosdb"""
    return '{"status": "Done"}'


@patch(
    "azure.durable_functions.DurableOrchestrationContext",
    spec=df.DurableOrchestrationContext,
)
def test_valid_request(mock_durable_context):
    """Test the main function."""
    mock_durable_context.call_activity.side_effect = output_to_cosmosdb_side_effect
    mock_durable_context.get_input.return_value = {
        "container1": ["item1", "item2", "item3", "item4", "item5", "item6", "item7"]
    }

    result = list(orchestrator_function(mock_durable_context))
    mock_durable_context.call_activity.assert_called_once_with(
        "output_to_cosmosdb",
        ["container1", ["item1", "item2", "item3", "item4", "item5", "item6", "item7"]],
    )

    assert result[0] == '{"status": "Done"}'


@patch(
    "azure.durable_functions.DurableOrchestrationContext",
    spec=df.DurableOrchestrationContext,
)
def test_valid_request_multiple_containers(mock_durable_context):
    """Test the main function."""
    mock_durable_context.call_activity.side_effect = output_to_cosmosdb_side_effect
    mock_durable_context.get_input.return_value = {
        "container1": ["item1", "item2", "item3", "item4", "item5", "item6", "item7"],
        "container2": ["item1", "item2", "item3", "item4", "item5", "item6", "item7"],
    }

    result = list(orchestrator_function(mock_durable_context))
    mock_durable_context.call_activity.assert_called_with(
        "output_to_cosmosdb",
        ["container2", ["item1", "item2", "item3", "item4", "item5", "item6", "item7"]],
    )
    assert mock_durable_context.call_activity.call_count == 2
    assert result[0] == '{"status": "Done"}'


@patch(
    "azure.durable_functions.DurableOrchestrationContext",
    spec=df.DurableOrchestrationContext,
)
def test_empty_request(mock_durable_context):
    """Test the main function."""
    mock_durable_context.call_activity.side_effect = output_to_cosmosdb_side_effect
    mock_durable_context.get_input.return_value = {}

    list(orchestrator_function(mock_durable_context))
    mock_durable_context.call_activity.assert_not_called()
