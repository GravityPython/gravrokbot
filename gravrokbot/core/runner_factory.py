"""
Factory function to create the appropriate runner
"""

from gravrokbot.core.action_runner import ActionRunner
from gravrokbot.core.test_runner import TestRunner

def create_runner(main_window, config):
    """
    Factory function to create the appropriate runner
    
    Args:
        main_window: Main window instance for UI updates
        config (dict): Configuration dictionary with runner settings
        
    Returns:
        BotRunner: An instance of a runner (either ActionRunner or TestRunner)
    """
    test_mode_enabled = config.get("test_mode", {}).get("enabled", False)
    
    if test_mode_enabled:
        return TestRunner(main_window, config)
    else:
        return ActionRunner(main_window, config) 