import os
import time
import random
import logging
import pyautogui
import cv2
import numpy as np
import pytesseract
from PIL import Image

class ScreenInteraction:
    """Base class for screen interaction with human-like behavior"""
    
    def __init__(self, config):
        """
        Initialize screen interaction with config
        
        Args:
            config (dict): Configuration dictionary with settings
        """
        self.config = config
        self.screen_width, self.screen_height = pyautogui.size()
        self.last_action_time = time.time()
        
        # Initialize PyAutoGUI settings
        pyautogui.PAUSE = self.config.get('input_delay', 0.1)
        pyautogui.FAILSAFE = True
        
        # Configure logger
        self.logger = logging.getLogger("GravRokBot")
    
    def take_screenshot(self, region=None):
        """
        Take a screenshot of the specified region or full screen
        
        Args:
            region (tuple, optional): Region to capture (left, top, width, height)
            
        Returns:
            PIL.Image: Screenshot image
        """
        self.logger.debug(f"Taking screenshot{f' of region {region}' if region else ''}")
        return pyautogui.screenshot(region=region)
    
    def find_image(self, image_path, confidence=0.8, region=None, grayscale=True):
        """
        Find an image on screen
        
        Args:
            image_path (str): Path to image file to find
            confidence (float): Match confidence threshold (0-1)
            region (tuple, optional): Region to search in (left, top, width, height)
            grayscale (bool): Whether to search in grayscale
            
        Returns:
            tuple: (x, y) position of center if found, None otherwise
        """
        if not os.path.exists(image_path):
            self.logger.error(f"Image not found: {image_path}")
            return None
            
        self.logger.debug(f"Searching for image: {os.path.basename(image_path)}")
        try:
            location = pyautogui.locateCenterOnScreen(
                image_path, 
                confidence=confidence,
                region=region,
                grayscale=grayscale
            )
            
            if location:
                self.logger.debug(f"Found image at {location}")
            else:
                self.logger.debug(f"Image not found: {os.path.basename(image_path)}")
                
            return location
        except Exception as e:
            self.logger.error(f"Error finding image: {e}")
            return None
    
    def find_all_images(self, image_path, confidence=0.8, region=None, grayscale=True):
        """
        Find all instances of an image on screen
        
        Args:
            image_path (str): Path to image file to find
            confidence (float): Match confidence threshold (0-1)
            region (tuple, optional): Region to search in (left, top, width, height)
            grayscale (bool): Whether to search in grayscale
            
        Returns:
            list: List of (x, y) positions of matches
        """
        if not os.path.exists(image_path):
            self.logger.error(f"Image not found: {image_path}")
            return []
            
        self.logger.debug(f"Searching for all instances of image: {os.path.basename(image_path)}")
        try:
            locations = list(pyautogui.locateAllOnScreen(
                image_path, 
                confidence=confidence,
                region=region,
                grayscale=grayscale
            ))
            
            positions = [pyautogui.center(loc) for loc in locations]
            self.logger.debug(f"Found {len(positions)} instances")
            return positions
        except Exception as e:
            self.logger.error(f"Error finding images: {e}")
            return []
    
    def extract_text(self, region):
        """
        Extract text from a screen region using OCR
        
        Args:
            region (tuple): Region to extract text from (left, top, width, height)
            
        Returns:
            str: Extracted text
        """
        self.logger.debug(f"Extracting text from region {region}")
        try:
            screenshot = self.take_screenshot(region)
            text = pytesseract.image_to_string(screenshot)
            self.logger.debug(f"Extracted text: {text.strip()}")
            return text.strip()
        except Exception as e:
            self.logger.error(f"Error extracting text: {e}")
            return ""
    
    def humanized_click(self, x, y, button='left', randomize=True, randomize_range=10):
        """
        Perform a mouse click with human-like behavior
        
        Args:
            x (int): Target X coordinate
            y (int): Target Y coordinate
            button (str): 'left' or 'right' mouse button
            randomize (bool): Whether to randomize click position
            randomize_range (int): Maximum random offset in pixels
        """
        # Add random offset to make it look more human-like
        if randomize:
            x += random.randint(-randomize_range, randomize_range)
            y += random.randint(-randomize_range, randomize_range)
        
        # Ensure coordinates are within screen bounds
        x = max(0, min(x, self.screen_width - 1))
        y = max(0, min(y, self.screen_height - 1))
        
        # Random duration for mouse movement (human-like)
        move_duration = random.uniform(0.3, 0.7)
        
        self.logger.debug(f"Moving mouse to ({x}, {y})")
        pyautogui.moveTo(x, y, duration=move_duration)
        
        # Random delay before clicking
        time.sleep(random.uniform(0.1, 0.3))
        
        self.logger.debug(f"Clicking {button} mouse button")
        pyautogui.click(button=button)
        
        # Update last action time
        self.last_action_time = time.time()
    
    def find_and_click_image(self, image_path, confidence=0.8, region=None, grayscale=True):
        """
        Find an image on screen and click it
        
        Args:
            image_path (str): Path to image file to find
            confidence (float): Match confidence threshold (0-1)
            region (tuple, optional): Region to search in (left, top, width, height)
            grayscale (bool): Whether to search in grayscale
            
        Returns:
            bool: True if image was found and clicked, False otherwise
        """
        location = self.find_image(image_path, confidence, region, grayscale)
        if location:
            self.humanized_click(*location)
            return True
        return False
    
    def humanized_type(self, text, interval=None):
        """
        Type text with human-like timing
        
        Args:
            text (str): Text to type
            interval (float, optional): Typing interval, randomized if None
        """
        if interval is None:
            # Random typing speed
            interval = random.uniform(0.05, 0.15)
        
        self.logger.debug(f"Typing text: {text}")
        pyautogui.typewrite(text, interval=interval)
        
        # Update last action time
        self.last_action_time = time.time()
    
    def humanized_wait(self, min_seconds, max_seconds):
        """
        Wait for a random amount of time within range
        
        Args:
            min_seconds (float): Minimum seconds to wait
            max_seconds (float): Maximum seconds to wait
            
        Returns:
            float: Actual time waited in seconds
        """
        wait_time = random.uniform(min_seconds, max_seconds)
        self.logger.debug(f"Waiting for {wait_time:.2f} seconds")
        time.sleep(wait_time)
        return wait_time
    
    def press_key(self, key):
        """
        Press a keyboard key
        
        Args:
            key (str): Key to press
        """
        self.logger.debug(f"Pressing key: {key}")
        pyautogui.press(key)
        
        # Update last action time
        self.last_action_time = time.time() 