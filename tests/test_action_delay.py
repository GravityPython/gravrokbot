import unittest
import os
import sys
from unittest.mock import patch, MagicMock, call

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gravrokbot.core.action_workflow import ActionWorkflow

class TestActionDelay(unittest.TestCase):
    """Test cases for the delay system in ActionWorkflow"""
    
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
        # Make humanized_wait return the average wait time for testing
        self.mock_screen.humanized_wait.side_effect = lambda min_val, max_val: (min_val + max_val) / 2
        
        # Create mock logger
        self.mock_logger = MagicMock()
        
        # Patch logger
        self.logger_patcher = patch('gravrokbot.core.action_workflow.logging.getLogger')
        self.logger_patcher.start().return_value = self.mock_logger
        
        # Create a test class that implements ActionWorkflow
        class TestActionWithDelays(ActionWorkflow):
            def __init__(self, screen, config):
                super().__init__("Test Action", screen, config)
                
                # Add a test callback method
                self.test_callback_called = False
                
            def setup_transitions(self):
                self.add_transition_with_delays(
                    'test_transition', 'idle', 'detecting', 
                    pre_delay_min=1.0, pre_delay_max=2.0,
                    post_delay_min=3.0, post_delay_max=4.0,
                    after='on_test_callback'
                )
                
                self.add_transition_with_delays(
                    'no_delay_transition', 'detecting', 'clicking',
                    after='on_test_callback'
                )
                
            def on_test_callback(self):
                self.test_callback_called = True
        
        # Create the test action
        self.test_action = TestActionWithDelays(self.mock_screen, self.config)
    
    def tearDown(self):
        """Clean up after test case"""
        self.logger_patcher.stop()
    
    def test_transition_with_delays(self):
        """Test transitions with pre and post delays"""
        # Trigger the transition
        self.test_action.test_transition()
        
        # Verify pre-delay was applied
        self.mock_screen.humanized_wait.assert_any_call(1.0, 2.0)
        
        # Verify the callback was called
        self.assertTrue(self.test_action.test_callback_called)
        
        # Verify post-delay was applied
        self.mock_screen.humanized_wait.assert_any_call(3.0, 4.0)
        
        # Verify the correct number of calls to humanized_wait
        self.assertEqual(self.mock_screen.humanized_wait.call_count, 2)
        
        # Verify the state was changed
        self.assertEqual(self.test_action.state, 'detecting')
    
    def test_transition_without_delays(self):
        """Test transitions without delays"""
        # Set initial state
        self.test_action.test_transition()
        
        # Reset mocks and callback flag
        self.mock_screen.reset_mock()
        self.test_action.test_callback_called = False
        
        # Trigger the no-delay transition
        self.test_action.no_delay_transition()
        
        # Verify the callback was called
        self.assertTrue(self.test_action.test_callback_called)
        
        # Verify no delays were applied
        self.assertEqual(self.mock_screen.humanized_wait.call_count, 0)
        
        # Verify the state was changed
        self.assertEqual(self.test_action.state, 'clicking')
    
    def test_add_transition_parameters(self):
        """Test that all parameters are correctly passed to the state machine"""
        # Create a subclass for testing parameter passing
        class TestActionParams(ActionWorkflow):
            def setup_transitions(self):
                # Store the original add_transition method for verification
                self.original_add_transition = self.machine.add_transition
                
                # Mock it for testing
                self.machine.add_transition = MagicMock()
                
                # Call our method with various parameters
                self.add_transition_with_delays(
                    'test', 'idle', 'detecting',
                    pre_delay_min=1.0, pre_delay_max=2.0,
                    post_delay_min=3.0, post_delay_max=4.0,
                    conditions=['test_condition'],
                    unless=['test_unless'],
                    before='test_before',
                    after='test_after',
                    prepare='test_prepare'
                )
        
        # Create the test action
        test_action = TestActionParams(self.mock_screen, self.config)
        
        # Verify that add_transition was called with the correct parameters
        test_action.machine.add_transition.assert_called_once()
        args, kwargs = test_action.machine.add_transition.call_args
        
        self.assertEqual(kwargs['trigger'], 'test')
        self.assertEqual(kwargs['source'], 'idle')
        self.assertEqual(kwargs['dest'], 'detecting')
        self.assertEqual(kwargs['conditions'], ['test_condition'])
        self.assertEqual(kwargs['unless'], ['test_unless'])
        self.assertEqual(kwargs['before'], 'test_before')
        self.assertEqual(kwargs['prepare'], 'test_prepare')
        # The after parameter should be modified to our wrapper
        self.assertNotEqual(kwargs['after'], 'test_after')
        self.assertTrue(kwargs['after'].startswith('_delayed_wrapper_'))

if __name__ == '__main__':
    unittest.main() 