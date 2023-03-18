"""Test get_config.py"""

import asyncio
import datetime
import os
from unittest import mock

import pytest
from azure.cosmos import exceptions

from shared_code import (
    aio_helper,
    cosmosdb_module,
    date_time_helper,
    get_config,
    schemas,
    utils,
)


@pytest.mark.asyncio()
async def test_gather_with_concurrency():
    """Test gather with concurrency"""

    async def my_coroutine(test_input):
        await asyncio.sleep(0.1)
        return test_input * 2

    tasks = [my_coroutine(i) for i in range(10)]
    result = await aio_helper.gather_with_concurrency(5, *tasks)
    assert result == [0, 2, 4, 6, 8, 10, 12, 14, 16, 18]


class TestCosmosdbModule:
    """Test cosmosdb module"""

    @mock.patch("shared_code.get_config.get_cosmosdb")
    @mock.patch("azure.cosmos.cosmos_client.CosmosClient")
    def test_cosmosdb_client(self, mock_cosmos_client, mock_get_cosmosdb):
        """Test cosmosdb client with mocked config and client"""
        mock_config = mock.MagicMock()
        mock_config.__getitem__.side_effect = lambda key: {
            "endpoint": "mock_endpoint",
            "key": "mock_key",
        }[key]
        mock_get_cosmosdb.return_value = mock_config

        mock_client = mock.MagicMock()
        mock_cosmos_client.return_value = mock_client

        client = cosmosdb_module.cosmosdb_client()

        mock_cosmos_client.assert_called_once_with("mock_endpoint", "mock_key")
        assert client == mock_client

    @mock.patch("shared_code.cosmosdb_module.cosmosdb_client")
    @mock.patch("shared_code.cosmosdb_module.get_config.get_cosmosdb")
    def test_cosmosdb_database(self, mock_get_cosmosdb, mock_cosmosdb_client):
        """Test cosmosdb database"""
        mock_get_cosmosdb.return_value = {"database": "mock database"}
        mock_client = mock_cosmosdb_client.return_value
        mock_database_client = mock_client.get_database_client.return_value
        mock_database_client.return_value = "mock database client"

        result = cosmosdb_module.cosmosdb_database()

        # Assert that the result is as expected
        assert result == mock_database_client

    @mock.patch("shared_code.cosmosdb_module.cosmosdb_database")
    def test_cosmosdb_container(self, mock_cosmosdb_database):
        """Test cosmosdb container"""
        # mock_get_config = mock_get_config.return_value
        mock_database = mock_cosmosdb_database.return_value
        mock_container_client = mock_database.get_container_client.return_value
        result = cosmosdb_module.cosmosdb_container("mock container name")
        assert result == mock_container_client

    @pytest.mark.asyncio()
    async def test_container_function_with_back_off(self):
        """Test container function with back off"""
        function = mock.AsyncMock()
        max_retries = 2
        delay = 0.1
        max_delay = 1

        await cosmosdb_module.container_function_with_back_off(
            function, max_retries, delay, max_delay
        )
        function.assert_called_once()

        function.reset_mock()
        function.side_effect = exceptions.CosmosResourceExistsError()
        await cosmosdb_module.container_function_with_back_off(
            function, max_retries, delay, max_delay
        )
        function.assert_called_once()

        function.reset_mock()
        function.side_effect = exceptions.CosmosHttpResponseError(status_code=404)
        await cosmosdb_module.container_function_with_back_off(
            function, max_retries, delay, max_delay
        )
        function.assert_called_once()

        function.reset_mock()
        function.side_effect = Exception("test exception")

        # should raise an exception exception("test exception")
        with pytest.raises(Exception, match="test exception"):
            await cosmosdb_module.container_function_with_back_off(
                function, max_retries, delay, max_delay
            )
        assert function.call_count == max_retries + 1


