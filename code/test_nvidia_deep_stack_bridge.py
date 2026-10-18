from unittest.mock import MagicMock, patch
import pytest

import nvidia_deep_stack_bridge

def test_check_dcgm_status_success():
    with patch('nvidia_deep_stack_bridge.requests.get') as mock_get:
        # Configure the mock to return a response with status_code 200 and some valid text
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = """
# HELP DCGM_FI_DEV_GPU_UTIL GPU Utilization
# TYPE DCGM_FI_DEV_GPU_UTIL gauge
DCGM_FI_DEV_GPU_UTIL{gpu="0",UUID="GPU-xxx"} 45.5
# HELP DCGM_FI_DEV_FB_USED Framebuffer memory used (in MB)
# TYPE DCGM_FI_DEV_FB_USED gauge
DCGM_FI_DEV_FB_USED{gpu="0",UUID="GPU-xxx"} 2048
# HELP DCGM_FI_DEV_GPU_TEMP GPU Temperature
# TYPE DCGM_FI_DEV_GPU_TEMP gauge
DCGM_FI_DEV_GPU_TEMP{gpu="0",UUID="GPU-xxx"} 65
"""
        mock_get.return_value = mock_response

        metrics = nvidia_deep_stack_bridge.check_dcgm_status()

        assert metrics["status"] == "Active"
        assert metrics["GPU Utilization"] == "45.5%"
        assert metrics["VRAM Used"] == "2048 MB"
        assert metrics["GPU Temp"] == "65 °C"

def test_check_dcgm_status_non_200():
    with patch('nvidia_deep_stack_bridge.requests.get') as mock_get:
        # Configure the mock to return a response with status_code 500
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response

        metrics = nvidia_deep_stack_bridge.check_dcgm_status()

        assert "warning" in metrics
        assert "500" in metrics["warning"]

def test_check_dcgm_status_exception():
    with patch('nvidia_deep_stack_bridge.requests.get') as mock_get:
        # Configure the mock to raise an exception
        mock_get.side_effect = Exception("Connection Refused")

        metrics = nvidia_deep_stack_bridge.check_dcgm_status()

        assert "error" in metrics
        assert "Connection Refused" in metrics["error"]

def test_check_maxine_status_exists():
    with patch('nvidia_deep_stack_bridge.os.path.exists') as mock_exists:
        # Configure the mock to return True
        mock_exists.return_value = True

        assert nvidia_deep_stack_bridge.check_maxine_status() == True

def test_check_maxine_status_not_exists():
    with patch('nvidia_deep_stack_bridge.os.path.exists') as mock_exists:
        # Configure the mock to return False
        mock_exists.return_value = False

        assert nvidia_deep_stack_bridge.check_maxine_status() == False
