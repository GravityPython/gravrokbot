#!/usr/bin/env python3
import os
import sys
import logging
from pathlib import Path

# Get the project root directory (parent of gravrokbot package)
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

# Configure basic logging before importing other modules
logging.basicConfig(
    level=logging.DEBUG,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger = logging.getLogger(__name__)

def run_tester():
    try:
        from gravrokbot.testing.ui_tester import main
        main()
    except ImportError as e:
        logger.error(f"Error importing modules: {e}")
        logger.error(f"Python path: {sys.path}")
        logger.error("Make sure you have installed the package in development mode: pip install -e .")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    run_tester()