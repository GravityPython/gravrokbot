import os
import time
import logging
import json
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
        self.character_settings = {}
        self.load_character_settings()
    
    def load_character_settings(self):
        """Load character settings from file"""
        try:
            path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config", "character_settings.json")
            if os.path.exists(path):
                with open(path, 'r') as f:
                    self.character_settings = json.load(f)
        except Exception as e:
            self.logger.error(f"Error loading character settings: {e}")
            self.character_settings = {"characters": {}, "current_character": None}
    
    def save_character_settings(self):
        """Save character settings to file"""
        try:
            path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config", "character_settings.json")
            with open(path, 'w') as f:
                json.dump(self.character_settings, f, indent=4)
        except Exception as e:
            self.logger.error(f"Error saving character settings: {e}")
    
    def initialize_character_settings(self, character_name):
        """Initialize settings for a new character"""
        self.logger.info(f"Initializing settings for new character: {character_name}")
        
        # Load default settings
        default_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config", "default_settings.json")
        try:
            with open(default_path, 'r') as f:
                default_settings = json.load(f)
                
            # Create new character settings with defaults
            self.character_settings["characters"][character_name] = {
                "actions": {}
            }
            
            # Copy default action settings
            for action_key, action_config in default_settings["actions"].items():
                self.character_settings["characters"][character_name]["actions"][action_key] = {
                    "enabled": False,  # Initialize actions as disabled by default
                    "cooldown_minutes": action_config["cooldown_minutes"]
                }
                
            # Update current character
            self.character_settings["current_character"] = character_name
            
            # Save the updated settings
            self.save_character_settings()
            
            self.logger.info(f"Successfully initialized settings for {character_name}")
            
        except Exception as e:
            self.logger.error(f"Error initializing character settings: {e}")
    
    def detect_character_name(self):
        """
        Detect the current character name from the game screen
        Returns:
            str: Detected character name or None if detection fails
        """
        # TODO: Implement actual character name detection using OCR
        # For now, we'll use a placeholder that assumes we can get the name
        # This should be replaced with actual OCR implementation
        try:
            # Placeholder for OCR implementation
            # This should use self.screen.find_text() or similar to detect the name
            detected_name = "Character1"  # Replace with actual detection
            return detected_name
        except Exception as e:
            self.logger.error(f"Error detecting character name: {e}")
            return None

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
        
        # Detect the new character name
        new_character = self.detect_character_name()
        if new_character:
            self.logger.info(f"Detected character: {new_character}")
            
            # Check if this is a new character
            if new_character not in self.character_settings.get("characters", {}):
                self.logger.info(f"New character detected: {new_character}")
                self.initialize_character_settings(new_character)
            else:
                # Update current character in settings
                self.character_settings["current_character"] = new_character
                self.save_character_settings()
                
            self.logger.info(f"Character settings updated for: {new_character}")
        else:
            self.logger.warning("Could not detect character name")
            
        self.complete()
    
    def on_failure(self):
        """Handle failed character switch"""
        self.logger.warning("Failed to change character")
        super().on_failure() 