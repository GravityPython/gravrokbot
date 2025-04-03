"""
Test runner for simulating action execution
"""

import random
import logging
import threading
import time
from datetime import datetime
from gravrokbot.core.bot_runner import BotRunner

class TestRunner(BotRunner):
    def __init__(self, main_window, config):
        """
        Initialize test runner
        
        Args:
            main_window (MainWindow): Main window instance for UI updates
            config (dict): Configuration dictionary with runner settings
        """
        super().__init__(main_window, config)
        
        # Test mode settings
        test_mode_config = self.config.get('test_mode', {})
        self.dummy_execution_seconds = test_mode_config.get('dummy_execution_seconds', 15)
        
        # Test runner specific properties
        self.current_action_index = 0
        self.thread = None
        self.current_sleep_start = None
        self.current_sleep_duration = 0
        
        self.logger.warning("----- TEST MODE ENABLED -----")
        self.logger.info(f"Dummy execution time: {self.dummy_execution_seconds} seconds per action.")
        
    def start(self):
        """Start test runner in a background thread"""
        if self.running:
            self.logger.warning("Test runner already running")
            return
            
        self.logger.info("Starting test runner")
        self.running = True
        self.interrupt_requested = False
        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        self.thread.start()
    
    def stop(self):
        """Stop test runner immediately"""
        if not self.running:
            self.logger.warning("Test runner not running")
            return
            
        self.logger.info("Stopping test runner")
        self.interrupt()
        
        if hasattr(self, 'thread') and self.thread:
            self.thread.join(timeout=5.0)
            
        # Reset all action statuses to N/A
        for action in self.actions:
            if action.enabled:
                self.main_window.update_action_status(action.name, "N/A")
    
    def _interruptible_sleep(self, seconds):
        """Sleep function that can be interrupted"""
        self.current_sleep_start = time.time()
        self.current_sleep_duration = seconds
        
        end_time = time.time() + seconds
        while time.time() < end_time:
            # Check if interrupted
            if self.interrupt_requested:
                self.logger.debug("Sleep interrupted")
                return True
                
            # Check if paused
            if self.wait_if_paused():
                return True
                
            # Sleep in small increments to allow interruption
            time.sleep(0.1)
            
        self.current_sleep_start = None
        self.current_sleep_duration = 0
        return False
    
    def _run_loop(self):
        """Main test runner loop"""
        self.logger.info("Test runner loop started")
        
        try:
            while self.running and not self.interrupt_requested:
                # Test Mode: Simulate execution without cooldowns or real execution
                self.logger.info("--- Test Mode Cycle ---")
                test_executed_count = 0
                
                # Process each action
                for action in self.actions:
                    # Check for interruption between actions
                    if not self.running or self.interrupt_requested:
                        self.logger.info("Run loop interrupted between actions")
                        break
                        
                    # Check if paused
                    if self.wait_if_paused():
                        self.logger.info("Run loop interrupted during pause")
                        break
                    
                    if action.enabled:
                        # Update action status in UI
                        self.main_window.update_action_status(action.name, "Working")
                        
                        # Log action start
                        start_time = datetime.now().strftime("%H:%M:%S")
                        self.logger.info(f"[{start_time}] Testing Action: {action.name} - Starting (Simulating {self.dummy_execution_seconds}s)")
                        
                        # Simulate action execution with interruptible sleep
                        if self._interruptible_sleep(self.dummy_execution_seconds):
                            self.logger.info(f"Action {action.name} execution interrupted")
                            break
                        
                        # If we're still running (not interrupted), complete the action
                        if self.running and not self.interrupt_requested:
                            # Log action completion
                            end_time = datetime.now().strftime("%H:%M:%S")
                            self.logger.info(f"[{end_time}] Testing Action: {action.name} - Completed")
                            
                            # Update UI status
                            self.main_window.update_action_status(action.name, "Done")
                            
                            test_executed_count += 1
                
                if not self.running or self.interrupt_requested:
                    self.logger.info("Run loop interrupted, exiting")
                    break
                
                if test_executed_count == 0:
                    self.logger.info("No enabled actions to test in this cycle.")
                
                # Wait for next cycle
                refresh_rate = self.config.get('refresh_rate_seconds', 60)
                self.logger.info(f"Waiting {refresh_rate} seconds for next cycle...")
                
                # Check if we should continue running
                if not self.config.get('continuous_running', True):
                    self.logger.info("Continuous running disabled, stopping after one cycle")
                    break
                
                # Wait for next cycle with interruptible sleep
                if self._interruptible_sleep(refresh_rate):
                    self.logger.info("Wait between cycles interrupted")
                    break
                
                # Reset action statuses for next cycle if still running
                if self.running and not self.interrupt_requested:
                    for action in self.actions:
                        if action.enabled:
                            self.main_window.update_action_status(action.name, "Waiting")
                    
        except Exception as e:
            self.logger.error(f"Error in test runner loop: {e}")
        finally:
            self.logger.info("Test runner loop stopped")
            self.running = False
            self.interrupt_requested = False
    
    def get_action_statuses(self):
        """
        Get status information for all actions
        
        Returns:
            list: List of dictionaries with action status information
        """
        statuses = []
        for action in self.actions:
            status = {
                'name': action.name,
                'state': 'idle',  # In test mode, we don't track state machine states
                'enabled': action.enabled,
                'on_cooldown': False,  # Test mode ignores cooldowns
                'cooldown_remaining': 0,
                'last_execution': None
            }
            statuses.append(status)
        return statuses 