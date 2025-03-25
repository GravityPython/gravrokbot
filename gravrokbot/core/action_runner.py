import time
import logging
import threading
import random
from datetime import datetime, timedelta

class ActionRunner:
    """Manages and executes game actions based on scheduling and cooldowns"""
    
    def __init__(self, config):
        """
        Initialize action runner with config
        
        Args:
            config (dict): Configuration dictionary with runner settings
        """
        self.config = config
        self.logger = logging.getLogger("GravRokBot.Runner")
        self.actions = []
        self.running = False
        self.thread = None
        
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
        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        self.thread.start()
    
    def stop(self):
        """Stop the action runner"""
        if not self.running:
            self.logger.warning("Action runner not running")
            return
            
        self.logger.info("Stopping action runner")
        self.running = False
        if self.thread:
            self.thread.join(timeout=5.0)
    
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
        
        # Sleep for break duration
        time.sleep(break_minutes * 60)
        
        self.logger.info("Coffee break finished, resuming actions")
    
    def _run_loop(self):
        """Main action runner loop"""
        self.logger.info("Action runner loop started")
        
        try:
            while self.running:
                # Check if it's night sleep time
                if self._is_night_sleep_time():
                    self.logger.info("Night sleep time, pausing actions")
                    time.sleep(self.refresh_rate_seconds)
                    continue
                
                # Check if we should take a coffee break
                if self._should_take_coffee_break():
                    self._take_coffee_break()
                
                # Execute enabled actions that are not on cooldown
                executed_count = 0
                for action in self.actions:
                    if not action.is_on_cooldown() and action.enabled:
                        action.execute()
                        executed_count += 1
                        
                        # Small delay between actions
                        time.sleep(random.uniform(1.0, 3.0))
                
                if executed_count == 0:
                    self.logger.info("No actions executed in this cycle (all on cooldown or disabled)")
                
                # Wait for next cycle
                time.sleep(self.refresh_rate_seconds)
                
                # Check if we should continue running
                if not self.continuous_running:
                    self.logger.info("Continuous running disabled, stopping after one cycle")
                    break
                    
        except Exception as e:
            self.logger.error(f"Error in action runner loop: {e}")
        finally:
            self.logger.info("Action runner loop stopped")
            self.running = False
    
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