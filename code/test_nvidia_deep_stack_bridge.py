import pytest
from streamlit.testing.v1 import AppTest
from unittest.mock import patch

def test_nemoclaw_happy_path():
    at = AppTest.from_file("nvidia_deep_stack_bridge.py")
    with patch("requests.get") as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.text = "DCGM_FI_DEV_GPU_UTIL 45.0\nDCGM_FI_DEV_FB_USED 2048\nDCGM_FI_DEV_GPU_TEMP 65\n"
        at.run()

    assert not at.exception

    subheaders = [sh.value for sh in at.subheader]
    assert "🛡️ NemoClaw Gateway" in subheaders

    infos = [info.value for info in at.info]
    assert "OpenShell Gateway: https://127.0.0.1:8080" in infos

    successes = [s.value for s in at.success]
    assert "Gateway & Providers Registered" in successes

def test_nemoclaw_error_path():
    at = AppTest.from_file("nvidia_deep_stack_bridge.py")
    with patch("requests.get") as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.text = "DCGM_FI_DEV_GPU_UTIL 45.0\nDCGM_FI_DEV_FB_USED 2048\nDCGM_FI_DEV_GPU_TEMP 65\n"

        with patch("streamlit.info", side_effect=Exception("Test Exception")):
            at.run()

    assert not at.exception

    errors = [e.value for e in at.error]
    assert any("NemoClaw error: Test Exception" in err for err in errors)
