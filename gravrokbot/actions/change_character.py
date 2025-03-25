import os
import time
import logging
from gravrokbot.core.action_workflow import ActionWorkflow

class ChangeCharacterAction(ActionWorkflow):
    """Action to change character in Rise of Kingdoms game"""
    
    def __init__(self, screen_interaction, config):
        """
        Initialize change character action
        
        Args:
            screen_interaction (ScreenInteraction): Screen interaction instance
            config (dict): Configuration dict with action settings
        """
        super().__init__("Change Character", screen_interaction, config)
    
    def setup_transitions(self):
        """Setup change character specific transitions"""
        # Define the workflow as a sequence of transitions
        self.machine.add_transition('open_settings', 'starting', 'detecting', after='on_open_settings')
        self.machine.add_transition('open_character_menu', 'detecting', 'clicking', after='on_open_character_menu')
        self.machine.add_transition('switch_character', 'clicking', 'verifying', after='on_switch_character')
        self.machine.add_transition('check_switch', 'verifying', 'succeeded', conditions=['is_switch_successful'], after='on_success')
        self.machine.add_transition('check_switch', 'verifying', 'failed', unless=['is_switch_successful'], after='on_failure')
    
    def on_start(self):
        """Start changing character"""
        self.logger.info("Starting change character action")
        self.open_settings()
    
    def on_open_settings(self):
        """Open settings menu"""
        self.logger.info("Opening settings menu")
        
        # Get settings button path from config
        settings_button = self.config['images']['settings_button']
        
        # Make sure the image path is absolute
        if not os.path.isabs(settings_button):
            settings_button = os.path.join(os.path.dirname(os.path.dirname(__file__)), settings_button)
        
        # Find and click the settings button
        if self.screen.find_and_click_image(settings_button):
            self.logger.info("Clicked settings button")
            self.screen.humanized_wait(0.8, 1.2)
            self.open_character_menu()
        else:
            self.logger.error("Could not find settings button")
            self.fail()
    
    def on_open_character_menu(self):
        """Open character menu"""
        self.logger.info("Opening character menu")
        
        # Get character button path from config
        character_button = self.config['images']['character_button']
        
        # Make sure the image path is absolute
        if not os.path.isabs(character_button):
            character_button = os.path.join(os.path.dirname(os.path.dirname(__file__)), character_button)
        
        # Find and click the character button
        if self.screen.find_and_click_image(character_button):
            self.logger.info("Clicked character button")
            self.screen.humanized_wait(1.0, 1.5)
            self.switch_character()
        else:
            self.logger.error("Could not find character button")
            self.fail()
    
    def on_switch_character(self):
        """Switch to another character"""
        self.logger.info("Switching character")
        
        # Get switch button path from config
        switch_button = self.config['images']['switch_button']
        
        # Make sure the image path is absolute
        if not os.path.isabs(switch_button):
            switch_button = os.path.join(os.path.dirname(os.path.dirname(__file__)), switch_button)
        
        # Find and click the switch button
        if self.screen.find_and_click_image(switch_button):
            self.logger.info("Clicked switch button")
            # Wait longer for character switch
            self.screen.humanized_wait(5.0, 8.0)
            self.check_switch()
        else:
            self.logger.error("Could not find switch button")
            self.fail()
    
    def is_switch_successful(self):
        """
        Check if character switch was successful
        
        Returns:
            bool: True if character switch was successful, False otherwise
        """
        # Get confirmation image path from config
        confirmation_image = self.config['images']['confirmation']
        
        # Make sure the image path is absolute
        if not os.path.isabs(confirmation_image):
            confirmation_image = os.path.join(os.path.dirname(os.path.dirname(__file__)), confirmation_image)
        
        # Check if confirmation image is on screen
        return self.screen.find_image(confirmation_image) is not None
    
    def on_success(self):
        """Handle successful character switch"""
        self.logger.info("Successfully changed character")
        self.complete()
    
    def on_failure(self):
        """Handle failed character switch"""
        self.logger.warning("Failed to change character")
        super().on_failure() 