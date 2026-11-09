import pytest
from unittest.mock import patch
import sys
import importlib
from streamlit.testing.v1 import AppTest

# Dummy response for requests.get
class MockResponse:
    def __init__(self, status_code, text):
        self.status_code = status_code
        self.text = text

@pytest.fixture(autouse=True)
def clear_streamlit_cache():
    import streamlit as st
    st.cache_data.clear()

@pytest.fixture(autouse=True)
def reload_module():
    # Make sure we don't have the module loaded, allowing clean patching
    if 'nvidia_deep_stack_bridge' in sys.modules:
        del sys.modules['nvidia_deep_stack_bridge']

@patch('requests.get')
def test_app_telemetry_success(mock_get):
    mock_get.return_value = MockResponse(
        status_code=200,
        text="""
# HELP DCGM_FI_DEV_GPU_UTIL GPU utilization.
# TYPE DCGM_FI_DEV_GPU_UTIL gauge
DCGM_FI_DEV_GPU_UTIL 50.5
# HELP DCGM_FI_DEV_FB_USED Framebuffer memory used (in MB).
# TYPE DCGM_FI_DEV_FB_USED gauge
DCGM_FI_DEV_FB_USED 4000.0
# HELP DCGM_FI_DEV_GPU_TEMP GPU temperature (in C).
# TYPE DCGM_FI_DEV_GPU_TEMP gauge
DCGM_FI_DEV_GPU_TEMP 65.0
"""
    )

    at = AppTest.from_file("nvidia_deep_stack_bridge.py")
    at.run()

    assert not at.exception

    metrics = at.metric
    metric_labels = [m.label for m in metrics]
    metric_values = [m.value for m in metrics]

    assert "GPU Utilization" in metric_labels
    idx_gpu_util = metric_labels.index("GPU Utilization")
    assert metric_values[idx_gpu_util] == "50.5%"

    assert "VRAM Used" in metric_labels
    idx_vram = metric_labels.index("VRAM Used")
    assert metric_values[idx_vram] == "4000 MB"

    assert "GPU Temp" in metric_labels
    idx_temp = metric_labels.index("GPU Temp")
    assert metric_values[idx_temp] == "65 °C"

@patch('requests.get')
def test_app_telemetry_failure(mock_get):
    mock_get.side_effect = Exception("Connection refused")

    at = AppTest.from_file("nvidia_deep_stack_bridge.py")
    at.run()

    assert not at.exception

    assert len(at.error) > 0
    error_values = [e.value for e in at.error]
    assert any("DCGM offline / unreachable" in val for val in error_values)

@patch('requests.get')
def test_app_telemetry_not_200(mock_get):
    mock_get.return_value = MockResponse(status_code=500, text="Internal Server Error")

    at = AppTest.from_file("nvidia_deep_stack_bridge.py")
    at.run()

    assert not at.exception

    assert len(at.warning) > 0
    warning_values = [w.value for w in at.warning]
    assert any("DCGM status: 500" in val for val in warning_values)

def test_app_tabs():
    with patch('requests.get') as mock_get:
        mock_get.return_value = MockResponse(status_code=200, text="")
        at = AppTest.from_file("nvidia_deep_stack_bridge.py")
        at.run()

        assert not at.exception

        # Verify button execution in Tab 1
        # Click the button "Run Maxine OpenUSD Verification"
        at.button[0].click().run()
        assert not at.exception

        # Should now have success message in the UI
        success_values = [s.value for s in at.success]
        assert any("Pipeline operational" in val for val in success_values)