class TestGetConfig:
    """Test get_config.py"""

    @mock.patch.dict(os.environ, {"API_KEY": "test_api_key"})
    def test_get_api_key(self):
        """Test get api key"""
        api_key = get_config.get_api_key()
        assert api_key == "test_api_key"

    @mock.patch.dict(os.environ, {"CLEARBIT_API_KEY": "test_clearbit_api_key"})
    def test_get_clearbit_api_key(self):
        """Test get clearbit api key"""
        clearbit_api_key = get_config.get_clearbit_api_key()
        assert clearbit_api_key == "test_clearbit_api_key"

    @mock.patch.dict(
        os.environ,
        {
            "COSMOSDB_ENDPOINT": "test_endpoint",
            "COSMOSDB_KEY": "test_key",
            "COSMOSDB_DATABASE": "test_database",
            "COSMOSDB_OFFER_THROUGHPUT": "test_offer_throughput",
        },
    )
    def test_get_cosmosdb(self):
        """Test get cosmosdb"""
        cosmosdb = get_config.get_cosmosdb()
        assert cosmosdb["endpoint"] == "test_endpoint"
        assert cosmosdb["key"] == "test_key"
        assert cosmosdb["database"] == "test_database"
        assert cosmosdb["offer_throughput"] == "test_offer_throughput"

    def test_get_containers(self):
        """Test get containers"""
        containers = get_config.get_containers()
        assert isinstance(containers, dict)
        assert "containers" in containers
        assert isinstance(containers["containers"], list)
        assert len(containers["containers"]) > 0


class TestDateTimeHelper:
    """Test date time helper"""

    def test_get_quarter_first_and_last_date(self):
        """Test get quarter first and last date"""
        quarter = "Q1 2021"
        start_date, end_date = date_time_helper.get_quarter_first_and_last_date(quarter)
        assert start_date == datetime.date(2021, 1, 1)
        assert end_date == datetime.date(2021, 3, 31)

        quarter = "Q2 2021"
        start_date, end_date = date_time_helper.get_quarter_first_and_last_date(quarter)
        assert start_date == datetime.date(2021, 4, 1)
        assert end_date == datetime.date(2021, 6, 30)

        quarter = "Q3 2021"
        start_date, end_date = date_time_helper.get_quarter_first_and_last_date(quarter)
        assert start_date == datetime.date(2021, 7, 1)
        assert end_date == datetime.date(2021, 9, 30)

        quarter = "Q4 2021"
        start_date, end_date = date_time_helper.get_quarter_first_and_last_date(quarter)
        assert start_date == datetime.date(2021, 10, 1)
        assert end_date == datetime.date(2021, 12, 31)

        quarter = "Q5 2021"
        start_date, end_date = date_time_helper.get_quarter_first_and_last_date(quarter)
        assert None is start_date
        assert None is end_date

    def test_datatogetswitch(self):
        """Test data to get switch"""

        today = datetime.date.today()

        data_to_get = "test"
        start_data, end_date = date_time_helper.datatogetswitch(data_to_get)
        assert None is start_data
        assert None is end_date

        data_to_get = "year"
        start_data, end_date = date_time_helper.datatogetswitch(data_to_get)
        assert start_data == (today - datetime.timedelta(days=365)).strftime("%Y-%m-%d")
        assert end_date == today.strftime("%Y-%m-%d")

        data_to_get = "month"
        start_data, end_date = date_time_helper.datatogetswitch(data_to_get)
        assert start_data == (today - datetime.timedelta(days=30)).strftime("%Y-%m-%d")
        assert end_date == today.strftime("%Y-%m-%d")

        data_to_get = "week"
        start_data, end_date = date_time_helper.datatogetswitch(data_to_get)
        assert start_data == (today - datetime.timedelta(days=7)).strftime("%Y-%m-%d")
        assert end_date == today.strftime("%Y-%m-%d")

        data_to_get = "ytd"
        start_data, end_date = date_time_helper.datatogetswitch(data_to_get)
        assert start_data == datetime.date(today.year, 1, 1).strftime("%Y-%m-%d")
        assert end_date == today.strftime("%Y-%m-%d")

    def test_month_to_quarter(self):
        """Test month to quarter"""
        month = "January"
        quarter = date_time_helper.month_to_quarter(month)
        assert quarter == "Q1"

        month = "February"
        quarter = date_time_helper.month_to_quarter(month)
        assert quarter == "Q1"

        month = "March"
        quarter = date_time_helper.month_to_quarter(month)
        assert quarter == "Q1"

        month = "April"
        quarter = date_time_helper.month_to_quarter(month)
        assert quarter == "Q2"

        month = "May"
        quarter = date_time_helper.month_to_quarter(month)
        assert quarter == "Q2"

        month = "June"
        quarter = date_time_helper.month_to_quarter(month)
        assert quarter == "Q2"

        month = "July"
        quarter = date_time_helper.month_to_quarter(month)
        assert quarter == "Q3"

        month = "August"
        quarter = date_time_helper.month_to_quarter(month)
        assert quarter == "Q3"

        month = "September"
        quarter = date_time_helper.month_to_quarter(month)
        assert quarter == "Q3"

        month = "October"
        quarter = date_time_helper.month_to_quarter(month)
        assert quarter == "Q4"

        month = "November"
        quarter = date_time_helper.month_to_quarter(month)
        assert quarter == "Q4"

        month = "December"
        quarter = date_time_helper.month_to_quarter(month)
        assert quarter == "Q4"

        month = "Not a month"
        quarter = date_time_helper.month_to_quarter(month)
        assert quarter is None

    def test_get_quarter(self):
        """Test get quarter"""
        start_date = datetime.date(2021, 1, 1)
        end_date = datetime.date(2021, 3, 31)
        quarters = date_time_helper.get_quarters(start_date, end_date)
        assert quarters == ["Q1 2021"]

        start_date = datetime.date(2021, 1, 1)
        end_date = datetime.date(2022, 3, 31)
        quarters = date_time_helper.get_quarters(start_date, end_date)
        assert quarters == ["Q1 2021", "Q2 2021", "Q3 2021", "Q4 2021", "Q1 2022"]

        start_date = datetime.date(2021, 1, 1)
        end_date = datetime.date(2020, 12, 31)
        quarters = date_time_helper.get_quarters(start_date, end_date)
        assert not quarters

    def test_get_months(self):
        """Test get months"""
        start_date = datetime.date(2021, 1, 1)
        end_date = datetime.date(2021, 3, 31)
        months = date_time_helper.get_months(start_date, end_date)
        assert months == [
            datetime.date(2021, 1, 31),
            datetime.date(2021, 2, 28),
            datetime.date(2021, 3, 31),
        ]

        start_date = datetime.date(2021, 1, 1)
        end_date = datetime.date(2020, 12, 31)
        months = date_time_helper.get_months(start_date, end_date)
        assert months == []

    def test_get_weeks(self):
        """Test get weeks"""


