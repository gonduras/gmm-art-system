import sys
import unittest
from unittest.mock import patch, MagicMock

class TestNvidiaDeepStackBridge(unittest.TestCase):
    def setUp(self):
        # Clear module if it's already imported to prevent test pollution
        if 'nvidia_deep_stack_bridge' in sys.modules:
            del sys.modules['nvidia_deep_stack_bridge']

    @patch('streamlit.set_page_config')
    @patch('streamlit.title')
    @patch('streamlit.caption')
    @patch('streamlit.columns')
    @patch('streamlit.subheader')
    @patch('streamlit.markdown')
    @patch('streamlit.metric')
    @patch('streamlit.divider')
    @patch('streamlit.tabs')
    @patch('streamlit.header')
    @patch('streamlit.button')
    @patch('streamlit.code')
    @patch('streamlit.info')
    @patch('streamlit.success')
    @patch('streamlit.warning')
    @patch('streamlit.error')
    @patch('os.path.exists')
    @patch('requests.get')
    def test_maxine_path_active(
        self, mock_get, mock_exists, mock_error, mock_warning, mock_success,
        mock_info, mock_code, mock_button, mock_header, mock_tabs, mock_divider,
        mock_metric, mock_markdown, mock_subheader, mock_columns, mock_caption,
        mock_title, mock_set_page_config
    ):
        # Setup mocks
        mock_col1 = MagicMock()
        mock_col2 = MagicMock()
        mock_col3 = MagicMock()
        mock_col4 = MagicMock()
        mock_columns.return_value = (mock_col1, mock_col2, mock_col3, mock_col4)

        mock_tab1 = MagicMock()
        mock_tab2 = MagicMock()
        mock_tab3 = MagicMock()
        mock_tabs.return_value = (mock_tab1, mock_tab2, mock_tab3)

        # Simulate active Maxine path
        mock_exists.return_value = True

        # Import the module which runs the code
        import nvidia_deep_stack_bridge

        # Assertions
        mock_success.assert_any_call("Maxine VFX SDK 1.3.0.0 Active")
        mock_markdown.assert_any_call("- **AIGS:** AI Green Screen Matting")

    @patch('streamlit.set_page_config')
    @patch('streamlit.title')
    @patch('streamlit.caption')
    @patch('streamlit.columns')
    @patch('streamlit.subheader')
    @patch('streamlit.markdown')
    @patch('streamlit.metric')
    @patch('streamlit.divider')
    @patch('streamlit.tabs')
    @patch('streamlit.header')
    @patch('streamlit.button')
    @patch('streamlit.code')
    @patch('streamlit.info')
    @patch('streamlit.success')
    @patch('streamlit.warning')
    @patch('streamlit.error')
    @patch('os.path.exists')
    @patch('requests.get')
    def test_maxine_path_missing(
        self, mock_get, mock_exists, mock_error, mock_warning, mock_success,
        mock_info, mock_code, mock_button, mock_header, mock_tabs, mock_divider,
        mock_metric, mock_markdown, mock_subheader, mock_columns, mock_caption,
        mock_title, mock_set_page_config
    ):
        # Setup mocks
        mock_col1 = MagicMock()
        mock_col2 = MagicMock()
        mock_col3 = MagicMock()
        mock_col4 = MagicMock()
        mock_columns.return_value = (mock_col1, mock_col2, mock_col3, mock_col4)

        mock_tab1 = MagicMock()
        mock_tab2 = MagicMock()
        mock_tab3 = MagicMock()
        mock_tabs.return_value = (mock_tab1, mock_tab2, mock_tab3)

        # Simulate missing Maxine path
        mock_exists.return_value = False

        # Import the module which runs the code
        import nvidia_deep_stack_bridge

        # Assertions
        mock_warning.assert_any_call("Maxine path not detected in container mount")

if __name__ == '__main__':
    unittest.main()
