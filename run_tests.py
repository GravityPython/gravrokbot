#!/usr/bin/env python3
"""
Test runner for GravRokBot
"""

import os
import sys
import unittest

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def run_tests():
    """Run all tests in the tests directory"""
    test_loader = unittest.TestLoader()
    test_suite = test_loader.discover('tests', pattern='test_*.py')
    
    test_runner = unittest.TextTestRunner(verbosity=2)
    result = test_runner.run(test_suite)
    
    return not result.failures and not result.errors

if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1) 