"""Test add_item_to_input.py"""
import json
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import azure.functions as func
import pytest
from azure.cosmos import ContainerProxy

from add_user_data import main

with open(Path(__file__).parent / "data" / "get_user_data.json", "r") as f:
    mock_get_user_data = json.load(f)


@pytest.mark.asyncio()
async def test_invalid_json_body():
    """Test with invalid json body"""
    req = func.HttpRequest(
        method="POST",
        body={"invalid": "json"},
        url="/api/add/add_user_data",
    )
    response = await main(req)
    assert response.status_code == 400
    assert response.get_body() == b'{"result": "Invalid json body"}'


@pytest.mark.asyncio()
async def test_invalid_schema():
    """Test invalid schema"""
    body = {"invalid": "json"}

    req = func.HttpRequest(
        method="POST",
        body=json.dumps(body).encode("utf-8"),
        url="/api/add/add_user_data",
    )

    response = await main(req)
    assert response.status_code == 400
    assert response.get_body() == b'{"result": "Schema validation failed"}'


@pytest.mark.asyncio()
@patch("shared_code.utils.get_user")
@patch("shared_code.cosmosdb_module.cosmosdb_container")
async def test_main(cosmosdb_container_mock, get_user_mock):
    """Test add_item_to_input"""
    body = {
        "dark_mode": "system",
        "clearbit_api_key": "123",
        "alpha_vantage_api_key": "123",
        "brandfetch_api_key": "123",
        "currency": "USD",
    }

    req = func.HttpRequest(
        method="POST",
        body=json.dumps(body).encode("utf-8"),
        url="/api/add/add_user_data",
    )

    cosmosdb_container_mock.return_value = MagicMock(spec=ContainerProxy)
    cosmosdb_container_mock.return_value.create_item = AsyncMock()
    get_user_mock.return_value = mock_get_user_data

    response = await main(req)

    assert response.status_code == 200
    assert response.mimetype == "application/json"
    assert response.get_body().decode() == '{"result": "done"}'
