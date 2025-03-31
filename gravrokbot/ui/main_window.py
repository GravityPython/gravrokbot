"""
Main window UI for GravRokBot using ttkbootstrap.
"""

import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from datetime import datetime, timedelta
import sys
import os
import logging
import json

class MainWindow:
    def __init__(self):
        # Define status types and their styles
        self.ACTION_STATUSES = {
            "N/A": "secondary-inverse",  # Gray background
            "Waiting": "warning-inverse",  # Orange background
            "Working": "info-inverse",    # Blue background
            "Done": "success-inverse"     # Green background
        }
        
        self.root = ttk.Window(
            title="Rise of Kingdoms Bot 1.0.0",
            themename="darkly",
            size=(1200, 800),
            position=(100, 100)
        )
        
        # Configure logging
        self.logger = logging.getLogger('gravrokbot')
        
        # Initialize character settings
        self.character_settings = {}
        self.current_character = None
        
        # Load default settings
        self.load_default_settings()
        
        # Load character settings
        self.load_character_settings()
        
        # Load cooldown states
        self.load_cooldown_states()
        
        # Create main container
        self.main_container = ttk.Frame(self.root)
        self.main_container.pack(fill=BOTH, expand=True, padx=5, pady=5)
        
        # Create header
        self.create_header()
        
        # Create main content
        self.create_main_content()
        
        # Create bottom status bar
        self.create_status_bar()
        
        # Initialize bot status
        self.running = False
        
        # Track selected action
        self.selected_action = None
        
        # Register cleanup handler
        self.root.protocol("WM_DELETE_WINDOW", self.cleanup_and_exit)
        
        # Start cooldown update timer using refresh rate from settings
        refresh_rate = self.settings["runner"]["refresh_rate_seconds"] * 1000  # Convert to milliseconds
        self.root.after(refresh_rate, self.update_cooldowns)
        
    def load_default_settings(self):
        """Load settings from file, falling back to defaults if needed"""
        try:
            # First load default settings
            default_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config", "default_settings.json")
            with open(default_path, 'r') as f:
                self.settings = json.load(f)
                
            # Then try to load and merge user settings
            settings_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config", "settings.json")
            if os.path.exists(settings_path):
                with open(settings_path, 'r') as f:
                    user_settings = json.load(f)
                    
                # Recursive merge function
                def merge_dicts(base, override):
                    for key, value in override.items():
                        if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                            merge_dicts(base[key], value)
                        else:
                            base[key] = value
                            
                # Merge user settings into default settings
                merge_dicts(self.settings, user_settings)
                    
        except Exception as e:
            self.logger.error(f"Error loading settings: {e}")
            # Fallback to hardcoded defaults if both files fail
            self.settings = {
                "runner": {
                    "refresh_rate_seconds": 60,
                    "continuous_running": True,
                    "night_sleep_enabled": True,
                    "night_sleep_start": "23:00",
                    "night_sleep_end": "07:00",
                    "coffee_break_min_minutes": 10,
                    "coffee_break_max_minutes": 30,
                    "coffee_break_chance": 0.05,
                    "min_break_interval_minutes": 120,
                    "character_switch": {
                        "enabled": True,
                        "min_seconds": 1800,
                        "max_seconds": 3600
                    }
                }
            }
        
    def load_character_settings(self):
        """Load character-specific settings"""
        try:
            path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config", "character_settings.json")
            if os.path.exists(path):
                with open(path, 'r') as f:
                    self.character_settings = json.load(f)
                    
                # Validate current character
                self.current_character = self.character_settings.get("current_character")
                if self.current_character not in self.character_settings.get("characters", {}):
                    # If current character is invalid, use the first available character
                    available_characters = list(self.character_settings.get("characters", {}).keys())
                    self.current_character = available_characters[0] if available_characters else None
                    self.character_settings["current_character"] = self.current_character
                    
                # Apply settings for current character
                self.apply_character_settings()
            else:
                # Create default settings for first character
                self.initialize_character_settings()
        except Exception as e:
            self.logger.error(f"Error loading character settings: {e}")
            # If there's an error, initialize with defaults
            self.initialize_character_settings()

    def initialize_character_settings(self):
        """Create default settings for first character"""
        self.character_settings = {
            "characters": {
                "Character1": {
                    "actions": {}
                }
            },
            "current_character": "Character1"
        }
        
        # Copy default action settings
        for action_key, action_config in self.settings["actions"].items():
            self.character_settings["characters"]["Character1"]["actions"][action_key] = {
                "enabled": False,  # Initialize actions as disabled by default
                "cooldown_minutes": action_config["cooldown_minutes"]
            }
            
        self.current_character = "Character1"
        self.save_character_settings()
        
        # Apply the settings
        self.apply_character_settings()

    def save_character_settings(self):
        """Save character-specific settings"""
        try:
            path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config", "character_settings.json")
            with open(path, 'w') as f:
                json.dump(self.character_settings, f, indent=4)
        except Exception as e:
            self.logger.error(f"Error saving character settings: {e}")

    def apply_character_settings(self):
        """Apply settings for current character"""
        if not self.current_character or not hasattr(self, 'action_vars'):
            return
            
        char_settings = self.character_settings["characters"].get(self.current_character)
        if not char_settings:
            return
            
        # Update action states and cooldowns
        for action_name, var in self.action_vars.items():
            action_key = action_name.lower().replace(" ", "_")
            if action_key in char_settings["actions"]:
                action_settings = char_settings["actions"][action_key]
                # Set the enabled state from character settings, defaulting to False if not found
                var.set(action_settings.get("enabled", False))
                if action_key in self.settings["actions"]:
                    self.settings["actions"][action_key]["cooldown_minutes"] = action_settings["cooldown_minutes"]
                    
        # Update character name in UI if it exists
        if hasattr(self, 'character_name'):
            self.character_name.configure(text=self.current_character)

    def save_current_character_settings(self):
        """Save settings for current character"""
        if not self.current_character:
            return
            
        # Update character settings with current states
        char_settings = self.character_settings["characters"][self.current_character]["actions"]
        for action_name, var in self.action_vars.items():
            action_key = action_name.lower().replace(" ", "_")
            if action_key in char_settings:
                # Save both enabled state and cooldown
                char_settings[action_key]["enabled"] = var.get()
                if action_key in self.settings["actions"]:
                    char_settings[action_key]["cooldown_minutes"] = self.settings["actions"][action_key]["cooldown_minutes"]

    def load_cooldown_states(self):
        """Load cooldown states from JSON file"""
        try:
            config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config", "cooldown_states.json")
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    self.cooldown_states = json.load(f)
            else:
                self.cooldown_states = {}
                # Initialize cooldown states for first character
                self.initialize_cooldown_states("Character1")
                self.save_cooldown_states()
        except Exception as e:
            self.logger.error(f"Error loading cooldown states: {e}")
            self.cooldown_states = {}

    def initialize_cooldown_states(self, character_name):
        """Initialize cooldown states for a character"""
        self.cooldown_states[character_name] = {}
        for action in [
            "gather_resources", 
            "collect_city_resources", 
            "material_production",
            "open_mails",
            "claim_daily_vip_gifts",
            "change_character"
        ]:
            self.cooldown_states[character_name][action] = {
                "is_active": False,
                "start_time": None,
                "end_time": None
            }

    def save_cooldown_states(self):
        """Save cooldown states to JSON file"""
        try:
            config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config", "cooldown_states.json")
            with open(config_path, 'w') as f:
                json.dump(self.cooldown_states, f, indent=4)
        except Exception as e:
            self.logger.error(f"Error saving cooldown states: {e}")
        
    def update_cooldowns(self):
        """Update cooldown timers and UI"""
        if not self.current_character:
            return
            
        current_time = datetime.now()
        updated = False
        
        char_cooldowns = self.cooldown_states.get(self.current_character, {})
        for action_key, state in char_cooldowns.items():
            if state["is_active"] and state["end_time"]:
                end_time = datetime.fromisoformat(state["end_time"])
                if current_time >= end_time:
                    state["is_active"] = False
                    state["start_time"] = None
                    state["end_time"] = None
                    self.save_cooldown_states()
                    updated = True
        
        # Update UI if config tab is showing cooldowns
        if self.selected_action:
            self.update_cooldown_status()
            
        # Schedule next update using refresh rate from settings
        refresh_rate = self.settings["runner"]["refresh_rate_seconds"] * 1000  # Convert to milliseconds
        self.root.after(refresh_rate, self.update_cooldowns)
        
    def update_cooldown_status(self):
        """Update only the cooldown status text without recreating the entire config tab"""
        if not self.selected_action:
            return
            
        action_key = self.selected_action.lower().replace(" ", "_")
        status_widget = self.config_widgets.get(f"{action_key}_status")
        if not status_widget:
            return
            
        minutes, seconds = self.get_cooldown_remaining(action_key)
        if minutes > 0 or seconds > 0:
            status_text = f"Time remaining: {minutes}m {seconds}s"
            status_style = "warning"
        else:
            status_text = "Ready"
            status_style = "success"
            
        status_widget.configure(text=status_text, bootstyle=status_style)
        
        # Update reset button visibility
        reset_button = self.config_widgets.get(f"{action_key}_reset")
        if reset_button:
            if minutes > 0 or seconds > 0:
                reset_button.pack(side=RIGHT)
            else:
                reset_button.pack_forget()
                
    def start_cooldown(self, action_key):
        """Start cooldown for an action"""
        if not self.current_character:
            return
            
        current_time = datetime.now()
        cooldown_minutes = self.settings["actions"][action_key]["cooldown_minutes"]
        end_time = current_time + timedelta(minutes=cooldown_minutes)
        
        if self.current_character not in self.cooldown_states:
            self.initialize_cooldown_states(self.current_character)
            
        self.cooldown_states[self.current_character][action_key] = {
            "is_active": True,
            "start_time": current_time.isoformat(),
            "end_time": end_time.isoformat()
        }
        self.save_cooldown_states()
        
    def reset_cooldown(self, action_key):
        """Reset cooldown for an action"""
        if not self.current_character:
            return
            
        if self.current_character not in self.cooldown_states:
            self.initialize_cooldown_states(self.current_character)
            
        self.cooldown_states[self.current_character][action_key] = {
            "is_active": False,
            "start_time": None,
            "end_time": None
        }
        self.save_cooldown_states()
        self.update_config_tab()
        
    def get_cooldown_remaining(self, action_key):
        """Get remaining cooldown time in minutes and seconds"""
        if not self.current_character:
            return 0, 0
            
        char_cooldowns = self.cooldown_states.get(self.current_character, {})
        state = char_cooldowns.get(action_key)
        
        if not state or not state["is_active"] or not state["end_time"]:
            return 0, 0
            
        end_time = datetime.fromisoformat(state["end_time"])
        remaining = end_time - datetime.now()
        
        if remaining.total_seconds() <= 0:
            return 0, 0
            
        minutes = int(remaining.total_seconds() // 60)
        seconds = int(remaining.total_seconds() % 60)
        return minutes, seconds
        
    def create_header(self):
        """Create the header with instance info and resource counters"""
        header = ttk.Frame(self.main_container)
        header.pack(fill=X, pady=(0, 5))
        
        # Instance selector (left)
        instance_frame = ttk.Frame(header)
        instance_frame.pack(side=LEFT)
        
        self.instance_var = tk.StringVar(value="BlueStacks 1")
        instance_menu = ttk.Menubutton(
            instance_frame,
            text="BlueStacks 1",
            bootstyle="outline"
        )
        instance_menu.pack(side=LEFT)
        
        # Character name display (center-left)
        character_frame = ttk.Frame(header)
        character_frame.pack(side=LEFT, padx=20)
        
        ttk.Label(
            character_frame,
            text="Character:",
            bootstyle="secondary"
        ).pack(side=LEFT)
        
        self.character_name = ttk.Label(
            character_frame,
            text="Not Selected",
            bootstyle="info",
            padding=(5, 0)
        )
        self.character_name.pack(side=LEFT)
        
        # Control buttons (center)
        control_frame = ttk.Frame(header)
        control_frame.pack(side=LEFT, padx=50)  # Increased padding to move buttons right
        
        self.start_button = ttk.Button(
            control_frame,
            text="Start Bot",
            bootstyle="success",
            command=self.start_bot
        )
        self.start_button.pack(side=LEFT, padx=5)
        
        self.stop_button = ttk.Button(
            control_frame,
            text="Stop Bot",
            bootstyle="danger",
            command=self.stop_bot,
            state="disabled"
        )
        self.stop_button.pack(side=LEFT, padx=5)
        
        # Resource counters (right)
        resources_frame = ttk.Frame(header)
        resources_frame.pack(side=RIGHT)
        
        resources = [
            ("🌾", "1.3M"),
            ("🪵", "1.6M"),
            ("🪨", "2.1M"),
            ("💰", "239.4k"),
            ("💎", "4.6k")
        ]
        
        for icon, value in resources:
            ttk.Label(
                resources_frame,
                text=f"{icon} {value}",
                bootstyle="inverse-dark",
                padding=5
            ).pack(side=LEFT, padx=2)
            
    def create_main_content(self):
        """Create the main content area with activities and logs"""
        content = ttk.Frame(self.main_container)
        content.pack(fill=BOTH, expand=True)
        
        # Create left panel (Activities)
        self.create_activities_panel(content)
        
        # Create right panel (Logs)
        self.create_logs_panel(content)
        
    def create_activities_panel(self, parent):
        """Create the activities panel with tabs"""
        left_panel = ttk.Frame(parent)
        left_panel.pack(side=LEFT, fill=BOTH, expand=True, padx=(0, 5))
        
        # Tabs for Activities and Misc
        tabs = ttk.Notebook(left_panel)
        tabs.pack(fill=BOTH, expand=True)
        
        # Activities tab
        activities_frame = ttk.Frame(tabs)
        tabs.add(activities_frame, text="ACTIVITIES")
        
        # List of actual actions from our actions folder
        self.action_vars = {}  # Store action variables
        self.action_buttons = {}  # Store action buttons
        self.action_status_labels = {}  # Store status labels
        
        actions = [
            "Gather Resources",
            "Collect City Resources",
            "Material Production",
            "Open Mails",
            "Claim Daily VIP Gifts",
            "Change Character"
        ]
        
        for action in actions:
            action_frame = ttk.Frame(activities_frame)
            action_frame.pack(fill=X, pady=1)
            
            # Get saved enabled state for the action
            action_key = action.lower().replace(" ", "_")
            enabled = False
            if (self.current_character and 
                self.current_character in self.character_settings.get("characters", {}) and
                action_key in self.character_settings["characters"][self.current_character]["actions"]):
                enabled = self.character_settings["characters"][self.current_character]["actions"][action_key].get("enabled", False)
            
            # Create variable for checkbox with saved state
            var = tk.BooleanVar(value=enabled)
            self.action_vars[action] = var
            
            # Checkbox on the left
            ttk.Checkbutton(
                action_frame,
                text=action,
                bootstyle="round-toggle",
                variable=var
            ).pack(side=LEFT)
            
            # Create button for selection
            btn = ttk.Button(
                action_frame,
                text="Configure",
                bootstyle="outline",
                command=lambda a=action: self.select_action(a)
            )
            btn.pack(side=RIGHT, padx=5)
            self.action_buttons[action] = btn
            
            # Create status label with default "N/A" status
            status_label = ttk.Label(
                action_frame,
                text="N/A",
                bootstyle=self.ACTION_STATUSES["N/A"],
                padding=(5, 2)  # Add some padding to make the background more visible
            )
            status_label.pack(side=RIGHT, padx=5)
            self.action_status_labels[action] = status_label
            
        # Misc tab - create and add
        misc_frame = self.create_misc_tab(tabs)
        tabs.add(misc_frame, text="MISC")
        
    def create_logs_panel(self, parent):
        """Create the logs panel with tabs"""
        right_panel = ttk.Frame(parent)
        right_panel.pack(side=RIGHT, fill=BOTH, expand=True)
        
        # Tabs for Activity Log and Config
        self.right_tabs = ttk.Notebook(right_panel)
        self.right_tabs.pack(fill=BOTH, expand=True)
        
        # Activity Log tab
        log_frame = ttk.Frame(self.right_tabs)
        self.right_tabs.add(log_frame, text="ACTIVITY LOG")
        
        self.log_text = tk.Text(
            log_frame,
            wrap=tk.WORD,
            bg='#2b3e50',  # Dark theme background
            fg='#ffffff',  # White text
            font=('Consolas', 10)
        )
        self.log_text.pack(fill=BOTH, expand=True)
        
        # Config tab
        self.config_frame = ttk.Frame(self.right_tabs)
        self.right_tabs.add(self.config_frame, text="CONFIG")
        
        # Add default message
        self.config_message = ttk.Label(
            self.config_frame,
            text="Select an action to view its configuration",
            bootstyle="secondary",
            padding=20
        )
        self.config_message.pack(expand=True)
        
        # Create config widgets container (hidden by default)
        self.config_container = ttk.Frame(self.config_frame)
        
        # Store config widgets
        self.config_widgets = {}
        
    def create_misc_tab(self, parent):
        """Create the MISC tab with runner settings"""
        misc_frame = ttk.Frame(parent)
        
        # Runner Settings Section
        runner_label = ttk.Label(
            misc_frame,
            text="Runner Settings",
            font=("TkDefaultFont", 12, "bold")
        )
        runner_label.pack(fill=X, pady=(10, 5), padx=5)
        
        # Basic Settings Frame
        basic_frame = ttk.LabelFrame(misc_frame, text="Basic Settings", padding=10)
        basic_frame.pack(fill=X, padx=5, pady=5)
        
        # Refresh Rate
        refresh_frame = ttk.Frame(basic_frame)
        refresh_frame.pack(fill=X, pady=2)
        ttk.Label(refresh_frame, text="Refresh Rate (seconds):").pack(side=LEFT)
        self.refresh_rate = ttk.Entry(
            refresh_frame,
            width=10
        )
        self.refresh_rate.insert(0, str(self.settings["runner"]["refresh_rate_seconds"]))
        self.refresh_rate.pack(side=LEFT, padx=5)
        
        # Continuous Running
        self.continuous_running = ttk.Checkbutton(
            basic_frame,
            text="Continuous Running",
            variable=tk.BooleanVar(value=self.settings["runner"]["continuous_running"]),
            bootstyle="round-toggle"
        )
        self.continuous_running.pack(fill=X, pady=2)
        
        # Night Mode Settings Frame
        night_frame = ttk.LabelFrame(misc_frame, text="Night Mode", padding=10)
        night_frame.pack(fill=X, padx=5, pady=5)
        
        # Night Mode Enable
        self.night_mode_enabled = ttk.Checkbutton(
            night_frame,
            text="Enable Night Mode",
            variable=tk.BooleanVar(value=self.settings["runner"]["night_sleep_enabled"]),
            bootstyle="round-toggle"
        )
        self.night_mode_enabled.pack(fill=X, pady=2)
        
        # Night Mode Times
        times_frame = ttk.Frame(night_frame)
        times_frame.pack(fill=X, pady=2)
        
        ttk.Label(times_frame, text="Start Time:").pack(side=LEFT)
        self.night_start = ttk.Entry(
            times_frame,
            width=10
        )
        self.night_start.insert(0, self.settings["runner"]["night_sleep_start"])
        self.night_start.pack(side=LEFT, padx=5)
        
        ttk.Label(times_frame, text="End Time:").pack(side=LEFT, padx=(10, 0))
        self.night_end = ttk.Entry(
            times_frame,
            width=10
        )
        self.night_end.insert(0, self.settings["runner"]["night_sleep_end"])
        self.night_end.pack(side=LEFT, padx=5)
        
        # Coffee Break Settings Frame
        coffee_frame = ttk.LabelFrame(misc_frame, text="Coffee Break", padding=10)
        coffee_frame.pack(fill=X, padx=5, pady=5)
        
        # Min Minutes
        min_frame = ttk.Frame(coffee_frame)
        min_frame.pack(fill=X, pady=2)
        ttk.Label(min_frame, text="Minimum Break (minutes):").pack(side=LEFT)
        self.coffee_min = ttk.Entry(
            min_frame,
            width=10
        )
        self.coffee_min.insert(0, str(self.settings["runner"]["coffee_break_min_minutes"]))
        self.coffee_min.pack(side=LEFT, padx=5)
        
        # Max Minutes
        max_frame = ttk.Frame(coffee_frame)
        max_frame.pack(fill=X, pady=2)
        ttk.Label(max_frame, text="Maximum Break (minutes):").pack(side=LEFT)
        self.coffee_max = ttk.Entry(
            max_frame,
            width=10
        )
        self.coffee_max.insert(0, str(self.settings["runner"]["coffee_break_max_minutes"]))
        self.coffee_max.pack(side=LEFT, padx=5)
        
        # Break Chance
        chance_frame = ttk.Frame(coffee_frame)
        chance_frame.pack(fill=X, pady=2)
        ttk.Label(chance_frame, text="Break Chance (0-1):").pack(side=LEFT)
        self.coffee_chance = ttk.Entry(
            chance_frame,
            width=10
        )
        self.coffee_chance.insert(0, str(self.settings["runner"]["coffee_break_chance"]))
        self.coffee_chance.pack(side=LEFT, padx=5)
        
        # Min Break Interval
        interval_frame = ttk.Frame(coffee_frame)
        interval_frame.pack(fill=X, pady=2)
        ttk.Label(interval_frame, text="Minimum Break Interval (minutes):").pack(side=LEFT)
        self.min_break_interval = ttk.Entry(
            interval_frame,
            width=10
        )
        self.min_break_interval.insert(0, str(self.settings["runner"]["min_break_interval_minutes"]))
        self.min_break_interval.pack(side=LEFT, padx=5)
        
        # Character Switch Settings Frame
        char_frame = ttk.LabelFrame(misc_frame, text="Character Switch", padding=10)
        char_frame.pack(fill=X, padx=5, pady=5)
        
        # Enable/Disable Toggle
        self.char_switch_enabled = ttk.Checkbutton(
            char_frame,
            text="Enable Character Switch",
            variable=tk.BooleanVar(value=self.settings["runner"]["character_switch"]["enabled"]),
            bootstyle="round-toggle"
        )
        self.char_switch_enabled.pack(fill=X, pady=2)
        
        # Min Seconds
        min_frame = ttk.Frame(char_frame)
        min_frame.pack(fill=X, pady=2)
        ttk.Label(min_frame, text="Switch after min (seconds):").pack(side=LEFT)
        self.char_switch_min = ttk.Entry(
            min_frame,
            width=10
        )
        self.char_switch_min.insert(0, str(self.settings["runner"]["character_switch"]["min_seconds"]))
        self.char_switch_min.pack(side=LEFT, padx=5)
        
        # Max Seconds
        max_frame = ttk.Frame(char_frame)
        max_frame.pack(fill=X, pady=2)
        ttk.Label(max_frame, text="Switch after max (seconds):").pack(side=LEFT)
        self.char_switch_max = ttk.Entry(
            max_frame,
            width=10
        )
        self.char_switch_max.insert(0, str(self.settings["runner"]["character_switch"]["max_seconds"]))
        self.char_switch_max.pack(side=LEFT, padx=5)
        
        # Save Settings Button
        save_frame = ttk.Frame(misc_frame)
        save_frame.pack(fill=X, pady=10, padx=5)
        
        ttk.Button(
            save_frame,
            text="Save Settings",
            bootstyle="success",
            command=self.save_settings
        ).pack(side=RIGHT)
        
        ttk.Button(
            save_frame,
            text="Reset to Default",
            bootstyle="secondary",
            command=self.reset_settings
        ).pack(side=RIGHT, padx=5)
        
        return misc_frame
        
    def create_status_bar(self):
        """Create the bottom status bar"""
        status_bar = ttk.Frame(self.main_container)
        status_bar.pack(fill=X, pady=(5, 0))
        
        self.status_label = ttk.Label(
            status_bar,
            text="Status: Ready",
            bootstyle="info"
        )
        self.status_label.pack(side=LEFT)
        
    def add_log(self, message):
        """Add a message to the log with timestamp"""
        timestamp = datetime.now().strftime('[%H:%M:%S]')
        self.log_text.insert('end', f"{timestamp} {message}\n")
        self.log_text.see('end')
        
    def start_bot(self):
        """Start the bot"""
        self.running = True
        self.status_label.configure(text="Status: Running", bootstyle="success")
        self.start_button.configure(state="disabled")
        self.stop_button.configure(state="normal")
        self.add_log("Bot started")
        
        # Set all enabled actions to "Waiting"
        for action, var in self.action_vars.items():
            if var.get():  # If action is checked/enabled
                self.update_action_status(action, "Waiting")
            else:
                self.update_action_status(action, "N/A")
        
    def stop_bot(self):
        """Stop the bot"""
        self.running = False
        self.status_label.configure(text="Status: Ready", bootstyle="info")
        self.start_button.configure(state="normal")
        self.stop_button.configure(state="disabled")
        self.add_log("Bot stopped")
        
        # Reset all action statuses to "N/A"
        for action in self.action_status_labels:
            self.update_action_status(action, "N/A")
        
    def save_settings(self):
        """Save current settings to file"""
        try:
            # Update settings dictionary
            self.settings["runner"].update({
                "refresh_rate_seconds": int(self.refresh_rate.get()),
                "continuous_running": self.continuous_running.instate(['selected']),
                "night_sleep_enabled": self.night_mode_enabled.instate(['selected']),
                "night_sleep_start": self.night_start.get(),
                "night_sleep_end": self.night_end.get(),
                "coffee_break_min_minutes": int(self.coffee_min.get()),
                "coffee_break_max_minutes": int(self.coffee_max.get()),
                "coffee_break_chance": float(self.coffee_chance.get()),
                "min_break_interval_minutes": int(self.min_break_interval.get()),
                "character_switch": {
                    "enabled": self.char_switch_enabled.instate(['selected']),
                    "min_seconds": int(self.char_switch_min.get()),
                    "max_seconds": int(self.char_switch_max.get())
                }
            })
            
            # Save to file
            config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config", "settings.json")
            with open(config_path, 'w') as f:
                json.dump(self.settings, f, indent=4)
            
            self.add_log("Settings saved successfully")
        except Exception as e:
            self.add_log(f"Error saving settings: {str(e)}")
    
    def reset_settings(self):
        """Reset settings to default values"""
        self.load_default_settings()
        
        # Update UI elements
        self.refresh_rate.delete(0, tk.END)
        self.refresh_rate.insert(0, str(self.settings["runner"]["refresh_rate_seconds"]))
        
        self.continuous_running.state(['!selected'])
        if self.settings["runner"]["continuous_running"]:
            self.continuous_running.state(['selected'])
            
        self.night_mode_enabled.state(['!selected'])
        if self.settings["runner"]["night_sleep_enabled"]:
            self.night_mode_enabled.state(['selected'])
            
        self.night_start.delete(0, tk.END)
        self.night_start.insert(0, self.settings["runner"]["night_sleep_start"])
        
        self.night_end.delete(0, tk.END)
        self.night_end.insert(0, self.settings["runner"]["night_sleep_end"])
        
        self.coffee_min.delete(0, tk.END)
        self.coffee_min.insert(0, str(self.settings["runner"]["coffee_break_min_minutes"]))
        
        self.coffee_max.delete(0, tk.END)
        self.coffee_max.insert(0, str(self.settings["runner"]["coffee_break_max_minutes"]))
        
        self.coffee_chance.delete(0, tk.END)
        self.coffee_chance.insert(0, str(self.settings["runner"]["coffee_break_chance"]))
        
        self.min_break_interval.delete(0, tk.END)
        self.min_break_interval.insert(0, str(self.settings["runner"]["min_break_interval_minutes"]))
        
        self.char_switch_enabled.state(['!selected'])
        if self.settings["runner"]["character_switch"]["enabled"]:
            self.char_switch_enabled.state(['selected'])
        
        self.char_switch_min.delete(0, tk.END)
        self.char_switch_min.insert(0, str(self.settings["runner"]["character_switch"]["min_seconds"]))
        
        self.char_switch_max.delete(0, tk.END)
        self.char_switch_max.insert(0, str(self.settings["runner"]["character_switch"]["max_seconds"]))
        
        self.add_log("Settings reset to default values")
        
    def select_action(self, action_name):
        """Handle action selection"""
        # Reset all buttons to outline style
        for btn in self.action_buttons.values():
            btn.configure(bootstyle="outline")
            
        # Highlight selected button
        self.action_buttons[action_name].configure(bootstyle="info-outline")
        
        # Update selected action
        self.selected_action = action_name
        
        # Update config tab
        self.update_config_tab()
        
    def update_config_tab(self):
        """Update the config tab based on selected action"""
        # Clear existing widgets
        for widget in self.config_container.winfo_children():
            widget.destroy()
            
        if not self.selected_action:
            self.config_message.pack(expand=True)
            self.config_container.pack_forget()
            return
            
        # Hide default message and show container
        self.config_message.pack_forget()
        self.config_container.pack(fill=BOTH, expand=True, padx=10, pady=10)
        
        # Convert action name to settings key
        action_key = self.selected_action.lower().replace(" ", "_")
        
        if action_key in self.settings["actions"]:
            action_config = self.settings["actions"][action_key]
            
            # Create cooldown settings frame
            cooldown_frame = ttk.LabelFrame(self.config_container, text="Cooldown Settings", padding=10)
            cooldown_frame.pack(fill=X, pady=5)
            
            # Cooldown duration
            duration_frame = ttk.Frame(cooldown_frame)
            duration_frame.pack(fill=X, pady=5)
            
            ttk.Label(
                duration_frame,
                text="Cooldown (minutes):",
                padding=(0, 0, 10, 0)
            ).pack(side=LEFT)
            
            # Create and configure the entry widget with validation
            vcmd = (self.root.register(self.validate_number), '%P')
            cooldown_entry = ttk.Entry(
                duration_frame,
                width=10,
                validate='key',
                validatecommand=vcmd
            )
            cooldown_entry.insert(0, str(action_config["cooldown_minutes"]))
            cooldown_entry.pack(side=LEFT)
            
            # Store widget reference
            self.config_widgets[f"{action_key}_cooldown"] = cooldown_entry
            
            # Cooldown status
            status_frame = ttk.Frame(cooldown_frame)
            status_frame.pack(fill=X, pady=5)
            
            ttk.Label(
                status_frame,
                text="Status:",
                padding=(0, 0, 10, 0)
            ).pack(side=LEFT)
            
            minutes, seconds = self.get_cooldown_remaining(action_key)
            if minutes > 0 or seconds > 0:
                status_text = f"Time remaining: {minutes}m {seconds}s"
                status_style = "warning"
            else:
                status_text = "Ready"
                status_style = "success"
            
            status_label = ttk.Label(
                status_frame,
                text=status_text,
                bootstyle=status_style
            )
            status_label.pack(side=LEFT)
            
            # Store status label reference
            self.config_widgets[f"{action_key}_status"] = status_label
            
            # Reset button
            reset_button = ttk.Button(
                status_frame,
                text="Reset Cooldown",
                bootstyle="danger",
                command=lambda: self.reset_cooldown(action_key)
            )
            
            # Store reset button reference
            self.config_widgets[f"{action_key}_reset"] = reset_button
            
            if minutes > 0 or seconds > 0:
                reset_button.pack(side=RIGHT)
            
            # Add save button
            ttk.Button(
                self.config_container,
                text="Save Configuration",
                bootstyle="success",
                command=self.save_action_config,
                padding=10
            ).pack(side=BOTTOM, pady=20)
            
    def save_action_config(self):
        """Save the action-specific configuration"""
        if not self.selected_action:
            return
            
        action_key = self.selected_action.lower().replace(" ", "_")
        
        try:
            # Update settings with new values
            cooldown_widget = self.config_widgets.get(f"{action_key}_cooldown")
            if cooldown_widget:
                new_cooldown = int(cooldown_widget.get())
                self.settings["actions"][action_key]["cooldown_minutes"] = new_cooldown
                
                # Update character-specific settings
                if self.current_character:
                    self.character_settings["characters"][self.current_character]["actions"][action_key]["cooldown_minutes"] = new_cooldown
                    
            # Save both settings files
            config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config", "settings.json")
            with open(config_path, 'w') as f:
                json.dump(self.settings, f, indent=4)
            
            self.save_character_settings()
                    
            self.add_log(f"Configuration saved for {self.selected_action}")
            
        except Exception as e:
            self.add_log(f"Error saving action configuration: {str(e)}")
        
    def validate_number(self, value):
        """Validate that the input is a positive number or empty"""
        if value == "":
            return True
        try:
            num = int(value)
            return num >= 0
        except ValueError:
            return False
        
    def update_character_name(self, name):
        """Update character name and load their settings"""
        # Save current character's settings before switching
        if self.current_character:
            self.save_current_character_settings()
        
        # Update UI
        self.character_name.configure(text=name)
        
        # Update current character
        self.current_character = name
        self.character_settings["current_character"] = name
        
        # Create settings for new character if needed
        if name not in self.character_settings["characters"]:
            self.character_settings["characters"][name] = {
                "actions": {}
            }
            # Copy default action settings
            for action_key, action_config in self.settings["actions"].items():
                self.character_settings["characters"][name]["actions"][action_key] = {
                    "enabled": action_config.get("enabled", True),
                    "cooldown_minutes": action_config["cooldown_minutes"]
                }
            
            # Initialize cooldown states for new character
            if name not in self.cooldown_states:
                self.initialize_cooldown_states(name)
        
        # Apply new character's settings
        self.apply_character_settings()
        
        # Save both character settings and cooldown states
        self.save_character_settings()
        self.save_cooldown_states()
        
        self.add_log(f"Character switched to: {name}")
        
    def update_action_status(self, action, status):
        """Update the status of an action with the appropriate color"""
        if action not in self.action_status_labels or status not in self.ACTION_STATUSES:
            return
            
        status_label = self.action_status_labels[action]
        bootstyle = self.ACTION_STATUSES[status]
        status_label.configure(text=status, bootstyle=bootstyle)
        
        # Log the status change
        self.add_log(f"Action '{action}' status changed to: {status}")
        
    def cleanup_and_exit(self):
        """Perform cleanup operations before exiting"""
        try:
            # Save current character's settings if one is selected
            if self.current_character:
                self.save_current_character_settings()
                
            # Save character settings file
            self.save_character_settings()
            
            # Save cooldown states
            self.save_cooldown_states()
            
            # Log cleanup
            self.logger.info("Cleanup completed successfully")
            
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")
            
        finally:
            # Destroy the window and exit
            self.root.destroy()
        
    def run(self):
        """Start the main event loop"""
        self.root.mainloop()

def main():
    app = MainWindow()
    app.run()

if __name__ == "__main__":
    main() 