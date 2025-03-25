import os
import cv2
import numpy as np
from PIL import Image
import logging

logger = logging.getLogger("GravRokBot.ImageUtils")

def load_image(image_path):
    """
    Load an image from disk
    
    Args:
        image_path (str): Path to image
        
    Returns:
        PIL.Image: Loaded image or None if failed
    """
    try:
        return Image.open(image_path)
    except Exception as e:
        logger.error(f"Error loading image {image_path}: {e}")
        return None

def pil_to_cv2(pil_image):
    """
    Convert PIL image to OpenCV format
    
    Args:
        pil_image (PIL.Image): PIL image
        
    Returns:
        numpy.ndarray: OpenCV image
    """
    return cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)

def cv2_to_pil(cv2_image):
    """
    Convert OpenCV image to PIL format
    
    Args:
        cv2_image (numpy.ndarray): OpenCV image
        
    Returns:
        PIL.Image: PIL image
    """
    return Image.fromarray(cv2.cvtColor(cv2_image, cv2.COLOR_BGR2RGB))

def enhance_image_for_ocr(image):
    """
    Enhance an image for better OCR results
    
    Args:
        image (PIL.Image): Input image
        
    Returns:
        PIL.Image: Enhanced image
    """
    # Convert to OpenCV format
    img = pil_to_cv2(image)
    
    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Apply thresholding
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
    # Apply dilation and erosion to remove noise
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
    processed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
    
    # Convert back to PIL format
    return cv2_to_pil(processed)

def highlight_matches(screenshot, template, matches, threshold=0.8):
    """
    Highlight matches on a screenshot for debugging
    
    Args:
        screenshot (PIL.Image): Screenshot image
        template (PIL.Image): Template image to find
        matches (list): List of match locations
        threshold (float): Match threshold
        
    Returns:
        PIL.Image: Image with highlighted matches
    """
    # Convert to OpenCV format
    img = pil_to_cv2(screenshot)
    tpl = pil_to_cv2(template)
    
    # Get template dimensions
    h, w = tpl.shape[:2]
    
    # Draw rectangles around matches
    for match in matches:
        x, y = match
        top_left = (int(x - w/2), int(y - h/2))
        bottom_right = (int(x + w/2), int(y + h/2))
        cv2.rectangle(img, top_left, bottom_right, (0, 255, 0), 2)
        
        # Add confidence text
        cv2.putText(img, f"{threshold:.2f}", (top_left[0], top_left[1] - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
    
    # Convert back to PIL format
    return cv2_to_pil(img)

def save_debug_image(image, filename):
    """
    Save an image for debugging purposes
    
    Args:
        image (PIL.Image): Image to save
        filename (str): Filename to save to
    """
    debug_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "debug")
    os.makedirs(debug_dir, exist_ok=True)
    
    file_path = os.path.join(debug_dir, filename)
    image.save(file_path)
    logger.debug(f"Saved debug image: {file_path}")
    
    return file_path 