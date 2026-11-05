import sys
import unittest
from unittest.mock import patch, MagicMock
import importlib

class TestDCGMTelemetry(unittest.TestCase):

    def setUp(self):
        # Create a mock for streamlit
        self.mock_st = MagicMock()

        # Mock columns and tabs context managers safely
        mock_col = MagicMock()
        mock_col.__enter__ = MagicMock(return_value=mock_col)
        mock_col.__exit__ = MagicMock(return_value=None)

        mock_tab = MagicMock()
        mock_tab.__enter__ = MagicMock(return_value=mock_tab)
        mock_tab.__exit__ = MagicMock(return_value=None)

        # Make mock_st.columns and mock_st.tabs return iterables of arbitrary length if needed,
        # but specifically handle the unpacking used in the script.
        self.mock_st.columns.return_value = [mock_col] * 4
        self.mock_st.tabs.return_value = [mock_tab] * 3

        # Patch sys.modules safely for this test case
        self.modules_patcher = patch.dict('sys.modules', {'streamlit': self.mock_st})
        self.modules_patcher.start()

    def tearDown(self):
        self.modules_patcher.stop()
        # Remove the module from sys.modules so it runs fresh each time
        if 'nvidia_deep_stack_bridge' in sys.modules:
            del sys.modules['nvidia_deep_stack_bridge']

    @patch('requests.get')
    def test_dcgm_telemetry_success(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = """
# HELP DCGM_FI_DEV_GPU_UTIL GPU utilization (%).
# TYPE DCGM_FI_DEV_GPU_UTIL gauge
DCGM_FI_DEV_GPU_UTIL{gpu="0",UUID="GPU-123"} 85.5
# HELP DCGM_FI_DEV_FB_USED Framebuffer memory used (in MB).
# TYPE DCGM_FI_DEV_FB_USED gauge
DCGM_FI_DEV_FB_USED{gpu="0",UUID="GPU-123"} 4096
# HELP DCGM_FI_DEV_GPU_TEMP GPU temperature (in C).
# TYPE DCGM_FI_DEV_GPU_TEMP gauge
DCGM_FI_DEV_GPU_TEMP{gpu="0",UUID="GPU-123"} 70
"""
        mock_get.return_value = mock_response

        # Import the module to run its top-level code
        import nvidia_deep_stack_bridge

        mock_get.assert_called_once_with("http://localhost:9400/metrics", timeout=2)

        self.mock_st.success.assert_any_call("DCGM Exporter Active (:9400)")
        self.mock_st.metric.assert_any_call("GPU Utilization", "85.5%")
        self.mock_st.metric.assert_any_call("VRAM Used", "4096 MB")
        self.mock_st.metric.assert_any_call("GPU Temp", "70 °C")

    @patch('requests.get')
    def test_dcgm_telemetry_non_200(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        import nvidia_deep_stack_bridge

        self.mock_st.warning.assert_any_call("DCGM status: 404")

    @patch('requests.get')
    def test_dcgm_telemetry_exception(self, mock_get):
        import requests
        mock_get.side_effect = requests.exceptions.Timeout("Connection timed out")

        import nvidia_deep_stack_bridge

        # Check that st.error was called with the exception
        self.assertTrue(any("DCGM offline / unreachable" in call.args[0] for call in self.mock_st.error.call_args_list))

if __name__ == '__main__':
    unittest.main()
