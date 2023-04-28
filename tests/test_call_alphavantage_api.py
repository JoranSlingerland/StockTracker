"""Test the call_alphavantage_api module."""

from unittest.mock import MagicMock, patch

import pytest
from requests import Response

from call_alphavantage_api import main


@patch("requests.get")
def test_valid_response(mock_get):
    """Test the main function."""

    url = "https://foo.bar"
    api_key = "123"
    mock_response = MagicMock(spec=Response)
    mock_response.status_code = 200
    mock_response.json.return_value = {"foo": "bar"}
    mock_get.return_value = mock_response

    result = main([url, api_key])
    assert result == {"foo": "bar"}
    assert mock_get.call_count == 1
    mock_get.assert_called_with("https://foo.bar&apikey=123", timeout=10)


@patch("requests.get")
@patch("time.sleep")
def test_http_error(mock_sleep, mock_get):
    """Test the main function."""

    url = "https://foo.bar"
    api_key = "123"
    mock_response = MagicMock(spec=Response)
    mock_response.status_code = 500
    mock_response.json.return_value = {"foo": "bar"}
    mock_get.return_value = mock_response

    with pytest.raises(Exception, match="Error: 500"):
        main([url, api_key])

    assert mock_get.call_count == 4
    mock_get.assert_called_with("https://foo.bar&apikey=123", timeout=10)


@patch("requests.get")
@patch("time.sleep")
def test_too_many_api_calls(mock_sleep, mock_get):
    """Test the main function."""

    url = "https://foo.bar"
    api_key = "123"
    mock_response = MagicMock(spec=Response)
    mock_response.status_code = 200
    mock_response.json.return_value = {"Note": "bar"}
    mock_get.return_value = mock_response

    with pytest.raises(Exception, match="Too many api calls, Exiting."):
        main([url, api_key])

    assert mock_get.call_count == 19
    mock_get.assert_called_with("https://foo.bar&apikey=123", timeout=10)
