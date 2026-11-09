import sys
import os
import pytest
from unittest.mock import patch
from streamlit.testing.v1 import AppTest

# Clear module to ensure clean import
if 'nvidia_deep_stack_bridge' in sys.modules:
    del sys.modules['nvidia_deep_stack_bridge']

@patch("requests.get")
def test_app_renders_correctly(mock_get):
    # Mock requests to avoid network calls during test
    mock_get.return_value.status_code = 200
    mock_get.return_value.text = "DCGM_FI_DEV_GPU_UTIL 50.0\nDCGM_FI_DEV_FB_USED 2048\nDCGM_FI_DEV_GPU_TEMP 65\n"

    app_path = os.path.join(os.path.dirname(__file__), "nvidia_deep_stack_bridge.py")
    app = AppTest.from_file(app_path)
    app.run()

    # Assertions
    assert not app.exception
    assert "⚡ GMM — NVIDIA Deep Stack & AI Workbench Bridge" in app.title[0].value
    assert "DCGM Exporter Active (:9400)" in app.success[0].value

    # Check that metrics are rendered
    assert len(app.metric) >= 3
    assert app.metric[0].label == "GPU Utilization"
    assert app.metric[0].value == "50.0%"

    import nvidia_deep_stack_bridge
    nvidia_deep_stack_bridge.fetch_telemetry_metrics.clear()
