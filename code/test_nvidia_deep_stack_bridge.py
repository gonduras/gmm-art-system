import pytest
from unittest.mock import patch

# Ensure the module can be imported properly
from nvidia_deep_stack_bridge import fetch_dcgm_metrics

@pytest.fixture(autouse=True)
def clear_cache():
    """Clear the cache before each test to prevent state pollution."""
    fetch_dcgm_metrics.clear()

def test_fetch_dcgm_metrics_success():
    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.text = "test_metrics"

        status, text = fetch_dcgm_metrics()

        assert status == 200
        assert text == "test_metrics"
        mock_get.assert_called_once_with("http://localhost:9400/metrics", timeout=2)

def test_fetch_dcgm_metrics_caching():
    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.text = "test_metrics"

        # First call should hit the mocked requests.get
        status1, text1 = fetch_dcgm_metrics()
        assert status1 == 200
        assert mock_get.call_count == 1

        # Second call should use the cache, so requests.get shouldn't be called again
        status2, text2 = fetch_dcgm_metrics()
        assert status2 == 200
        assert mock_get.call_count == 1

def test_fetch_dcgm_metrics_exception():
    with patch('requests.get') as mock_get:
        mock_get.side_effect = Exception("Connection Refused")

        status, text = fetch_dcgm_metrics()

        assert status == 500
        assert text == "Internal error while fetching metrics."
        mock_get.assert_called_once_with("http://localhost:9400/metrics", timeout=2)
