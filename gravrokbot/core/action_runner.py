import time
import logging
import threading
import random
from datetime import datetime, timedelta
from gravrokbot.core.bot_runner import BotRunner

class ActionRunner(BotRunner):
    """Manages and executes game actions based on scheduling and cooldowns"""
    
    def __init__(self, main_window, config):
        """
        Initialize action runner with config
        
        Args:
            main_window: Main window instance for UI updates
            config (dict): Configuration dictionary with runner settings
        """
        super().__init__(main_window, config)
        
        # Configure timing settings
        self.refresh_rate_seconds = self.config.get('refresh_rate_seconds', 60)
        self.continuous_running = self.config.get('continuous_running', True)
        self.night_sleep_enabled = self.config.get('night_sleep_enabled', False)
        self.night_sleep_start = self.config.get('night_sleep_start', '23:00')
        self.night_sleep_end = self.config.get('night_sleep_end', '07:00')
        self.coffee_break_min_minutes = self.config.get('coffee_break_min_minutes', 10)
        self.coffee_break_max_minutes = self.config.get('coffee_break_max_minutes', 30)
        self.coffee_break_chance = self.config.get('coffee_break_chance', 0.05)  # 5% chance per cycle
        
        # Last time the bot took a break
        self.last_break_time = None
        
        # Test Mode Settings
        test_mode_config = self.config.get('test_mode', {})
        self.test_mode_enabled = test_mode_config.get('enabled', False)
        self.test_mode_dummy_seconds = test_mode_config.get('dummy_execution_seconds', 15)

        if self.test_mode_enabled:
            self.logger.warning("----- TEST MODE ENABLED -----")
            self.logger.info(f"Dummy execution time: {self.test_mode_dummy_seconds} seconds per action.")

        self.logger.info("Action runner initialized")
    
    def add_action(self, action):
        """
        Add an action to the runner
        
        Args:
            action (ActionWorkflow): Action to add
        """
        self.logger.info(f"Adding action: {action.name}")
        self.actions.append(action)
    
    def start(self):
        """Start the action runner in a background thread"""
        if self.running:
            self.logger.warning("Action runner already running")
            return
            
        self.logger.info("Starting action runner")
        self.running = True
        self.interrupt_requested = False
        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        self.thread.start()
    
    def stop(self):
        """Stop the action runner immediately"""
        if not self.running:
            self.logger.warning("Action runner not running")
            return
            
        self.logger.info("Stopping action runner")
        self.interrupt()
        
        if hasattr(self, 'thread') and self.thread:
            self.thread.join(timeout=5.0)
            
        # Reset all action statuses to N/A
        for action in self.actions:
            if action.enabled:
                self.main_window.update_action_status(action.name, "N/A")
    
    def _interruptible_sleep(self, seconds):
        """Sleep function that can be interrupted"""
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
            
        return False
    
    def _is_night_sleep_time(self):
        """
        Check if current time is within night sleep hours
        
        Returns:
            bool: True if it's night sleep time, False otherwise
        """
        if not self.night_sleep_enabled:
            return False
            
        now = datetime.now().time()
        start_time = datetime.strptime(self.night_sleep_start, '%H:%M').time()
        end_time = datetime.strptime(self.night_sleep_end, '%H:%M').time()
        
        # Handle cases like 23:00 - 07:00 that cross midnight
        if start_time > end_time:
            return now >= start_time or now <= end_time
        else:
            return start_time <= now <= end_time
    
    def _should_take_coffee_break(self):
        """
        Determine if bot should take a coffee break
        
        Returns:
            bool: True if bot should take a break, False otherwise
        """
        # Check if we recently had a break
        if self.last_break_time:
            min_break_interval = self.config.get('min_break_interval_minutes', 120)  # 2 hours minimum between breaks
            elapsed_minutes = (datetime.now() - self.last_break_time).total_seconds() / 60
            if elapsed_minutes < min_break_interval:
                return False
        
        # Random chance for coffee break
        return random.random() < self.coffee_break_chance
    
    def _take_coffee_break(self):
        """
        Take a coffee break (pause execution for a random time)
        """
        break_minutes = random.uniform(self.coffee_break_min_minutes, self.coffee_break_max_minutes)
        self.logger.info(f"Taking a coffee break for {break_minutes:.1f} minutes")
        
        # Record break time
        self.last_break_time = datetime.now()
        
        # Sleep for break duration (interruptible)
        if self._interruptible_sleep(break_minutes * 60):
            self.logger.info("Coffee break interrupted")
            return True
        
        self.logger.info("Coffee break finished, resuming actions")
        return False
    
    def _run_loop(self):
        """Main action runner loop"""
        self.logger.info("Action runner loop started")
        
        try:
            while self.running and not self.interrupt_requested:
                # Check if it's night sleep time
                if self._is_night_sleep_time():
                    self.logger.info("Night sleep time, pausing actions")
                    if self._interruptible_sleep(self.refresh_rate_seconds):
                        break
                    continue
                
                # Check if we should take a coffee break
                if self._should_take_coffee_break():
                    if self._take_coffee_break():
                        break
                
                # Check if paused
                if self.wait_if_paused():
                    self.logger.info("Run loop interrupted during pause")
                    break
                
                # --- Action Execution Logic ---
                if self.test_mode_enabled:
                    # Test Mode: Simulate execution without cooldowns or real execution
                    self.logger.info("--- Test Mode Cycle ---")
                    test_executed_count = 0
                    for action in self.actions:
                        # Check for interruption
                        if not self.running or self.interrupt_requested:
                            break
                            
                        if action.enabled:
                            # Update action status in UI
                            self.main_window.update_action_status(action.name, "Working")
                            
                            start_time = datetime.now().strftime("%H:%M:%S")
                            self.logger.info(f"[{start_time}] Testing Action: {action.name} - Starting (Simulating {self.test_mode_dummy_seconds}s)")
                            
                            # Simulation with interruptible sleep
                            if self._interruptible_sleep(self.test_mode_dummy_seconds):
                                self.logger.info(f"Action {action.name} execution interrupted")
                                break
                            
                            # If we're still running (not interrupted), log completion
                            if self.running and not self.interrupt_requested:
                                end_time = datetime.now().strftime("%H:%M:%S")
                                self.logger.info(f"[{end_time}] Testing Action: {action.name} - Completed")
                                self.main_window.update_action_status(action.name, "Done")
                                test_executed_count += 1
                    
                    if test_executed_count == 0 and self.running and not self.interrupt_requested:
                         self.logger.info("No enabled actions to test in this cycle.")

                else:
                    # Normal Mode: Execute enabled actions that are not on cooldown
                    executed_count = 0
                    for action in self.actions:
                        # Check for interruption
                        if not self.running or self.interrupt_requested:
                            break
                            
                        if not action.is_on_cooldown() and action.enabled:
                            # Update UI status
                            self.main_window.update_action_status(action.name, "Working")
                            
                            # Execute action
                            action.execute()
                            executed_count += 1
                            
                            # Update UI status after execution
                            self.main_window.update_action_status(action.name, "Done")

                            # Small delay between actions
                            delay = random.uniform(1.0, 3.0)
                            if self._interruptible_sleep(delay):
                                break

                    if executed_count == 0 and self.running and not self.interrupt_requested:
                        self.logger.info("No actions executed in this cycle (all on cooldown or disabled)")
                # --- End Action Execution Logic ---
                
                # Exit if interrupted
                if not self.running or self.interrupt_requested:
                    break
                
                # Wait for next cycle
                self.logger.info(f"Waiting {self.refresh_rate_seconds} seconds for next cycle...")
                
                # Check if we should continue running
                if not self.continuous_running:
                    self.logger.info("Continuous running disabled, stopping after one cycle")
                    break
                    
                # Wait for next cycle with interruptible sleep
                if self._interruptible_sleep(self.refresh_rate_seconds):
                    self.logger.info("Wait between cycles interrupted")
                    break
                    
                # Reset action statuses for next cycle if still running
                if self.running and not self.interrupt_requested:
                    for action in self.actions:
                        if action.enabled:
                            self.main_window.update_action_status(action.name, "Waiting")
                    
        except Exception as e:
            self.logger.error(f"Error in action runner loop: {e}")
        finally:
            self.logger.info("Action runner loop stopped")
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
                'state': action.state,
                'enabled': action.enabled,
                'on_cooldown': action.is_on_cooldown(),
                'cooldown_remaining': action.get_cooldown_remaining(),
                'last_execution': action.last_execution_time
            }
            statuses.append(status)
        return statuses 