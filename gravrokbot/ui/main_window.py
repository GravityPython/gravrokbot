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
            
        # Misc tab
        misc_frame = ttk.Frame(tabs)
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
        
    def run(self):
        """Start the main event loop"""
        self.root.mainloop()

def main():
    app = MainWindow()
    app.run()

if __name__ == "__main__":
    main() 