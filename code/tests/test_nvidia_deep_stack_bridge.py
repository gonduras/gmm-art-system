import pytest
from unittest.mock import patch, MagicMock
import requests
import streamlit as st

# We need to import fetch_dcgm_metrics, but since we are testing Streamlit stuff,
# we need to be careful with caching. Let's clear the cache before each test just in case.
# Also, we import the function under test.
from nvidia_deep_stack_bridge import fetch_dcgm_metrics

@pytest.fixture(autouse=True)
def clear_streamlit_cache():
    """Clear Streamlit cache before each test."""
    fetch_dcgm_metrics.clear()
    yield

class TestFetchDCGMMetrics:

    @patch("nvidia_deep_stack_bridge.requests.get")
    def test_fetch_dcgm_metrics_success(self, mock_get):
        # Setup mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "DCGM_FI_DEV_GPU_UTIL 45.2\nDCGM_FI_DEV_FB_USED 2048"
        mock_get.return_value = mock_response

        # Call function
        result = fetch_dcgm_metrics()

        # Assertions
        mock_get.assert_called_once_with("http://localhost:9400/metrics", timeout=2)
        assert result["status_code"] == 200
        assert result["text"] == "DCGM_FI_DEV_GPU_UTIL 45.2\nDCGM_FI_DEV_FB_USED 2048"
        assert result["error"] is None

    @patch("nvidia_deep_stack_bridge.requests.get")
    def test_fetch_dcgm_metrics_non_200(self, mock_get):
        # Setup mock response
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.text = "Not Found"
        mock_get.return_value = mock_response

        # Call function
        result = fetch_dcgm_metrics()

        # Assertions
        mock_get.assert_called_once_with("http://localhost:9400/metrics", timeout=2)
        assert result["status_code"] == 404
        assert result["text"] is None
        assert result["error"] is None

    @patch("nvidia_deep_stack_bridge.requests.get")
    @patch("nvidia_deep_stack_bridge.logging.error")
    def test_fetch_dcgm_metrics_exception(self, mock_logging_error, mock_get):
        # Setup mock to raise exception
        mock_get.side_effect = requests.exceptions.RequestException("Connection refused")

        # Call function
        result = fetch_dcgm_metrics()

        # Assertions
        mock_get.assert_called_once_with("http://localhost:9400/metrics", timeout=2)
        mock_logging_error.assert_called_once()
        assert result["status_code"] is None
        assert result["text"] is None
        assert result["error"] == "Connection refused"