class TestSchemas:
    """Test schemas"""

    def test_stock_input(self):
        """Test stock input"""
        schema = schemas.stock_input()
        assert isinstance(schema, dict)

    def test_transaction_input(self):
        """Test stock output"""
        schema = schemas.transaction_input()
        assert isinstance(schema, dict)


class TestUtils:
    """Test utils"""

    def test_get_unique_items(self):
        """Test get unique items"""
        items = [
            {"key_to_filter": "a"},
            {"key_to_filter": "b"},
            {"key_to_filter": "c"},
            {"key_to_filter": "a"},
            {"key_to_filter": "b"},
            {"key_to_filter": "c"},
        ]
        key_to_filter = "key_to_filter"
        unique_items = utils.get_unique_items(items, key_to_filter)
        assert unique_items == ["a", "b", "c"]

        items = []
        unique_items = utils.get_unique_items(items, key_to_filter)
        assert not unique_items

    def test_get_weighted_average(self):
        """Test get weighted average"""
        data = [1, 4]
        weight = [1, 2]
        weighted_average = utils.get_weighted_average(data, weight)
        assert weighted_average == 3.0

    def test_add_meta_data_to_stock_data(self):
        """Test add meta data to stock data"""
        stock_data = [{"symbol": "ABC"}, {"symbol": "XYZ"}]
        meta_data = [
            {"symbol": "ABC", "name": "ABC Inc."},
            {"symbol": "XYZ", "name": "XYZ Inc."},
        ]

        container = mock.Mock()
        container.read_all_items.return_value = meta_data
        result = utils.add_meta_data_to_stock_data(stock_data, container)
        assert result == [
            {"symbol": "ABC", "meta": {"symbol": "ABC", "name": "ABC Inc."}},
            {"symbol": "XYZ", "meta": {"symbol": "XYZ", "name": "XYZ Inc."}},
        ]

        # Test when no meta data is found
        container.read_all_items.return_value = []
        result = utils.add_meta_data_to_stock_data(stock_data, container)
        assert result == [
            {"symbol": "ABC", "meta": {}},
            {"symbol": "XYZ", "meta": {}},
        ]
