"""Test get_meta_data function"""

from unittest.mock import Mock, patch

import time_machine

from get_meta_data import call_brandfetch_api, call_clearbit_api, main


def test_no_symbols():
    """test_no_symbols"""
    payload = [
        [],
        [],
        {
            "clearbit_api_key": "clearbit_api_key",
            "brandfetch_api_key": "brandfetch_api_key",
        },
        "userid",
    ]

    result = main(payload)
    assert result == []


@time_machine.travel("2023-05-31")
@patch("get_meta_data.call_clearbit_api")
@patch("get_meta_data.call_brandfetch_api")
def test_main(mock_brandfetch_api, mock_clearbit_api):
    """test_main"""

    mock_clearbit_api.return_value = {
        "name": "Acme Inc.",
        "description": "A company that makes things",
        "geo": {"country": "US"},
        "category": {"sector": "Manufacturing"},
    }
    mock_brandfetch_api.return_value = {
        "name": "Acme Inc.",
        "domain": "acme.com",
        "description": "A company that makes things",
        "links": [{"name": "twitter", "url": "https://example.com"}],
        "logos": [
            {
                "type": "logo",
                "theme": "light",
                "formats": [
                    {
                        "src": "example.com/logo.png",
                        "background": "transparent",
                        "format": "svg",
                        "size": 15555,
                    }
                ],
            }
        ],
        "images": [
            {
                "type": "banner",
                "formats": [
                    {
                        "src": "example.com/image.png",
                        "background": "transparent",
                        "format": "png",
                        "height": 500,
                        "width": 1500,
                        "size": 5539,
                    }
                ],
            }
        ],
    }

    payload = (
        ["AAPL", "GOOG"],
        [
            {"symbol": "AAPL", "domain": "apple.com"},
            {"symbol": "GOOG", "domain": "google.com"},
        ],
        {"clearbit_api_key": "123", "brandfetch_api_key": "456"},
        "user123",
    )
    result = main(payload)

    expected_result = [
        {
            "symbol": "AAPL",
            "name": "Acme Inc.",
            "description": "A company that makes things",
            "country": "US",
            "sector": "Manufacturing",
            "domain": "apple.com",
            "links": [{"name": "twitter", "url": "https://example.com"}],
            "expiry": "2023-06-30",
            "userid": "user123",
            "logo": "example.com/logo.png",
            "icon": None,
            "symbol_img": None,
            "banner": "example.com/image.png",
        },
        {
            "symbol": "GOOG",
            "name": "Acme Inc.",
            "description": "A company that makes things",
            "country": "US",
            "sector": "Manufacturing",
            "domain": "google.com",
            "links": [{"name": "twitter", "url": "https://example.com"}],
            "expiry": "2023-06-30",
            "userid": "user123",
            "logo": "example.com/logo.png",
            "icon": None,
            "symbol_img": None,
            "banner": "example.com/image.png",
        },
    ]

    for item in result:
        item.pop("id")

    assert result == expected_result


@time_machine.travel("2023-05-31")
@patch("get_meta_data.call_clearbit_api")
@patch("get_meta_data.call_brandfetch_api")
def test_main_no_images(mock_brandfetch_api, mock_clearbit_api):
    """test_main"""

    mock_clearbit_api.return_value = {
        "name": "Acme Inc.",
        "description": "A company that makes things",
        "geo": {"country": "US"},
        "category": {"sector": "Manufacturing"},
    }
    mock_brandfetch_api.return_value = {
        "name": "Acme Inc.",
        "domain": "acme.com",
        "description": "A company that makes things",
        "links": [{"name": "twitter", "url": "https://example.com"}],
        "logos": [],
        "images": [],
    }

    payload = (
        ["AAPL", "GOOG"],
        [
            {"symbol": "AAPL", "domain": "apple.com"},
            {"symbol": "GOOG", "domain": "google.com"},
        ],
        {"clearbit_api_key": "123", "brandfetch_api_key": "456"},
        "user123",
    )
    result = main(payload)

    expected_result = [
        {
            "symbol": "AAPL",
            "name": "Acme Inc.",
            "description": "A company that makes things",
            "country": "US",
            "sector": "Manufacturing",
            "domain": "apple.com",
            "links": [{"name": "twitter", "url": "https://example.com"}],
            "expiry": "2023-06-30",
            "userid": "user123",
            "logo": None,
            "icon": None,
            "symbol_img": None,
            "banner": None,
        },
        {
            "symbol": "GOOG",
            "name": "Acme Inc.",
            "description": "A company that makes things",
            "country": "US",
            "sector": "Manufacturing",
            "domain": "google.com",
            "links": [{"name": "twitter", "url": "https://example.com"}],
            "expiry": "2023-06-30",
            "userid": "user123",
            "logo": None,
            "icon": None,
            "symbol_img": None,
            "banner": None,
        },
    ]

    for item in result:
        item.pop("id")

    assert result == expected_result


