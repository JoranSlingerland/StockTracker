"""Test the delete_cosmosdb_items function."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from azure.cosmos import ContainerProxy

from delete_cosmosdb_items import main

mock_items = [
    {
        "id": "1",
    }
]


@pytest.mark.asyncio()
@patch("shared_code.cosmosdb_module.cosmosdb_container")
async def test_all(cosmosdb_container_mock):
    """Test the main function."""
    payload = ["test", mock_items]

    cosmosdb_container_mock.return_value = MagicMock(spec=ContainerProxy)
    cosmosdb_container_mock.return_value.delete_item = AsyncMock()

    response = await main(payload)

    assert response == '{"status": "Done"}'
    assert cosmosdb_container_mock.return_value.delete_item.await_count == 1
    cosmosdb_container_mock.assert_called_with("test")
    cosmosdb_container_mock.return_value.delete_item.assert_called_with(
        mock_items[0], partition_key=mock_items[0]["id"]
    )
