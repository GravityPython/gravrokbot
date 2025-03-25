"""
Main window UI for GravRokBot using ttkbootstrap.
"""

import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from datetime import datetime
import sys
import os
import logging
import json

class MainWindow:
    def __init__(self):
        self.root = ttk.Window(
            title="Rise of Kingdoms Bot 1.0.0",
            themename="darkly",
            size=(1200, 800),
            position=(100, 100)
        )
        
        # Configure logging
        self.logger = logging.getLogger('gravrokbot')
        
        # Load default settings
        self.load_default_settings()
        
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
        
    def load_default_settings(self):
        """Load default settings from JSON file"""
        try:
            config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config", "default_settings.json")
            with open(config_path, 'r') as f:
                self.settings = json.load(f)
        except Exception as e:
            self.logger.error(f"Error loading default settings: {e}")
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
                        "min_seconds": 1800,
                        "max_seconds": 3600
                    }
                }
            }
        
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
        
        # Control buttons
        control_frame = ttk.Frame(header)
        control_frame.pack(side=LEFT, padx=10)
        
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
        actions = [
            "Gather Resources",
            "Collect City Resources",
            "Change Character",
            "Start Game",
            "Close Game"
        ]
        
        for action in actions:
            action_frame = ttk.Frame(activities_frame)
            action_frame.pack(fill=X, pady=1)
            
            # Create variable for checkbox
            var = tk.BooleanVar(value=True)
            self.action_vars[action] = var
            
            ttk.Checkbutton(
                action_frame,
                text=action,
                bootstyle="round-toggle",
                variable=var
            ).pack(side=LEFT)
            
            ttk.Label(
                action_frame,
                text="Waiting",
                bootstyle="secondary"
            ).pack(side=RIGHT)
            
        # Misc tab - create and add
        misc_frame = self.create_misc_tab(tabs)
        tabs.add(misc_frame, text="MISC")
        
    def create_logs_panel(self, parent):
        """Create the logs panel with tabs"""
        right_panel = ttk.Frame(parent)
        right_panel.pack(side=RIGHT, fill=BOTH, expand=True)
        
        # Tabs for Activity Log and Config
        tabs = ttk.Notebook(right_panel)
        tabs.pack(fill=BOTH, expand=True)
        
        # Activity Log tab
        log_frame = ttk.Frame(tabs)
        tabs.add(log_frame, text="ACTIVITY LOG")
        
        self.log_text = tk.Text(
            log_frame,
            wrap=tk.WORD,
            bg='#2b3e50',  # Dark theme background
            fg='#ffffff',  # White text
            font=('Consolas', 10)
        )
        self.log_text.pack(fill=BOTH, expand=True)
        
        # Config tab
        config_frame = ttk.Frame(tabs)
        tabs.add(config_frame, text="CONFIG")
        
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
        
    def stop_bot(self):
        """Stop the bot"""
        self.running = False
        self.status_label.configure(text="Status: Ready", bootstyle="info")
        self.start_button.configure(state="normal")
        self.stop_button.configure(state="disabled")
        self.add_log("Bot stopped")
        
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
        
    def run(self):
        """Start the main event loop"""
        self.root.mainloop()

def main():
    app = MainWindow()
    app.run()

if __name__ == "__main__":
    main() 