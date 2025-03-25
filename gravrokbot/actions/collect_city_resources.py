import os
import time
import logging
from gravrokbot.core.action_workflow import ActionWorkflow

class CollectCityResourcesAction(ActionWorkflow):
    """Action to collect city resources in Rise of Kingdoms game"""
    
    def __init__(self, screen_interaction, config):
        """
        Initialize collect city resources action
        
        Args:
            screen_interaction (ScreenInteraction): Screen interaction instance
            config (dict): Configuration dict with action settings
        """
        super().__init__("Collect City Resources", screen_interaction, config)
    
    def setup_transitions(self):
        """Setup collect city resources specific transitions"""
        # Define our workflow as a sequence of transitions with delays
        self.add_transition_with_delays(
            'check_city_view', 'starting', 'detecting', 
            pre_delay_min=0.5, pre_delay_max=1.0,  # Delay before checking city view
            post_delay_min=0.5, post_delay_max=0.8,  # Delay after checking
            after='on_check_city_view'
        )
        
        self.add_transition_with_delays(
            'find_collect_button', 'detecting', 'clicking', 
            pre_delay_min=0.3, pre_delay_max=0.6,  # Delay before finding collect button
            post_delay_min=0.8, post_delay_max=1.2,  # Delay after finding
            after='on_find_collect_button'
        )
        
        self.add_transition_with_delays(
            'verify_collection', 'clicking', 'verifying', 
            pre_delay_min=1.0, pre_delay_max=1.5,  # Delay before verification (wait for animation)
            post_delay_min=0.5, post_delay_max=0.8,  # Delay after verification
            after='on_verify_collection'
        )
        
        self.add_transition_with_delays(
            'finish_collection', 'verifying', 'succeeded', 
            pre_delay_min=0.3, pre_delay_max=0.5,  # Delay before finishing
            conditions=['is_collection_successful'], 
            after='on_success'
        )
        
        # Add failure path
        self.add_transition_with_delays(
            'finish_collection', 'verifying', 'failed', 
            pre_delay_min=0.3, pre_delay_max=0.5,  # Delay before finishing
            unless=['is_collection_successful'], 
            after='on_failure'
        )
        
        # Add manual collection fallback if collect all button isn't found
        self.add_transition_with_delays(
            'collect_individually', 'clicking', 'detecting', 
            pre_delay_min=0.5, pre_delay_max=1.0,  # Delay before starting individual collection
            post_delay_min=0.5, post_delay_max=1.0,  # Delay after individual collection
            after='on_collect_individually'
        )
    
    def on_start(self):
        """Start collecting city resources"""
        self.logger.info("Starting collect city resources action")
        self.check_city_view()
    
    def on_check_city_view(self):
        """Check if we're in city view"""
        self.logger.info("Checking if we're in city view")
        
        # Get city view image path from config
        city_view_image = self.config['images']['city_view']
        
        # Make sure the image path is absolute
        if not os.path.isabs(city_view_image):
            city_view_image = os.path.join(os.path.dirname(os.path.dirname(__file__)), city_view_image)
        
        # Check if we're in city view
        if self.screen.find_image(city_view_image):
            self.logger.info("We're in city view")
            self.find_collect_button()
        else:
            self.logger.warning("Not in city view, trying to find city button")
            # TODO: Implement finding and clicking city button
            # For now, just fail
            self.fail()
    
    def on_find_collect_button(self):
        """Find and click the collect all button"""
        self.logger.info("Looking for collect all button")
        
        # Get collect all button path from config
        collect_all_button = self.config['images']['collect_all']
        
        # Make sure the image path is absolute
        if not os.path.isabs(collect_all_button):
            collect_all_button = os.path.join(os.path.dirname(os.path.dirname(__file__)), collect_all_button)
        
        # Find and click the collect all button
        if self.screen.find_and_click_image(collect_all_button):
            self.logger.info("Clicked collect all button")
            self.verify_collection()
        else:
            self.logger.warning("Could not find collect all button, trying individual collection")
            self.collect_individually()
    
    def on_collect_individually(self):
        """Collect resources by clicking each building individually"""
        self.logger.info("Collecting resources from individual buildings")
        
        # Get resource buildings paths from config
        resource_buildings = self.config['images']['resource_buildings']
        
        clicked_count = 0
        
        # Loop through each building type
        for building_img in resource_buildings:
            # Make sure the image path is absolute
            if not os.path.isabs(building_img):
                building_img = os.path.join(os.path.dirname(os.path.dirname(__file__)), building_img)
            
            # Find all instances of this building
            self.logger.info(f"Looking for buildings of type: {os.path.basename(building_img)}")
            building_locations = self.screen.find_all_images(building_img)
            
            # Click on each building
            for location in building_locations:
                self.logger.info(f"Clicking building at {location}")
                self.screen.humanized_click(*location)
                self.screen.humanized_wait(0.5, 0.8)  # Short delay between building clicks
                clicked_count += 1
        
        if clicked_count > 0:
            self.logger.info(f"Clicked {clicked_count} resource buildings")
            self.verify_collection()
        else:
            self.logger.error("Could not find any resource buildings")
            self.fail()
    
    def on_verify_collection(self):
        """Verify resource collection was successful"""
        self.logger.info("Verifying resource collection")
        
        # Finish the action
        self.finish_collection()
    
    def is_collection_successful(self):
        """
        Check if resource collection was successful
        
        Returns:
            bool: True if collection was successful, False otherwise
        """
        # Get confirmation image path from config
        confirmation_image = self.config['images']['confirmation']
        
        # Make sure the image path is absolute
        if not os.path.isabs(confirmation_image):
            confirmation_image = os.path.join(os.path.dirname(os.path.dirname(__file__)), confirmation_image)
        
        # This could also just return True, as there might not be a specific indicator of success
        # For now, we'll check for a confirmation image, but this might need adjustment
        success = self.screen.find_image(confirmation_image) is not None
        
        # If no confirmation image is defined, assume success
        if not os.path.exists(confirmation_image):
            self.logger.warning("No confirmation image defined, assuming success")
            return True
            
        return success
    
    def on_success(self):
        """Handle successful resource collection"""
        self.logger.info("Successfully collected city resources")
        self.complete()
    
    def on_failure(self):
        """Handle failed resource collection"""
        self.logger.warning("Failed to collect city resources")
        super().on_failure() 