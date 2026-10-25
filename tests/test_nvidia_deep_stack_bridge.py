import sys
import unittest
from unittest.mock import patch, MagicMock
import os
import importlib

class TestMaxinePath(unittest.TestCase):
    def setUp(self):
        self.mock_st = MagicMock()
        self.mock_requests = MagicMock()
        sys.modules['streamlit'] = self.mock_st
        sys.modules['requests'] = self.mock_requests

        # Need to return 4 mock objects for st.columns(4)
        self.mock_st.columns.return_value = [MagicMock(), MagicMock(), MagicMock(), MagicMock()]
        # Need to return 3 mock objects for st.tabs(...)
        self.mock_st.tabs.return_value = [MagicMock(), MagicMock(), MagicMock()]

        # Force reload of the module in each test to re-evaluate module-level code
        if 'code.nvidia_deep_stack_bridge' in sys.modules:
            del sys.modules['code.nvidia_deep_stack_bridge']

    def test_maxine_path_exists(self):
        # We only mock os.path.exists to return True for the specific paths
        original_exists = os.path.exists

        def side_effect(path):
            if path in ["/project/gmm/vfx_sdk_core_v1.3.0.0_windows/VideoFX", "G:/gmm/vfx_sdk_core_v1.3.0.0_windows/VideoFX"]:
                return True
            return original_exists(path) # Fallback to actual implementation for other paths

        with patch('os.path.exists', side_effect=side_effect):
            import code.nvidia_deep_stack_bridge

        self.mock_st.success.assert_any_call("Maxine VFX SDK 1.3.0.0 Active")

    def test_maxine_path_not_exists(self):
        original_exists = os.path.exists

        def side_effect(path):
            if path in ["/project/gmm/vfx_sdk_core_v1.3.0.0_windows/VideoFX", "G:/gmm/vfx_sdk_core_v1.3.0.0_windows/VideoFX"]:
                return False
            return original_exists(path) # Fallback to actual implementation for other paths

        with patch('os.path.exists', side_effect=side_effect):
            import code.nvidia_deep_stack_bridge

        self.mock_st.warning.assert_any_call("Maxine path not detected in container mount")

if __name__ == '__main__':
    unittest.main()
