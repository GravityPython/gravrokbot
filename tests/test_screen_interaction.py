import unittest
import os
import sys
from unittest.mock import patch, MagicMock

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gravrokbot.core.screen_interaction import ScreenInteraction

class TestScreenInteraction(unittest.TestCase):
    """Test cases for ScreenInteraction class"""
    
    def setUp(self):
        """Set up test case"""
        self.config = {
            'input_delay': 0.1,
            'click_randomize_range': 5
        }
        
        # Create mock objects
        self.mock_logger = MagicMock()
        self.mock_pyautogui = MagicMock()
        self.mock_pyautogui.size.return_value = (1600, 900)
        
        # Patch logger and pyautogui
        self.logger_patcher = patch('gravrokbot.core.screen_interaction.logging.getLogger')
        self.logger_patcher.start().return_value = self.mock_logger
        
        self.pyautogui_patcher = patch('gravrokbot.core.screen_interaction.pyautogui', self.mock_pyautogui)
        self.pyautogui_patcher.start()
        
        # Create ScreenInteraction instance
        self.screen = ScreenInteraction(self.config)
    
    def tearDown(self):
        """Clean up after test case"""
        self.logger_patcher.stop()
        self.pyautogui_patcher.stop()
    
    def test_take_screenshot(self):
        """Test take_screenshot method"""
        # Call method
        self.screen.take_screenshot()
        
        # Verify screenshot was taken
        self.mock_pyautogui.screenshot.assert_called_once()
        
        # Test with region
        region = (100, 100, 200, 200)
        self.screen.take_screenshot(region)
        self.mock_pyautogui.screenshot.assert_called_with(region=region)
    
    def test_find_image(self):
        """Test find_image method"""
        # Set up mock
        mock_location = (800, 450)
        self.mock_pyautogui.locateCenterOnScreen.return_value = mock_location
        
        # Call method
        image_path = "test_image.png"
        with patch('os.path.exists', return_value=True):
            result = self.screen.find_image(image_path)
        
        # Verify image was searched
        self.mock_pyautogui.locateCenterOnScreen.assert_called_once()
        self.assertEqual(result, mock_location)
        
        # Test with image not found
        self.mock_pyautogui.locateCenterOnScreen.return_value = None
        with patch('os.path.exists', return_value=True):
            result = self.screen.find_image(image_path)
        self.assertIsNone(result)
        
        # Test with file not found
        with patch('os.path.exists', return_value=False):
            result = self.screen.find_image(image_path)
        self.assertIsNone(result)
    
    def test_humanized_click(self):
        """Test humanized_click method"""
        # Call method
        self.screen.humanized_click(800, 450)
        
        # Verify moveTo and click were called
        self.mock_pyautogui.moveTo.assert_called_once()
        self.mock_pyautogui.click.assert_called_once()
        
        # Test with no randomize
        self.mock_pyautogui.reset_mock()
        self.screen.humanized_click(800, 450, randomize=False)
        self.mock_pyautogui.moveTo.assert_called_once_with(800, 450, duration=self.mock_pyautogui.moveTo.call_args[1]['duration'])

if __name__ == '__main__':
    unittest.main() 