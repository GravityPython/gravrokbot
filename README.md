# GravRokBot

A bot for automating actions in "Rise of Kingdoms" game with human-like interactions. This bot uses computer vision to detect game elements and simulates human-like interaction with random delays and movements.

## Features

- Automated game actions with human-like behavior
- Customizable timers and action schedules
- Activity logging and monitoring
- Easy to extend with new actions
- Built-in delay system for realistic timing between actions
- Support for multiple automated tasks:
  - Gather resources
  - Collect city resources
  - Change characters
  - Close game
  - Start game

## Requirements

- Python 3.9+
- PyAutoGUI
- OpenCV
- Tesseract OCR (must be installed separately on the system)
- PyQt6
- Transitions

## Setup

1. Clone this repository:
```
git clone https://github.com/yourusername/gravrokbot.git
cd gravrokbot
```

2. Install requirements:
```
pip install -r requirements.txt
```

3. Install Tesseract OCR:
   - Windows: Download installer from https://github.com/UB-Mannheim/tesseract/wiki
   - MacOS: `brew install tesseract`
   - Linux: `sudo apt install tesseract-ocr`

4. Place game reference images in the `gravrokbot/assets/images/` directory (see assets README for details)

5. Configure settings in `gravrokbot/config/settings.json` (or use the UI)

6. Run the application:
```
python -m gravrokbot
```

## Configuration

All settings are stored in `gravrokbot/config/settings.json` and can be modified through the UI. The configuration includes:

- Runner settings: refresh rate, night sleep, coffee breaks
- Action settings: cooldown, retries, wait times
- Image paths for game element detection

## How to Use

1. Start the bot using the command above or by creating a shortcut
2. Enable/disable actions as needed in the UI
3. Click "Start Bot" to begin automation
4. Monitor activity in the log window
5. Stop the bot at any time with the "Stop Bot" button

## Extending with New Actions

GravRokBot is designed to be easily extended with new game actions. To create a new action:

1. Create a new Python file in the `gravrokbot/actions/` directory
2. Subclass the `ActionWorkflow` base class
3. Define the state machine transitions in `setup_transitions()`
4. Implement the required handler methods
5. Add your action to `gravrokbot/gravrokbot.py` in the `initialize_bot()` function

### Using the Delay System

The bot has a built-in delay system to create realistic timing between actions. Delays can be added directly in the transition definition:

```python
def setup_transitions(self):
    """Setup your action's transitions with delays"""
    self.add_transition_with_delays(
        'find_button', 'starting', 'detecting',
        pre_delay_min=0.5, pre_delay_max=1.0,  # Delay before executing
        post_delay_min=0.8, post_delay_max=1.2,  # Delay after executing
        after='on_find_button'
    )
    
    # Additional transitions...
```

This creates randomized delays both before and after each step to make the bot's actions appear more human-like and account for game execution delays.

### Example Action Template

```python
# gravrokbot/actions/my_new_action.py
import os
from gravrokbot.core.action_workflow import ActionWorkflow

class MyNewAction(ActionWorkflow):
    def __init__(self, screen_interaction, config):
        super().__init__("My New Action", screen_interaction, config)
    
    def setup_transitions(self):
        self.add_transition_with_delays(
            'first_step', 'starting', 'detecting', 
            pre_delay_min=0.5, pre_delay_max=1.0,
            post_delay_min=0.8, post_delay_max=1.2,
            after='on_first_step'
        )
        
        self.add_transition_with_delays(
            'second_step', 'detecting', 'clicking',
            pre_delay_min=0.3, pre_delay_max=0.6,
            post_delay_min=1.0, post_delay_max=1.5, 
            after='on_second_step'
        )
        
        self.add_transition_with_delays(
            'check_result', 'clicking', 'verifying',
            pre_delay_min=1.0, pre_delay_max=2.0,
            post_delay_min=0.5, post_delay_max=1.0,  
            after='on_check_result'
        )
        
        self.add_transition_with_delays(
            'finish', 'verifying', 'succeeded', 
            pre_delay_min=0.5, pre_delay_max=1.0,
            conditions=['is_successful'], 
            after='on_success'
        )
        
        self.add_transition_with_delays(
            'finish', 'verifying', 'failed', 
            pre_delay_min=0.5, pre_delay_max=1.0,
            unless=['is_successful'], 
            after='on_failure'
        )
    
    def on_start(self):
        self.logger.info("Starting my new action")
        self.first_step()
    
    # Implement other handler methods...
```

Then update the main application:

```python
# In gravrokbot/gravrokbot.py
from gravrokbot.actions.my_new_action import MyNewAction

# In initialize_bot function
if 'my_new_action' in config['actions']:
    my_action = MyNewAction(screen, config['actions']['my_new_action'])
    runner.add_action(my_action)
```

## Development

Run tests to ensure everything works:

```
python -m unittest discover tests
```

## License

MIT License - See LICENSE file for details

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
