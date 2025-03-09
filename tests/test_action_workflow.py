import unittest
import os
import sys
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gravrokbot.core.action_workflow import ActionWorkflow

class TestActionWorkflow(unittest.TestCase):
    """Test cases for ActionWorkflow class"""
    
    def setUp(self):
        """Set up test case"""
        self.config = {
            'enabled': True,
            'cooldown_minutes': 30,
            'max_retries': 3,
            'default_wait_time': 1.0
        }
        
        # Create mock screen interaction
        self.mock_screen = MagicMock()
        
        # Create mock logger
        self.mock_logger = MagicMock()
        
        # Patch logger
        self.logger_patcher = patch('gravrokbot.core.action_workflow.logging.getLogger')
        self.logger_patcher.start().return_value = self.mock_logger
        
        # Create ActionWorkflow instance
        self.action = ActionWorkflow("Test Action", self.mock_screen, self.config)
    
    def tearDown(self):
        """Clean up after test case"""
        self.logger_patcher.stop()
    
    def test_init(self):
        """Test initialization"""
        self.assertEqual(self.action.name, "Test Action")
        self.assertEqual(self.action.screen, self.mock_screen)
        self.assertEqual(self.action.config, self.config)
        self.assertEqual(self.action.enabled, True)
        self.assertEqual(self.action.cooldown_minutes, 30)
        self.assertEqual(self.action.max_retries, 3)
        self.assertEqual(self.action.retry_count, 0)
        self.assertEqual(self.action.state, 'idle')
    
    def test_execute_cooldown(self):
        """Test execute with action on cooldown"""
        # Set last execution time to be recent (within cooldown)
        self.action.last_execution_time = datetime.now() - timedelta(minutes=10)
        
        # Call execute
        result = self.action.execute()
        
        # Verify action was not executed because of cooldown
        self.assertFalse(result)
    
    def test_execute_disabled(self):
        """Test execute with action disabled"""
        # Disable action
        self.action.enabled = False
        
        # Call execute
        result = self.action.execute()
        
        # Verify action was not executed because it's disabled
        self.assertFalse(result)
    
    def test_execute_success(self):
        """Test successful execution"""
        # Call execute
        result = self.action.execute()
        
        # Verify action was executed
        self.assertTrue(result)
        self.assertIsNotNone(self.action.last_execution_time)
    
    def test_is_on_cooldown(self):
        """Test is_on_cooldown method"""
        # No last execution time
        self.assertFalse(self.action.is_on_cooldown())
        
        # Last execution time within cooldown
        self.action.last_execution_time = datetime.now() - timedelta(minutes=10)
        self.assertTrue(self.action.is_on_cooldown())
        
        # Last execution time outside cooldown
        self.action.last_execution_time = datetime.now() - timedelta(minutes=60)
        self.assertFalse(self.action.is_on_cooldown())
    
    def test_get_cooldown_remaining(self):
        """Test get_cooldown_remaining method"""
        # No last execution time
        self.assertEqual(self.action.get_cooldown_remaining(), 0)
        
        # Last execution time within cooldown
        self.action.last_execution_time = datetime.now() - timedelta(minutes=10)
        self.assertAlmostEqual(self.action.get_cooldown_remaining(), 20, delta=1)
        
        # Last execution time outside cooldown
        self.action.last_execution_time = datetime.now() - timedelta(minutes=60)
        self.assertEqual(self.action.get_cooldown_remaining(), 0)
    
    def test_retry_mechanism(self):
        """Test retry mechanism"""
        # Call on_failure
        self.action.on_failure()
        
        # Verify retry count was incremented
        self.assertEqual(self.action.retry_count, 1)
        
        # Call on_failure again
        self.action.on_failure()
        
        # Verify retry count was incremented again
        self.assertEqual(self.action.retry_count, 2)
        
        # Call on_failure to reach max retries
        self.action.on_failure()
        
        # Verify retry count was incremented and action completed
        self.assertEqual(self.action.retry_count, 3)
        self.assertEqual(self.action.state, 'completed')
    
    def test_on_success_resets_retry_count(self):
        """Test that on_success resets retry count"""
        # Set retry count
        self.action.retry_count = 2
        
        # Call on_success
        self.action.on_success()
        
        # Verify retry count was reset
        self.assertEqual(self.action.retry_count, 0)

if __name__ == '__main__':
    unittest.main() 