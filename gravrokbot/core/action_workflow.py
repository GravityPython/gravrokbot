import time
import logging
import functools
from transitions import Machine
from datetime import datetime, timedelta

class ActionWorkflow:
    """Base class for game action workflows using state machine"""
    
    # Define possible states for any action
    states = [
        'idle',
        'starting',
        'detecting',
        'clicking',
        'typing',
        'waiting',
        'verifying',
        'extracting_text',
        'succeeded',
        'failed',
        'completed'
    ]
    
    # Default delay profiles for common actions
    delay_profiles = {
        'quick': {
            'pre_delay_min': 0.2, 
            'pre_delay_max': 0.5,
            'post_delay_min': 0.3, 
            'post_delay_max': 0.6
        },
        'normal': {
            'pre_delay_min': 0.5, 
            'pre_delay_max': 1.0,
            'post_delay_min': 0.8, 
            'post_delay_max': 1.2
        },
        'verification': {
            'pre_delay_min': 0.5,
            'pre_delay_max': 1.0,
            'post_delay_min': 0.2, 
            'post_delay_max': 0.4
        },
        'long_wait': {
            'pre_delay_min': 0.3, 
            'pre_delay_max': 0.6,
            'post_delay_min': 2.0, 
            'post_delay_max': 3.0
        },
        'menu_navigation': {
            'pre_delay_min': 0.3, 
            'pre_delay_max': 0.7,
            'post_delay_min': 1.0, 
            'post_delay_max': 1.5
        }
    }
    
    def __init__(self, name, screen_interaction, config):
        """
        Initialize action workflow
        
        Args:
            name (str): Name of the action
            screen_interaction (ScreenInteraction): Screen interaction instance
            config (dict): Configuration dict with action settings
        """
        self.name = name
        self.screen = screen_interaction
        self.config = config
        self.logger = logging.getLogger(f"GravRokBot.{name}")
        
        # Initialize cooldown settings
        self.last_execution_time = None
        self.cooldown_minutes = self.config.get('cooldown_minutes', 30)
        self.enabled = self.config.get('enabled', True)
        self.max_retries = self.config.get('max_retries', 3)
        self.retry_count = 0
        
        # Load custom delay profiles from config if available
        self.custom_delay_profiles = self.config.get('delay_profiles', {})
        
        # Initialize state machine
        self.machine = Machine(
            model=self,
            states=self.states,
            initial='idle',
            auto_transitions=False
        )
        
        # Define basic transitions available to all actions
        self._define_common_transitions()
        
        # Action specific setup function should be called by subclasses
        self.setup_transitions()
    
    def _define_common_transitions(self):
        """Define transitions common to all actions"""
        # Basic flow transitions
        self.add_transition_with_delays('start', 'idle', 'starting', after='on_start')
        self.add_transition_with_delays('detect', 'starting', 'detecting', after='on_detect')
        self.add_transition_with_delays('click', 'detecting', 'clicking', after='on_click')
        self.add_transition_with_delays('wait', '*', 'waiting', after='on_wait')
        self.add_transition_with_delays('verify', '*', 'verifying', after='on_verify')
        self.add_transition_with_delays('extract_text', '*', 'extracting_text', after='on_extract_text')
        
        # Success/failure transitions
        self.add_transition_with_delays('succeed', '*', 'succeeded', after='on_success')
        self.add_transition_with_delays('fail', '*', 'failed', after='on_failure')
        self.add_transition_with_delays('complete', ['succeeded', 'failed'], 'completed', after='on_complete')
        
        # Reset transition
        self.add_transition_with_delays('reset', '*', 'idle', after='on_reset')
    
    def get_delay_profile(self, profile_name):
        """
        Get delay profile by name
        
        Args:
            profile_name (str): Name of the delay profile
            
        Returns:
            dict: Delay profile settings
        """
        # First check custom profiles from config
        if profile_name in self.custom_delay_profiles:
            return self.custom_delay_profiles[profile_name]
        
        # Then check built-in profiles
        if profile_name in self.delay_profiles:
            return self.delay_profiles[profile_name]
        
        # Return empty dict if not found
        self.logger.warning(f"Delay profile '{profile_name}' not found")
        return {}
    
    def add_transition_with_delays(self, trigger, source, dest, profile=None, 
                                 pre_delay_min=0, pre_delay_max=0,
                                 post_delay_min=0, post_delay_max=0, 
                                 conditions=None, unless=None,
                                 before=None, after=None, prepare=None):
        """
        Add a transition with configurable pre and post delays
        
        Args:
            trigger (str): The name of the trigger
            source (str or list): Source state(s)
            dest (str): Destination state
            profile (str, optional): Name of a predefined delay profile
            pre_delay_min (float): Minimum delay before executing the transition (seconds)
            pre_delay_max (float): Maximum delay before executing the transition (seconds)
            post_delay_min (float): Minimum delay after executing the transition (seconds)
            post_delay_max (float): Maximum delay after executing the transition (seconds)
            conditions (str or list): Condition(s) that must be met for the transition
            unless (str or list): Condition(s) that must NOT be met for the transition
            before (str or list): Callbacks to execute before the transition
            after (str or list): Callbacks to execute after the transition
            prepare (str or list): Callbacks to execute when the trigger is activated
        """
        # Apply delay profile if specified
        if profile:
            delay_settings = self.get_delay_profile(profile)
            
            # Only override if not explicitly specified
            if pre_delay_min == 0 and pre_delay_max == 0:
                pre_delay_min = delay_settings.get('pre_delay_min', 0)
                pre_delay_max = delay_settings.get('pre_delay_max', 0)
                
            if post_delay_min == 0 and post_delay_max == 0:
                post_delay_min = delay_settings.get('post_delay_min', 0)
                post_delay_max = delay_settings.get('post_delay_max', 0)
        
        if after is not None:
            # If we have an after callback, wrap it with delays
            original_after = after
            
            # Create a wrapper function that adds delays
            def delayed_after_wrapper(self, *args, **kwargs):
                # Pre-delay
                if pre_delay_min > 0 or pre_delay_max > 0:
                    delay_time = self.screen.humanized_wait(pre_delay_min, pre_delay_max)
                    self.logger.debug(f"Pre-delay: {delay_time:.2f}s before {original_after}")
                
                # Call the original after callback
                # Get the method from the instance
                after_method = getattr(self, original_after)
                after_method(*args, **kwargs)
                
                # Post-delay
                if post_delay_min > 0 or post_delay_max > 0:
                    delay_time = self.screen.humanized_wait(post_delay_min, post_delay_max)
                    self.logger.debug(f"Post-delay: {delay_time:.2f}s after {original_after}")
            
            # Dynamically create a method name for the wrapper
            wrapper_name = f"_delayed_wrapper_{original_after}"
            setattr(self.__class__, wrapper_name, delayed_after_wrapper)
            
            # Use the wrapper as the new after callback
            after = wrapper_name
        
        # Add the transition with potentially modified after callback
        self.machine.add_transition(
            trigger=trigger,
            source=source,
            dest=dest,
            conditions=conditions,
            unless=unless,
            before=before,
            after=after,
            prepare=prepare
        )
    
    def setup_transitions(self):
        """
        Setup action-specific transitions
        
        This method should be implemented by subclasses
        """
        pass
    
    def execute(self):
        """
        Execute the action workflow
        
        Returns:
            bool: True if action was executed, False if on cooldown
        """
        # Check if action is enabled
        if not self.enabled:
            self.logger.info(f"Action '{self.name}' is disabled, skipping")
            return False
        
        # Check cooldown
        if self.last_execution_time:
            elapsed_minutes = (datetime.now() - self.last_execution_time).total_seconds() / 60
            if elapsed_minutes < self.cooldown_minutes:
                self.logger.info(f"Action '{self.name}' on cooldown for another {self.cooldown_minutes - elapsed_minutes:.1f} minutes")
                return False
        
        self.logger.info(f"Executing action: {self.name}")
        self.start()
        
        # Record execution time
        self.last_execution_time = datetime.now()
        
        return True
    
    # These are placeholder methods to be overridden by subclasses
    def on_start(self):
        """Handle starting state"""
        self.logger.debug("Action starting")
    
    def on_detect(self):
        """Handle object detection state"""
        self.logger.debug("Detecting objects")
    
    def on_click(self):
        """Handle clicking state"""
        self.logger.debug("Clicking detected object")
    
    def on_wait(self):
        """Handle waiting state"""
        wait_time = self.config.get('default_wait_time', 1.0)
        self.screen.humanized_wait(wait_time * 0.8, wait_time * 1.2)
    
    def on_verify(self):
        """Handle verification state"""
        self.logger.debug("Verifying action")
    
    def on_extract_text(self):
        """Handle text extraction state"""
        self.logger.debug("Extracting text from screen")
    
    def on_success(self):
        """Handle success state"""
        self.logger.info(f"Action '{self.name}' succeeded")
        self.retry_count = 0
    
    def on_failure(self):
        """Handle failure state"""
        self.retry_count += 1
        self.logger.warning(f"Action '{self.name}' failed (attempt {self.retry_count}/{self.max_retries})")
        
        if self.retry_count < self.max_retries:
            self.logger.info(f"Retrying action '{self.name}'")
            self.reset()
            self.start()
        else:
            self.logger.error(f"Action '{self.name}' failed after {self.max_retries} attempts")
            self.complete()
    
    def on_complete(self):
        """Handle completion state"""
        self.logger.debug(f"Action '{self.name}' completed")
    
    def on_reset(self):
        """Handle reset state"""
        self.logger.debug(f"Action '{self.name}' reset")
        
    def is_on_cooldown(self):
        """
        Check if action is currently on cooldown
        
        Returns:
            bool: True if action is on cooldown, False otherwise
        """
        if not self.last_execution_time:
            return False
            
        elapsed_minutes = (datetime.now() - self.last_execution_time).total_seconds() / 60
        return elapsed_minutes < self.cooldown_minutes
    
    def get_cooldown_remaining(self):
        """
        Get remaining cooldown time in minutes
        
        Returns:
            float: Remaining cooldown time in minutes, 0 if not on cooldown
        """
        if not self.last_execution_time:
            return 0
            
        elapsed_minutes = (datetime.now() - self.last_execution_time).total_seconds() / 60
        remaining = max(0, self.cooldown_minutes - elapsed_minutes)
        return remaining 