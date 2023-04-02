"""Test the call_alphavantage_api module."""

from unittest.mock import MagicMock, patch

import pytest
from requests import Response

from call_alphavantage_api import main


@patch("shared_code.get_config.get_api_key")
@patch("requests.get")
def test_valid_response(mock_get, mock_get_api_key):
    """Test the main function."""

    url = "https://foo.bar"
    mock_get_api_key.return_value = "123"
    mock_response = MagicMock(spec=Response)
    mock_response.status_code = 200
    mock_response.json.return_value = {"foo": "bar"}
    mock_get.return_value = mock_response

    result = main(url)
    assert result == {"foo": "bar"}
    assert mock_get.call_count == 1
    assert mock_get_api_key.call_count == 1
    mock_get.assert_called_with("https://foo.bar&apikey=123", timeout=10)


@patch("shared_code.get_config.get_api_key")
@patch("requests.get")
@patch("time.sleep")
def test_http_error(mock_sleep, mock_get, mock_get_api_key):
    """Test the main function."""

    url = "https://foo.bar"
    mock_get_api_key.return_value = "123"
    mock_response = MagicMock(spec=Response)
    mock_response.status_code = 500
    mock_response.json.return_value = {"foo": "bar"}
    mock_get.return_value = mock_response

    with pytest.raises(Exception, match="Error: 500"):
        main(url)

    assert mock_get.call_count == 4
    assert mock_get_api_key.call_count == 1
    mock_get.assert_called_with("https://foo.bar&apikey=123", timeout=10)


@patch("shared_code.get_config.get_api_key")
@patch("requests.get")
@patch("time.sleep")
def test_too_many_api_calls(mock_sleep, mock_get, mock_get_api_key):
    """Test the main function."""

    url = "https://foo.bar"
    mock_get_api_key.return_value = "123"
    mock_response = MagicMock(spec=Response)
    mock_response.status_code = 200
    mock_response.json.return_value = {"Note": "bar"}
    mock_get.return_value = mock_response

    with pytest.raises(Exception, match="Too many api calls, Exiting."):
        main(url)

    assert mock_get.call_count == 19
    assert mock_get_api_key.call_count == 1
    mock_get.assert_called_with("https://foo.bar&apikey=123", timeout=10)
