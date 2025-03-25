import os
import time
import logging
from gravrokbot.core.action_workflow import ActionWorkflow
from gravrokbot.core.human_timing import HumanTiming

class GatherResourcesAction(ActionWorkflow):
    """Action to gather resources in Rise of Kingdoms game"""
    
    def __init__(self, screen_interaction, config):
        """
        Initialize gather resources action
        
        Args:
            screen_interaction (ScreenInteraction): Screen interaction instance
            config (dict): Configuration dict with action settings
        """
        super().__init__("Gather Resources", screen_interaction, config)
        self.human_timing = HumanTiming()
    
    def setup_transitions(self):
        """Setup gather resources specific transitions"""
        # Define our workflow as a sequence of transitions with delays using profiles
        self.add_transition_with_delays(
            'find_resource', 'starting', 'detecting', 
            profile='normal',  # Use the 'normal' delay profile
            after='on_find_resource'
        )
        
        self.add_transition_with_delays(
            'click_gather', 'detecting', 'clicking', 
            profile='menu_navigation',  # Use menu_navigation profile for UI interactions
            after='on_click_gather'
        )
        
        self.add_transition_with_delays(
            'click_march', 'clicking', 'verifying', 
            profile='long_wait',  # Use long_wait profile for march command which needs longer delays
            after='on_click_march'
        )
        
        self.add_transition_with_delays(
            'check_success', 'verifying', 'succeeded', 
            profile='verification',  # Use verification profile for checking results
            conditions=['is_gather_successful'], 
            after='on_success'
        )
        
        # Add failure path from verify to failed
        self.add_transition_with_delays(
            'check_success', 'verifying', 'failed', 
            profile='verification',  # Use verification profile for checking results
            unless=['is_gather_successful'], 
            after='on_failure'
        )
    
    def on_start(self):
        """Start gathering resources"""
        self.logger.info("Starting gather resources action")
        self.find_resource()
    
    def on_find_resource(self):
        """Find resource on map"""
        self.logger.info("Looking for resource node on map")
        
        # Get resource icon path from config
        resource_icon = self.config['images']['resource_icon']
        
        # Make sure the image path is absolute
        if not os.path.isabs(resource_icon):
            resource_icon = os.path.join(os.path.dirname(os.path.dirname(__file__)), resource_icon)
        
        # Find the resource on screen
        resource_location = self.screen.find_image(resource_icon)
        
        if resource_location:
            self.logger.info(f"Found resource at {resource_location}")
            # Store location for later use
            self.resource_location = resource_location
            # Click on the resource
            self.screen.humanized_click(*resource_location)
            self.click_gather()
        else:
            self.logger.error("Could not find resource on map")
            self.fail()
    
    def on_click_gather(self):
        """Click gather button"""
        self.logger.info("Looking for gather button")
        
        # Get gather button path from config
        gather_button = self.config['images']['gather_button']
        
        # Make sure the image path is absolute
        if not os.path.isabs(gather_button):
            gather_button = os.path.join(os.path.dirname(os.path.dirname(__file__)), gather_button)
        
        # Click the gather button
        if self.screen.find_and_click_image(gather_button):
            self.logger.info("Clicked gather button")
            self.click_march()
        else:
            self.logger.error("Could not find gather button")
            self.fail()
    
    def on_click_march(self):
        """Click march button"""
        self.logger.info("Looking for march button")
        
        # Get march button path from config
        march_button = self.config['images']['march_button']
        
        # Make sure the image path is absolute
        if not os.path.isabs(march_button):
            march_button = os.path.join(os.path.dirname(os.path.dirname(__file__)), march_button)
        
        # Click the march button
        if self.screen.find_and_click_image(march_button):
            self.logger.info("Clicked march button")
            self.check_success()
        else:
            self.logger.error("Could not find march button")
            self.fail()
    
    def is_gather_successful(self):
        """
        Check if gather action was successful
        
        Returns:
            bool: True if gather action was successful, False otherwise
        """
        # Get confirmation image path from config
        confirmation_image = self.config['images']['confirmation']
        
        # Make sure the image path is absolute
        if not os.path.isabs(confirmation_image):
            confirmation_image = os.path.join(os.path.dirname(os.path.dirname(__file__)), confirmation_image)
        
        # Check if confirmation image is on screen
        return self.screen.find_image(confirmation_image) is not None
    
    def on_success(self):
        """Handle successful gather action"""
        self.logger.info("Successfully started gathering resources")
        # Change state to completed
        self.complete()
    
    def on_failure(self):
        """Handle failed gather action"""
        self.logger.warning("Failed to gather resources")
        # Let the base class handle retries
        super().on_failure() 