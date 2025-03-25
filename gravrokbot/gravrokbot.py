#!/usr/bin/env python3
"""
GravRokBot - Rise of Kingdoms Automation Bot

This application automates interactions with the Rise of Kingdoms game
using computer vision and simulated human-like inputs.
"""

import os
import sys
import json
import logging
import colorlog
from PyQt6.QtWidgets import QApplication, QTreeWidgetItem
from PyQt6.QtCore import Qt

# Add package to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gravrokbot.ui.main_window import MainWindow
from gravrokbot.core.screen_interaction import ScreenInteraction
from gravrokbot.core.action_runner import ActionRunner
from gravrokbot.actions.gather_resources import GatherResourcesAction
from gravrokbot.actions.collect_city_resources import CollectCityResourcesAction
from gravrokbot.actions.change_character import ChangeCharacterAction
from gravrokbot.actions.close_game import CloseGameAction
from gravrokbot.actions.start_game import StartGameAction

# Configure logger
def setup_logger():
    """Configure the application logger"""
    logger = logging.getLogger("GravRokBot")
    logger.setLevel(logging.DEBUG)
    
    # Console handler with colors
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    
    # Color formatter
    color_formatter = colorlog.ColoredFormatter(
        "%(log_color)s[%(asctime)s] %(levelname)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red,bg_white',
        }
    )
    console_handler.setFormatter(color_formatter)
    
    # File handler
    os.makedirs("logs", exist_ok=True)
    file_handler = logging.FileHandler("logs/gravrokbot.log")
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter("[%(asctime)s] %(levelname)s: %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
    file_handler.setFormatter(file_formatter)
    
    # Add handlers
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    return logger

def load_config():
    """
    Load configuration from JSON file
    
    Returns:
        dict: Configuration dictionary
    """
    config_path = os.path.join(os.path.dirname(__file__), "config", "default_settings.json")
    user_config_path = os.path.join(os.path.dirname(__file__), "config", "settings.json")
    
    # Load default config
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    # Merge with user config if exists
    if os.path.exists(user_config_path):
        try:
            with open(user_config_path, 'r') as f:
                user_config = json.load(f)
                
            # Recursive merge function
            def merge_dicts(d1, d2):
                for k, v in d2.items():
                    if k in d1 and isinstance(d1[k], dict) and isinstance(v, dict):
                        merge_dicts(d1[k], v)
                    else:
                        d1[k] = v
            
            merge_dicts(config, user_config)
        except Exception as e:
            logger.error(f"Error loading user config: {e}")
    
    return config

def initialize_bot(config):
    """
    Initialize bot components
    
    Args:
        config (dict): Configuration dictionary
        
    Returns:
        tuple: (ScreenInteraction, ActionRunner) instances
    """
    # Initialize screen interaction
    screen = ScreenInteraction(config['screen'])
    
    # Initialize action runner
    runner = ActionRunner(config['runner'])
    
    # Create and add actions
    if 'gather_resources' in config['actions']:
        gather_action = GatherResourcesAction(screen, config['actions']['gather_resources'])
        runner.add_action(gather_action)
    
    if 'collect_city_resources' in config['actions']:
        collect_action = CollectCityResourcesAction(screen, config['actions']['collect_city_resources'])
        runner.add_action(collect_action)
    
    if 'change_character' in config['actions']:
        change_character_action = ChangeCharacterAction(screen, config['actions']['change_character'])
        runner.add_action(change_character_action)
    
    if 'close_game' in config['actions']:
        close_game_action = CloseGameAction(screen, config['actions']['close_game'])
        runner.add_action(close_game_action)
    
    if 'start_game' in config['actions']:
        start_game_action = StartGameAction(screen, config['actions']['start_game'])
        runner.add_action(start_game_action)
    
    return screen, runner

def connect_ui_to_bot(window, screen, runner):
    """
    Connect UI elements to bot actions
    
    Args:
        window (MainWindow): Main UI window
        screen (ScreenInteraction): Screen interaction instance
        runner (ActionRunner): Action runner instance
    """
    # Connect start/stop buttons
    window.start_button.clicked.connect(runner.start)
    window.stop_button.clicked.connect(runner.stop)
    
    # Connect action checkboxes to enable/disable actions
    for action_name, checkbox in window.action_checkboxes.items():
        # Find matching action
        for action in runner.actions:
            if action.name.lower().replace(" ", "_") == action_name:
                # Connect checkbox to action
                checkbox.setChecked(action.enabled)
                checkbox.stateChanged.connect(lambda state, a=action: setattr(a, 'enabled', state == Qt.CheckState.Checked.value))
    
    # Connect status updates
    def update_action_status():
        """Update action status in UI"""
        window.action_tree.clear()
        
        for status in runner.get_action_statuses():
            item = QTreeWidgetItem([
                status['name'],
                status['state'].capitalize(),
                f"{status['cooldown_remaining']:.1f} min" if status['on_cooldown'] else "Ready"
            ])
            window.action_tree.addTopLevelItem(item)
    
    # Connect timer to status update
    window.update_timer.timeout.connect(update_action_status)
    
    # Connect logging
    class UILogHandler(logging.Handler):
        """Custom log handler to send logs to the UI"""
        def emit(self, record):
            window.log_display.append_log(record.levelname, record.getMessage())
    
    # Add UI log handler to logger
    ui_handler = UILogHandler()
    ui_handler.setLevel(logging.INFO)
    logging.getLogger("GravRokBot").addHandler(ui_handler)
    
    # Connect UI settings with bot settings
    def apply_settings():
        """Apply UI settings to bot configuration"""
        # Runner settings
        runner.refresh_rate_seconds = window.refresh_rate.value()
        runner.continuous_running = window.continuous_running.isChecked()
        runner.night_sleep_enabled = window.night_sleep.isChecked()
        runner.night_sleep_start = window.night_start.time().toString("HH:mm")
        runner.night_sleep_end = window.night_end.time().toString("HH:mm")
        runner.coffee_break_min_minutes = window.coffee_min.value()
        runner.coffee_break_max_minutes = window.coffee_max.value()
        runner.coffee_break_chance = window.coffee_chance.value() / 100.0
        
        # TODO: Add more settings as needed
    
    # Connect apply settings button
    window.save_settings = apply_settings

def main():
    """Main application entry point"""
    # Setup logger
    global logger
    logger = setup_logger()
    
    logger.info("Starting GravRokBot")
    
    # Load configuration
    try:
        config = load_config()
        logger.info("Configuration loaded")
    except Exception as e:
        logger.critical(f"Error loading configuration: {e}")
        return 1
    
    # High DPI support
    QApplication.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)
    
    # Create application
    app = QApplication(sys.argv)
    app.setApplicationName("GravRokBot")
    
    # Initialize bot
    try:
        screen, runner = initialize_bot(config)
        logger.info("Bot components initialized")
    except Exception as e:
        logger.critical(f"Error initializing bot: {e}")
        return 1
    
    # Create main window
    window = MainWindow()
    
    # Connect UI to bot
    connect_ui_to_bot(window, screen, runner)
    
    # Show window
    window.show()
    
    # Run application
    return app.exec()

if __name__ == "__main__":
    sys.exit(main()) 