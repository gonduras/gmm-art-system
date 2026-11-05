import sys
import pytest
from unittest.mock import patch, MagicMock

# Needed to test streamlit apps without pollution
def test_dcgm_metrics_extracted(monkeypatch):
    import streamlit as st

    # Mock requests.get
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.text = """# HELP DCGM_FI_DEV_GPU_UTIL
# TYPE DCGM_FI_DEV_GPU_UTIL gauge
DCGM_FI_DEV_GPU_UTIL{gpu="0"} 45.2
# HELP DCGM_FI_DEV_FB_USED
# TYPE DCGM_FI_DEV_FB_USED gauge
DCGM_FI_DEV_FB_USED{gpu="0"} 1500
# HELP DCGM_FI_DEV_GPU_TEMP
# TYPE DCGM_FI_DEV_GPU_TEMP gauge
DCGM_FI_DEV_GPU_TEMP{gpu="0"} 75
"""

    with patch('requests.get', return_value=mock_resp):
        with patch('streamlit.metric') as mock_metric:
            # We import here so code executes with mocks in place
            if 'nvidia_deep_stack_bridge' in sys.modules:
                del sys.modules['nvidia_deep_stack_bridge']

            import nvidia_deep_stack_bridge

            # Verify metric calls
            mock_metric.assert_any_call("GPU Utilization", "45.2%")
            mock_metric.assert_any_call("VRAM Used", "1500 MB")
            mock_metric.assert_any_call("GPU Temp", "75 °C")
