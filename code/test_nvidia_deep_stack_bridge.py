import pytest
from unittest.mock import patch, MagicMock
from nvidia_deep_stack_bridge import fetch_dcgm_metrics

@pytest.fixture(autouse=True)
def clear_cache():
    """Clear the Streamlit cache before each test."""
    fetch_dcgm_metrics.clear()

@patch('nvidia_deep_stack_bridge.requests.get')
def test_fetch_dcgm_metrics_success(mock_get):
    """Test successful fetching of metrics."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = "test metrics"
    mock_get.return_value = mock_response

    status_code, text = fetch_dcgm_metrics()

    assert status_code == 200
    assert text == "test metrics"
    mock_get.assert_called_once()


@patch('nvidia_deep_stack_bridge.requests.get')
@patch('nvidia_deep_stack_bridge.logging.error')
def test_fetch_dcgm_metrics_exception(mock_log_error, mock_get):
    """Test fetching metrics when an exception is raised."""
    mock_get.side_effect = Exception("Test Exception")

    status_code, text = fetch_dcgm_metrics()

    assert status_code == 500
    assert text == ""
    mock_get.assert_called_once()
    mock_log_error.assert_called_once()
