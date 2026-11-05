import time
import requests
from unittest.mock import patch
import nvidia_deep_stack_bridge as app
import streamlit as st

@patch("requests.get")
def benchmark_app(mock_get):
    # Simulate a slow network request
    def slow_req(*args, **kwargs):
        time.sleep(1)
        mock_resp = requests.Response()
        mock_resp.status_code = 200
        mock_resp._content = b"DCGM_FI_DEV_GPU_UTIL 50.0\nDCGM_FI_DEV_FB_USED 1000\nDCGM_FI_DEV_GPU_TEMP 60"
        return mock_resp

    mock_get.side_effect = slow_req

    start = time.time()

    # We measure consecutive calls to fetch_dcgm_metrics.
    # First call will cache
    app.fetch_dcgm_metrics()

    # Second call should be instant, hitting the cache
    app.fetch_dcgm_metrics()

    # Third call should be instant, hitting the cache
    app.fetch_dcgm_metrics()

    end = time.time()
    return end - start

if __name__ == "__main__":
    t = benchmark_app()
    print(f"Time taken for 3 fetch_dcgm_metrics calls: {t:.4f}s")
