import os
import time
import logging
from gravrokbot.core.action_workflow import ActionWorkflow

class CloseGameAction(ActionWorkflow):
    """Action to close Rise of Kingdoms game"""
    
    def __init__(self, screen_interaction, config):
        """
        Initialize close game action
        
        Args:
            screen_interaction (ScreenInteraction): Screen interaction instance
            config (dict): Configuration dict with action settings
        """
        super().__init__("Close Game", screen_interaction, config)
    
    def setup_transitions(self):
        """Setup close game specific transitions"""
        # Define our workflow as a sequence of transitions
        self.machine.add_transition('open_settings', 'starting', 'detecting', after='on_open_settings')
        self.machine.add_transition('find_exit_button', 'detecting', 'clicking', after='on_find_exit_button')
        self.machine.add_transition('confirm_exit', 'clicking', 'verifying', after='on_confirm_exit')
        self.machine.add_transition('check_exit', 'verifying', 'succeeded', conditions=['is_game_closed'], after='on_success')
        self.machine.add_transition('check_exit', 'verifying', 'failed', unless=['is_game_closed'], after='on_failure')
    
    def on_start(self):
        """Start closing game"""
        self.logger.info("Starting close game action")
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
            self.find_exit_button()
        else:
            self.logger.error("Could not find settings button")
            self.fail()
    
    def on_find_exit_button(self):
        """Find and click exit button"""
        self.logger.info("Looking for exit button")
        
        # Get exit button path from config
        exit_button = self.config['images']['exit_button']
        
        # Make sure the image path is absolute
        if not os.path.isabs(exit_button):
            exit_button = os.path.join(os.path.dirname(os.path.dirname(__file__)), exit_button)
        
        # Find and click the exit button
        if self.screen.find_and_click_image(exit_button):
            self.logger.info("Clicked exit button")
            self.screen.humanized_wait(0.8, 1.2)
            self.confirm_exit()
        else:
            self.logger.error("Could not find exit button")
            self.fail()
    
    def on_confirm_exit(self):
        """Confirm exit in dialog"""
        self.logger.info("Looking for exit confirmation dialog")
        
        # Get confirmation image path from config
        confirmation_image = self.config['images']['confirmation']
        
        # Make sure the image path is absolute
        if not os.path.isabs(confirmation_image):
            confirmation_image = os.path.join(os.path.dirname(os.path.dirname(__file__)), confirmation_image)
        
        # Find the confirmation dialog and click yes/confirm
        if self.screen.find_and_click_image(confirmation_image):
            self.logger.info("Clicked exit confirmation")
            # Wait longer for game to close
            self.screen.humanized_wait(5.0, 8.0)
            self.check_exit()
        else:
            self.logger.error("Could not find exit confirmation dialog")
            self.fail()
    
    def is_game_closed(self):
        """
        Check if game is closed
        
        Returns:
            bool: True if game is closed, False otherwise
        """
        # This can be tricky to determine - one approach is to look for elements that
        # should be present when the game is running
        for key, img_path in self.config['images'].items():
            if key != 'confirmation':  # Don't check confirmation image itself
                # Make sure the image path is absolute
                if not os.path.isabs(img_path):
                    img_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), img_path)
                
                # If we find any game element, it's not closed
                if os.path.exists(img_path) and self.screen.find_image(img_path):
                    return False
        
        # If we can't find any game elements, assume it's closed
        return True
    
    def on_success(self):
        """Handle successful game closure"""
        self.logger.info("Successfully closed the game")
        self.complete()
    
    def on_failure(self):
        """Handle failed game closure"""
        self.logger.warning("Failed to close the game")
        super().on_failure() 