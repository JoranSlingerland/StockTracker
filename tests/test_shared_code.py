"""Test get_config.py"""
# pylint: disable=import-error

import unittest
from unittest import mock
import asyncio
import datetime
import os
from azure.cosmos import errors

from shared_code import (
    aio_helper,
    cosmosdb_module,
    date_time_helper,
    get_config,
    schemas,
    utils,
)


class TestAioHelper(unittest.TestCase):
    """Test aio_helper.py"""

    async def test_gather_with_concurrency(self):
        """Test gather with concurrency"""

        async def my_coroutine(test_input):
            await asyncio.sleep(0.1)
            return test_input * 2

        tasks = [my_coroutine(i) for i in range(10)]
        result = await aio_helper.gather_with_concurrency(5, *tasks)
        self.assertEqual(result, [0, 2, 4, 6, 8, 10, 12, 14, 16, 18])


class TestCosmosdbModule(unittest.TestCase):
    """Test cosmosdb module"""

    @mock.patch.dict(
        get_config.get_cosmosdb(),
        {
            "COSMOSDB_ENDPOINT": "test_endpoint",
            "COSMOSDB_KEY": "test_key",
            "COSMOSDB_DATABASE": "test_database",
            "COSMOSDB_OFFER_THROUGHPUT": "test_offer_throughput",
        },
    )
    @mock.patch("shared_code.cosmosdb_module.cosmos_client.CosmosClient")
    def test_cosmosdb_client(self, mock_cosmos_client):
        """Test cosmosdb client"""
        mock_cosmos_client.return_value = "mock client"
        result = cosmosdb_module.cosmosdb_client()
        self.assertEqual(result, "mock client")

    @mock.patch.dict(
        get_config.get_cosmosdb(),
        {
            "COSMOSDB_ENDPOINT": "test_endpoint",
            "COSMOSDB_KEY": "test_key",
            "COSMOSDB_DATABASE": "test_database",
            "COSMOSDB_OFFER_THROUGHPUT": "test_offer_throughput",
        },
    )
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
        self.assertEqual(result, mock_database_client)

    @mock.patch.dict(
        get_config.get_cosmosdb(),
        {
            "COSMOSDB_ENDPOINT": "test_endpoint",
            "COSMOSDB_KEY": "test_key",
            "COSMOSDB_DATABASE": "test_database",
            "COSMOSDB_OFFER_THROUGHPUT": "test_offer_throughput",
        },
    )
    @mock.patch("shared_code.cosmosdb_module.cosmosdb_database")
    def test_cosmosdb_container(self, mock_cosmosdb_database):
        """Test cosmosdb container"""
        mock_database = mock_cosmosdb_database.return_value
        mock_container_client = mock_database.get_container_client.return_value
        result = cosmosdb_module.cosmosdb_container("mock container name")

        self.assertEqual(result, mock_container_client)

    async def test_container_function_with_back_off(self):
        """Test container function with back off"""
        function = mock.MagicMock()
        await cosmosdb_module.container_function_with_back_off(function)
        function.assert_called_once()

        function.reset_mock()
        function.side_effect = Exception(errors.CosmosResourceExistsError)
        try:
            await cosmosdb_module.container_function_with_back_off(function)
        except Exception as err:
            self.assertIsInstance(err, errors.CosmosResourceExistsError)
        function.assert_called_once()

        function.reset_mock()
        function.side_effect = Exception(errors.CosmosHttpResponseError)
        try:
            await cosmosdb_module.container_function_with_back_off(function)
        except Exception as err:
            self.assertIsInstance(err, errors.CosmosHttpResponseError)
        function.assert_called_once()

        function.reset_mock()
        function.side_effect = Exception(Exception)
        try:
            await cosmosdb_module.container_function_with_back_off(function)
        except Exception as err:
            self.assertIsInstance(err, Exception)
            self.assertEqual(function.call_count, 10)


class TestGetConfig(unittest.TestCase):
    """Test get_config.py"""

    @mock.patch.dict(os.environ, {"API_KEY": "test_api_key"})
    def test_get_api_key(self):
        """Test get api key"""

        api_key = get_config.get_api_key()
        self.assertEqual(api_key, "test_api_key")

    @mock.patch.dict(os.environ, {"CLEARBIT_API_KEY": "test_clearbit_api_key"})
    def test_get_clearbit_api_key(self):
        """Test get clearbit api key"""

        clearbit_api_key = get_config.get_clearbit_api_key()
        self.assertEqual(clearbit_api_key, "test_clearbit_api_key")

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
        self.assertEqual(cosmosdb["endpoint"], "test_endpoint")
        self.assertEqual(cosmosdb["key"], "test_key")
        self.assertEqual(cosmosdb["database"], "test_database")
        self.assertEqual(cosmosdb["offer_throughput"], "test_offer_throughput")


