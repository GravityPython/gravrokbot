import os
import time
import logging
import subprocess
from gravrokbot.core.action_workflow import ActionWorkflow

class StartGameAction(ActionWorkflow):
    """Action to start Rise of Kingdoms game"""
    
    def __init__(self, screen_interaction, config):
        """
        Initialize start game action
        
        Args:
            screen_interaction (ScreenInteraction): Screen interaction instance
            config (dict): Configuration dict with action settings
        """
        super().__init__("Start Game", screen_interaction, config)
    
    def setup_transitions(self):
        """Setup start game specific transitions"""
        # Define our workflow as a sequence of transitions
        self.machine.add_transition('launch_game', 'starting', 'detecting', after='on_launch_game')
        self.machine.add_transition('find_start_button', 'detecting', 'clicking', after='on_find_start_button')
        self.machine.add_transition('wait_for_login', 'clicking', 'waiting', after='on_wait_for_login')
        self.machine.add_transition('login', 'waiting', 'verifying', after='on_login')
        self.machine.add_transition('check_game', 'verifying', 'succeeded', conditions=['is_game_started'], after='on_success')
        self.machine.add_transition('check_game', 'verifying', 'failed', unless=['is_game_started'], after='on_failure')
    
    def on_start(self):
        """Start the game"""
        self.logger.info("Starting the game action")
        self.launch_game()
    
    def on_launch_game(self):
        """Launch the game executable"""
        self.logger.info("Launching game")
        
        # Get game path from config
        game_path = self.config.get('game_path', '')
        
        if not game_path or not os.path.exists(game_path):
            self.logger.error(f"Invalid game path: {game_path}")
            self.fail()
            return
            
        try:
            # Launch the game process
            self.logger.info(f"Launching game from path: {game_path}")
            subprocess.Popen(game_path)
            
            # Wait for the game launcher to appear
            self.screen.humanized_wait(3.0, 5.0)
            self.find_start_button()
        except Exception as e:
            self.logger.error(f"Error launching game: {e}")
            self.fail()
    
    def on_find_start_button(self):
        """Find and click the start button in the launcher"""
        self.logger.info("Looking for start button")
        
        # Get start button path from config
        start_button = self.config['images']['start_button']
        
        # Make sure the image path is absolute
        if not os.path.isabs(start_button):
            start_button = os.path.join(os.path.dirname(os.path.dirname(__file__)), start_button)
        
        # Find and click the start button
        if self.screen.find_and_click_image(start_button):
            self.logger.info("Clicked start button")
            self.wait_for_login()
        else:
            # Try finding the game icon if start button isn't found
            game_icon = self.config['images']['game_icon']
            
            # Make sure the image path is absolute
            if not os.path.isabs(game_icon):
                game_icon = os.path.join(os.path.dirname(os.path.dirname(__file__)), game_icon)
                
            if self.screen.find_and_click_image(game_icon):
                self.logger.info("Clicked game icon")
                self.wait_for_login()
            else:
                self.logger.error("Could not find start button or game icon")
                self.fail()
    
    def on_wait_for_login(self):
        """Wait for the login screen to appear"""
        self.logger.info("Waiting for login screen")
        
        # Wait for the game to load
        self.screen.humanized_wait(15.0, 30.0)
        
        # Proceed to login
        self.login()
    
    def on_login(self):
        """Handle login if needed"""
        self.logger.info("Looking for login button")
        
        # Get login button path from config
        login_button = self.config['images']['login_button']
        
        # Make sure the image path is absolute
        if not os.path.isabs(login_button):
            login_button = os.path.join(os.path.dirname(os.path.dirname(__file__)), login_button)
        
        # Find and click the login button if present
        if self.screen.find_and_click_image(login_button):
            self.logger.info("Clicked login button")
            # Wait for login to complete
            self.screen.humanized_wait(5.0, 10.0)
        else:
            self.logger.info("No login button found, assuming already logged in")
        
        # Verify game started
        self.check_game()
    
    def is_game_started(self):
        """
        Check if game has successfully started
        
        Returns:
            bool: True if game is started, False otherwise
        """
        # Check for common game UI elements that indicate game is running
        # This could be checking for the city view or other game-specific elements
        
        # Get city view image from any action that might have one
        # For simplicity here, just checking settings button exists
        settings_button = self.config['images'].get('settings_button')
        if not settings_button and 'change_character' in self.config:
            settings_button = self.config['change_character']['images'].get('settings_button')
        
        if settings_button:
            # Make sure the image path is absolute
            if not os.path.isabs(settings_button):
                settings_button = os.path.join(os.path.dirname(os.path.dirname(__file__)), settings_button)
                
            # If we find settings button, game is started
            if os.path.exists(settings_button) and self.screen.find_image(settings_button):
                return True
                
        return False
    
    def on_success(self):
        """Handle successful game start"""
        self.logger.info("Successfully started the game")
        self.complete()
    
    def on_failure(self):
        """Handle failed game start"""
        self.logger.warning("Failed to start the game")
        super().on_failure() 