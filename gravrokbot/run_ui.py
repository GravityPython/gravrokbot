#!/usr/bin/env python3
"""
Entry point for the GravRokBot UI
"""

import os
import sys
import logging
import colorlog

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def setup_logging():
    """Configure logging with colors"""
    handler = colorlog.StreamHandler()
    handler.setFormatter(colorlog.ColoredFormatter(
        '%(log_color)s%(asctime)s [%(levelname)s] %(message)s',
        datefmt='%H:%M:%S',
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red,bg_white',
        }
    ))

    logger = logging.getLogger('gravrokbot')
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return logger

def main():
    """Main entry point"""
    logger = setup_logging()
    logger.info("Starting GravRokBot UI...")
    
    try:
        from gravrokbot.ui.main_window import MainWindow
        app = MainWindow()
        app.run()
    except Exception as e:
        logger.error(f"Failed to start UI: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 