class TestDateTimeHelper(unittest.TestCase):
    """Test date time helper"""

    def test_get_quarter_first_and_last_date(self):
        """Test get quarter first and last date"""
        quarter = "Q1 2021"
        start_date, end_date = date_time_helper.get_quarter_first_and_last_date(quarter)
        self.assertEqual(start_date, datetime.date(2021, 1, 1))
        self.assertEqual(end_date, datetime.date(2021, 3, 31))

        quarter = "Q2 2021"
        start_date, end_date = date_time_helper.get_quarter_first_and_last_date(quarter)
        self.assertEqual(start_date, datetime.date(2021, 4, 1))
        self.assertEqual(end_date, datetime.date(2021, 6, 30))

        quarter = "Q3 2021"
        start_date, end_date = date_time_helper.get_quarter_first_and_last_date(quarter)
        self.assertEqual(start_date, datetime.date(2021, 7, 1))
        self.assertEqual(end_date, datetime.date(2021, 9, 30))

        quarter = "Q4 2021"
        start_date, end_date = date_time_helper.get_quarter_first_and_last_date(quarter)
        self.assertEqual(start_date, datetime.date(2021, 10, 1))
        self.assertEqual(end_date, datetime.date(2021, 12, 31))

        quarter = "Q5 2021"
        start_date, end_date = date_time_helper.get_quarter_first_and_last_date(quarter)
        self.assertEqual(start_date, None)
        self.assertEqual(end_date, None)

    def test_datatogetswitch(self):
        """Test data to get switch"""

    def test_month_to_quarter(self):
        """Test month to quarter"""
        month = "January"
        quarter = date_time_helper.month_to_quarter(month)
        self.assertEqual(quarter, "Q1")

        month = "February"
        quarter = date_time_helper.month_to_quarter(month)
        self.assertEqual(quarter, "Q1")

        month = "March"
        quarter = date_time_helper.month_to_quarter(month)
        self.assertEqual(quarter, "Q1")

        month = "April"
        quarter = date_time_helper.month_to_quarter(month)
        self.assertEqual(quarter, "Q2")

        month = "May"
        quarter = date_time_helper.month_to_quarter(month)
        self.assertEqual(quarter, "Q2")

        month = "June"
        quarter = date_time_helper.month_to_quarter(month)
        self.assertEqual(quarter, "Q2")

        month = "July"
        quarter = date_time_helper.month_to_quarter(month)
        self.assertEqual(quarter, "Q3")

        month = "August"
        quarter = date_time_helper.month_to_quarter(month)
        self.assertEqual(quarter, "Q3")

        month = "September"
        quarter = date_time_helper.month_to_quarter(month)
        self.assertEqual(quarter, "Q3")

        month = "October"
        quarter = date_time_helper.month_to_quarter(month)
        self.assertEqual(quarter, "Q4")

        month = "November"
        quarter = date_time_helper.month_to_quarter(month)
        self.assertEqual(quarter, "Q4")

        month = "December"
        quarter = date_time_helper.month_to_quarter(month)
        self.assertEqual(quarter, "Q4")

        month = "Not a month"
        quarter = date_time_helper.month_to_quarter(month)
        self.assertEqual(quarter, None)

    def test_get_quarter(self):
        """test get quarter"""
        start_date = datetime.date(2021, 1, 1)
        end_date = datetime.date(2021, 3, 31)
        quarters = date_time_helper.get_quarters(start_date, end_date)
        self.assertEqual(quarters, ["Q1 2021"])

        start_date = datetime.date(2021, 1, 1)
        end_date = datetime.date(2022, 3, 31)
        quarters = date_time_helper.get_quarters(start_date, end_date)
        self.assertEqual(
            quarters, ["Q1 2021", "Q2 2021", "Q3 2021", "Q4 2021", "Q1 2022"]
        )

        start_date = datetime.date(2021, 1, 1)
        end_date = datetime.date(2020, 12, 31)
        quarters = date_time_helper.get_quarters(start_date, end_date)
        self.assertEqual(quarters, [])

    def test_get_months(self):
        """test get months"""
        start_date = datetime.date(2021, 1, 1)
        end_date = datetime.date(2021, 3, 31)
        months = date_time_helper.get_months(start_date, end_date)
        self.assertEqual(
            months,
            [
                datetime.date(2021, 1, 31),
                datetime.date(2021, 2, 28),
                datetime.date(2021, 3, 31),
            ],
        )

        start_date = datetime.date(2021, 1, 1)
        end_date = datetime.date(2020, 12, 31)
        months = date_time_helper.get_months(start_date, end_date)
        self.assertEqual(months, [])

    def test_get_weeks(self):
        """test get weeks"""


class TestSchemas(unittest.TestCase):
    """ "Test schemas"""

    def test_stock_input(self):
        """Test stock input"""

        schema = schemas.stock_input()
        self.assertIsInstance(schema, dict)

    def test_transaction_input(self):
        """Test stock output"""
        schema = schemas.transaction_input()
        self.assertIsInstance(schema, dict)


class TestUtils(unittest.TestCase):
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
        self.assertEqual(unique_items, ["a", "b", "c"])

        items = []

        unique_items = utils.get_unique_items(items, key_to_filter)
        self.assertEqual(unique_items, [])

    def test_get_weighted_average(self):
        """Test get weighted average"""
        data = [1, 4]
        weight = [1, 2]
        weighted_average = utils.get_weighted_average(data, weight)
        self.assertEqual(weighted_average, 3.0)

    def test_add_meta_data_to_stock_data2(self):
        """Test add meta data to stock data"""
        stock_data = [{"symbol": "ABC"}, {"symbol": "XYZ"}]
        meta_data = [
            {"symbol": "ABC", "name": "ABC Inc."},
            {"symbol": "XYZ", "name": "XYZ Inc."},
        ]

        container = mock.Mock()
        container.read_all_items.return_value = meta_data
        result = utils.add_meta_data_to_stock_data(stock_data, container)
        self.assertEqual(
            result,
            [
                {"symbol": "ABC", "meta": {"symbol": "ABC", "name": "ABC Inc."}},
                {"symbol": "XYZ", "meta": {"symbol": "XYZ", "name": "XYZ Inc."}},
            ],
        )

        # Test when no meta data is found
        container.read_all_items.return_value = []
        result = utils.add_meta_data_to_stock_data(stock_data, container)
        self.assertEqual(
            result,
            [
                {"symbol": "ABC", "meta": {}},
                {"symbol": "XYZ", "meta": {}},
            ],
        )
