# gravrokbot/testing/ui_tester.py
import os
import sys
import time
import logging
import json
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QTextEdit, QLabel, 
                            QProgressBar, QComboBox)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QThread
from pathlib import Path

class ActionWorkerThread(QThread):
    """Worker thread to run actions without blocking UI"""
    progress = pyqtSignal(str)
    action_complete = pyqtSignal()
    
    def __init__(self, action):
        super().__init__()
        self.action = action
        
    def run(self):
        try:
            self.action.start()
            while not self.action.is_complete():
                self.progress.emit(f"Current state: {self.action.state}")
                time.sleep(0.1)
            self.action_complete.emit()
        except Exception as e:
            self.progress.emit(f"Error: {str(e)}")

class UITester(QMainWindow):
    """Test interface for GravRokBot actions"""
    
    def __init__(self, screen_interaction, config):
        super().__init__()
        self.screen_interaction = screen_interaction
        self.config = config
        self.action_thread = None
        self.setup_ui()
        
    def setup_ui(self):
        self.setWindowTitle("GravRokBot Tester")
        self.setGeometry(100, 100, 800, 600)
        
        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QHBoxLayout(main_widget)
        
        # Left panel for controls
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # Action selector
        self.action_combo = QComboBox()
        self.action_combo.addItems([
            "Gather Resources",
            "Collect City Resources",
            "Change Character",
            "Close Game",
            "Start Game"
        ])
        left_layout.addWidget(QLabel("Select Action:"))
        left_layout.addWidget(self.action_combo)
        
        # Timing visualization
        self.timing_label = QLabel("Last Action Timing:")
        left_layout.addWidget(self.timing_label)
        
        self.timing_display = QTextEdit()
        self.timing_display.setReadOnly(True)
        self.timing_display.setMaximumHeight(100)
        left_layout.addWidget(self.timing_display)
        
        # Current state
        self.state_label = QLabel("Current State: Idle")
        left_layout.addWidget(self.state_label)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        left_layout.addWidget(self.progress_bar)
        
        # Control buttons
        button_layout = QHBoxLayout()
        
        self.start_button = QPushButton("Start Action")
        self.start_button.clicked.connect(self.start_action)
        button_layout.addWidget(self.start_button)
        
        self.stop_button = QPushButton("Stop")
        self.stop_button.clicked.connect(self.stop_action)
        self.stop_button.setEnabled(False)
        button_layout.addWidget(self.stop_button)
        
        left_layout.addLayout(button_layout)
        
        # Add spacer
        left_layout.addStretch()
        
        # Right panel for logs
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        right_layout.addWidget(QLabel("Action Logs:"))
        right_layout.addWidget(self.log_display)
        
        # Add panels to main layout
        layout.addWidget(left_panel, stretch=1)
        layout.addWidget(right_panel, stretch=2)
        
        # Setup logging handler
        self.log_handler = QTextEditLogger(self.log_display)
        self.log_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        ))
        logging.getLogger().addHandler(self.log_handler)
        logging.getLogger().setLevel(logging.DEBUG)
        
    def start_action(self):
        """Start the selected action"""
        action_name = self.action_combo.currentText()
        action = None
        
        try:
            # Create appropriate action instance
            if action_name == "Gather Resources":
                from gravrokbot.actions.gather_resources import GatherResourcesAction
                action = GatherResourcesAction(self.screen_interaction, self.config['actions']['gather_resources'])
            elif action_name == "Collect City Resources":
                from gravrokbot.actions.collect_city_resources import CollectCityResourcesAction
                action = CollectCityResourcesAction(self.screen_interaction, self.config['actions']['collect_city_resources'])
            elif action_name == "Change Character":
                from gravrokbot.actions.change_character import ChangeCharacterAction
                action = ChangeCharacterAction(self.screen_interaction, self.config['actions']['change_character'])
            elif action_name == "Close Game":
                from gravrokbot.actions.close_game import CloseGameAction
                action = CloseGameAction(self.screen_interaction, self.config['actions']['close_game'])
            elif action_name == "Start Game":
                from gravrokbot.actions.start_game import StartGameAction
                action = StartGameAction(self.screen_interaction, self.config['actions']['start_game'])
            else:
                self.log_display.append(f"Error: Unknown action {action_name}")
                return
            
            if action:
                # Create and start worker thread
                self.action_thread = ActionWorkerThread(action)
                self.action_thread.progress.connect(self.update_progress)
                self.action_thread.action_complete.connect(self.action_completed)
                
                # Update UI
                self.start_button.setEnabled(False)
                self.stop_button.setEnabled(True)
                self.progress_bar.setMaximum(0)  # Indeterminate progress
                
                # Start the action
                self.action_thread.start()
                
        except ImportError as e:
            self.log_display.append(f"Error: Could not import action module: {e}")
        except Exception as e:
            self.log_display.append(f"Error: {str(e)}")
        
    def stop_action(self):
        """Stop the current action"""
        if self.action_thread and self.action_thread.isRunning():
            self.action_thread.terminate()
            self.action_thread.wait()
            self.action_completed()
            
    def update_progress(self, message):
        """Update progress display"""
        self.state_label.setText(f"Current State: {message}")
        
    def action_completed(self):
        """Handle action completion"""
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(100)
        self.state_label.setText("Current State: Idle")
        
    def update_timing_display(self, timing_info):
        """Update timing information display"""
        self.timing_display.append(timing_info)
        
class QTextEditLogger(logging.Handler):
    """Logger that writes to QTextEdit"""
    
    def __init__(self, widget):
        super().__init__()
        self.widget = widget
        
    def emit(self, record):
        msg = self.format(record)
        self.widget.append(msg)

def main():
    """Main entry point for the UI tester"""
    from gravrokbot.core.screen_interaction import ScreenInteraction
    
    # Get the package root directory
    package_root = Path(__file__).resolve().parent.parent
    
    # Load config
    config_path = package_root / 'config' / 'default_settings.json'
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
    except Exception as e:
        logging.error(f"Error loading configuration from {config_path}: {e}")
        return 1
    
    # Create screen interaction instance
    screen_interaction = ScreenInteraction(config['screen'])
    
    # Create and show UI
    app = QApplication(sys.argv)
    tester = UITester(screen_interaction, config)
    tester.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()