@time_machine.travel("2023-05-31")
@patch("get_meta_data.call_clearbit_api")
@patch("get_meta_data.call_brandfetch_api")
def test_main_dark_images(mock_brandfetch_api, mock_clearbit_api):
    """test_main"""

    mock_clearbit_api.return_value = {
        "name": "Acme Inc.",
        "description": "A company that makes things",
        "geo": {"country": "US"},
        "category": {"sector": "Manufacturing"},
    }
    mock_brandfetch_api.return_value = {
        "name": "Acme Inc.",
        "domain": "acme.com",
        "description": "A company that makes things",
        "links": [{"name": "twitter", "url": "https://example.com"}],
        "logos": [
            {
                "type": "logo",
                "theme": "dark",
                "formats": [
                    {
                        "src": "example.com/logo.png",
                        "background": "transparent",
                        "format": "svg",
                        "size": 15555,
                    }
                ],
            }
        ],
        "images": [],
    }

    payload = (
        ["AAPL", "GOOG"],
        [
            {"symbol": "AAPL", "domain": "apple.com"},
            {"symbol": "GOOG", "domain": "google.com"},
        ],
        {"clearbit_api_key": "123", "brandfetch_api_key": "456"},
        "user123",
    )
    result = main(payload)

    expected_result = [
        {
            "symbol": "AAPL",
            "name": "Acme Inc.",
            "description": "A company that makes things",
            "country": "US",
            "sector": "Manufacturing",
            "domain": "apple.com",
            "links": [{"name": "twitter", "url": "https://example.com"}],
            "expiry": "2023-06-30",
            "userid": "user123",
            "logo": "example.com/logo.png",
            "icon": None,
            "symbol_img": None,
            "banner": None,
        },
        {
            "symbol": "GOOG",
            "name": "Acme Inc.",
            "description": "A company that makes things",
            "country": "US",
            "sector": "Manufacturing",
            "domain": "google.com",
            "links": [{"name": "twitter", "url": "https://example.com"}],
            "expiry": "2023-06-30",
            "userid": "user123",
            "logo": "example.com/logo.png",
            "icon": None,
            "symbol_img": None,
            "banner": None,
        },
    ]

    for item in result:
        item.pop("id")

    assert result == expected_result


class TestApiCalls:
    """TestApiCalls"""

    @patch("requests.get")
    def test_call_clearbit_api(self, mock_get):
        """test_call_clearbit_api"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"name": "John Doe"}
        mock_get.return_value = mock_response

        result = call_clearbit_api("https://clearbit.com", "123")
        assert result == {"name": "John Doe"}

    @patch("requests.get")
    def test_call_brandfetch_api(self, mock_get):
        """test_call_brandfetch_api"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"name": "John Doe"}
        mock_get.return_value = mock_response

        result = call_brandfetch_api("https://brandfetch.com", "123")
        assert result == {"name": "John Doe"}

    @patch("requests.get")
    def test_call_brandfetch_error(self, mock_get):
        """test_call_brandfetch_error"""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.json.return_value = {"name": "John Doe"}
        mock_get.return_value = mock_response

        result = call_brandfetch_api("https://brandfetch.com", "123")
        assert result is None

    @patch("requests.get")
    def test_call_clearbit_error(self, mock_get):
        """test_call_clearbit_error"""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.json.return_value = {"name": "John Doe"}
        mock_get.return_value = mock_response

        result = call_clearbit_api("https://clearbit.com", "123")
        assert result is None
