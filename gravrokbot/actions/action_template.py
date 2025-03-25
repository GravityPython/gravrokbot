import os
import time
import logging
from gravrokbot.core.action_workflow import ActionWorkflow

class ActionTemplate(ActionWorkflow):
    """Template for new action classes"""
    
    def __init__(self, screen_interaction, config):
        """
        Initialize action
        
        Args:
            screen_interaction (ScreenInteraction): Screen interaction instance
            config (dict): Configuration dict with action settings
        """
        super().__init__("Action Name", screen_interaction, config)
    
    def setup_transitions(self):
        """Setup action-specific transitions"""
        # Define the workflow as a sequence of transitions with delays
        # Example:
        """
        # METHOD 1: Using predefined delay profiles
        self.add_transition_with_delays(
            'first_step', 'starting', 'detecting',
            profile='normal',  # Use the 'normal' profile for balanced delays
            after='on_first_step'
        )
        
        self.add_transition_with_delays(
            'second_step', 'detecting', 'clicking',
            profile='menu_navigation',  # Use menu_navigation profile for UI interactions
            after='on_second_step'
        )
        
        self.add_transition_with_delays(
            'third_step', 'clicking', 'verifying',
            profile='long_wait',  # Use long_wait profile when longer delays are needed
            after='on_third_step'
        )
        
        # METHOD 2: Using custom delay values
        self.add_transition_with_delays(
            'fourth_step', 'verifying', 'succeeded',
            pre_delay_min=0.5, pre_delay_max=1.0,  # Custom pre-execution delay
            post_delay_min=1.2, post_delay_max=1.8,  # Custom post-execution delay
            conditions=['is_successful'],  # Condition for success
            after='on_success'
        )
        
        # METHOD 3: Combining profiles with custom values (custom values take precedence)
        self.add_transition_with_delays(
            'fifth_step', 'verifying', 'failed',
            profile='verification',  # Use the base profile
            post_delay_min=2.0, post_delay_max=3.0,  # Override just the post-delay
            unless=['is_successful'],  # Condition for failure
            after='on_failure'
        )
        
        # Available profiles:
        # - 'quick': Short delays for simple actions (0.2-0.5s pre, 0.3-0.6s post)
        # - 'normal': Standard delays for most actions (0.5-1.0s pre, 0.8-1.2s post)
        # - 'verification': Delays for verification steps (0.5-1.0s pre, 0.2-0.4s post)
        # - 'long_wait': Longer post-delays for actions that need time (0.3-0.6s pre, 2.0-3.0s post)
        # - 'menu_navigation': Delays for menu navigation (0.3-0.7s pre, 1.0-1.5s post)
        """
        pass
    
    def on_start(self):
        """Start the action"""
        self.logger.info("Starting action")
        # Call the next transition
        # Example: self.next_step()
        # If no custom transitions defined, you can directly call success/failure
        self.succeed()
    
    # Define custom state handlers for your transitions
    # def on_first_step(self):
    #     """Handle first step state"""
    #     self.logger.debug("Processing first step")
    #     # Do something
    #     # Call the next transition
    #     self.second_step()
    
    # def on_second_step(self):
    #     """Handle second step state"""
    #     self.logger.debug("Processing second step")
    #     # Do something
    #     # Call the next transition
    #     self.third_step()
    
    # def is_successful(self):
    #     """
    #     Check if action was successful
    #     
    #     Returns:
    #         bool: True if action was successful, False otherwise
    #     """
    #     # Implement success check
    #     return True
    
    def on_success(self):
        """Handle successful action"""
        self.logger.info("Action succeeded")
        # Complete the action
        self.complete()
    
    def on_failure(self):
        """Handle failed action"""
        self.logger.warning("Action failed")
        # Let the base class handle retries
        super().on_failure() 