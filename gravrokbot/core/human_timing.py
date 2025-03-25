"""
Human-like timing module for GravRokBot.
Provides sophisticated randomization for delays and timing to simulate human behavior.
"""

import random
import time
import numpy as np
from datetime import datetime

class HumanTiming:
    """
    Sophisticated timing system that simulates human-like delays and variations
    """
    
    def __init__(self):
        self.last_action_time = datetime.now()
        self.action_count = 0
        self.fatigue_factor = 1.0
        
    def get_random_delay(self, min_delay, max_delay):
        """
        Generate a random delay using various distributions and factors
        
        Args:
            min_delay (float): Minimum delay in seconds
            max_delay (float): Maximum delay in seconds
            
        Returns:
            float: Calculated delay in seconds
        """
        # Base delay using truncated normal distribution (more realistic than uniform)
        mean = (min_delay + max_delay) / 2
        std = (max_delay - min_delay) / 4
        base_delay = np.random.truncnorm(
            (min_delay - mean) / std,
            (max_delay - mean) / std,
            loc=mean,
            scale=std
        ).item()
        
        # Add occasional longer pauses (simulate human distraction)
        if random.random() < 0.05:  # 5% chance
            base_delay *= random.uniform(2, 4)
            
        # Add micro-variations (simulate human imperfection)
        micro_variation = random.gauss(0, 0.1)
        base_delay += micro_variation
        
        # Apply time-of-day variation (humans are slower at night/early morning)
        hour = datetime.now().hour
        if 0 <= hour < 6:  # Late night/early morning
            base_delay *= random.uniform(1.2, 1.5)
        
        # Apply fatigue factor (actions get slightly slower over time)
        self.action_count += 1
        if self.action_count > 50:  # Reset counter and randomize fatigue
            self.action_count = 0
            self.fatigue_factor = random.uniform(0.8, 1.2)
        else:
            # Gradually increase fatigue
            self.fatigue_factor += random.uniform(0.001, 0.005)
        
        base_delay *= self.fatigue_factor
        
        # Ensure we stay within absolute limits despite modifications
        return max(min_delay, min(max_delay * 2, base_delay))
    
    def add_random_pause(self):
        """
        Determine if we should add a longer random pause (coffee break, bio break, etc.)
        
        Returns:
            float: Additional pause time in seconds, 0 if no pause
        """
        # Check time since last long pause
        time_since_last = (datetime.now() - self.last_action_time).total_seconds()
        
        # Probability increases with time since last pause
        pause_probability = min(0.001 * (time_since_last / 60), 0.05)
        
        if random.random() < pause_probability:
            self.last_action_time = datetime.now()
            # Return a pause between 1 and 5 minutes
            return random.uniform(60, 300)
        
        return 0
    
    def get_click_delay(self):
        """
        Get a random delay for clicking (very short, micro-movements)
        
        Returns:
            float: Click delay in seconds
        """
        # Use Gamma distribution for click delays (better models quick human actions)
        return np.random.gamma(shape=2, scale=0.1)
    
    def apply_delay_profile(self, profile_name, config):
        """
        Apply a predefined delay profile from configuration
        
        Args:
            profile_name (str): Name of the delay profile to use
            config (dict): Configuration dictionary containing delay profiles
            
        Returns:
            tuple: (pre_delay, post_delay) in seconds
        """
        if 'delay_profiles' not in config or profile_name not in config['delay_profiles']:
            # Use default delays if profile not found
            return (
                self.get_random_delay(0.5, 1.0),
                self.get_random_delay(0.5, 1.0)
            )
            
        profile = config['delay_profiles'][profile_name]
        pre_delay = self.get_random_delay(
            profile['pre_delay_min'],
            profile['pre_delay_max']
        )
        post_delay = self.get_random_delay(
            profile['post_delay_min'],
            profile['post_delay_max']
        )
        
        return pre_delay, post_delay
    
    def wait(self, min_time, max_time=None):
        """
        Wait for a random amount of time between min_time and max_time
        
        Args:
            min_time (float): Minimum time to wait in seconds
            max_time (float, optional): Maximum time to wait in seconds
            
        Returns:
            float: Actual time waited in seconds
        """
        if max_time is None:
            max_time = min_time * 1.5
            
        delay = self.get_random_delay(min_time, max_time)
        time.sleep(delay)
        return delay 