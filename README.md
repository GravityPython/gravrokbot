# GravRokBot

A bot for automating actions in "Rise of Kingdoms" game with human-like interactions. This bot uses computer vision to detect game elements and simulates human-like interaction with random delays and movements.

## Features

- Automated game actions with human-like behavior
- Customizable timers and action schedules
- Activity logging and monitoring
- Easy to extend with new actions
- Built-in delay system for realistic timing between actions
- Predefined delay profiles for common actions
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
- Delay profiles for customizing action timing

### Delay Profiles

Delay profiles define sets of timing parameters that can be reused across different actions:

```json
"delay_profiles": {
  "slow_game": {
    "pre_delay_min": 1.0,
    "pre_delay_max": 2.0,
    "post_delay_min": 1.5,
    "post_delay_max": 3.0
  },
  "fast_game": {
    "pre_delay_min": 0.2,
    "pre_delay_max": 0.4,
    "post_delay_min": 0.3,
    "post_delay_max": 0.6
  }
}
```

You can define global profiles at the root level and action-specific profiles within each action:

```json
"actions": {
  "gather_resources": {
    "delay_profiles": {
      "resource_search": {
        "pre_delay_min": 0.5,
        "pre_delay_max": 1.0,
        "post_delay_min": 1.0, 
        "post_delay_max": 2.0
      }
    }
  }
}
```

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

The bot has a built-in delay system to create realistic timing between actions. There are three ways to add delays:

#### 1. Using Predefined Profiles

```python
def setup_transitions(self):
    self.add_transition_with_delays(
        'find_button', 'starting', 'detecting',
        profile='normal',  # Use predefined 'normal' profile
        after='on_find_button'
    )
```

#### 2. Using Custom Delay Values

```python
def setup_transitions(self):
    self.add_transition_with_delays(
        'find_button', 'starting', 'detecting',
        pre_delay_min=0.5, pre_delay_max=1.0,  # Custom pre-execution delay
        post_delay_min=0.8, post_delay_max=1.2,  # Custom post-execution delay
        after='on_find_button'
    )
```

#### 3. Using Profile with Overrides

```python
def setup_transitions(self):
    self.add_transition_with_delays(
        'find_button', 'starting', 'detecting',
        profile='normal',  # Use the base profile
        post_delay_min=2.0, post_delay_max=3.0,  # Override just the post-delay
        after='on_find_button'
    )
```

### Built-in Delay Profiles

The system comes with several built-in profiles:

- `quick`: Short delays for simple actions (0.2-0.5s pre, 0.3-0.6s post)
- `normal`: Standard delays for most actions (0.5-1.0s pre, 0.8-1.2s post)
- `verification`: Delays for verification steps (0.5-1.0s pre, 0.2-0.4s post)
- `long_wait`: Longer post-delays for actions that need time (0.3-0.6s pre, 2.0-3.0s post)
- `menu_navigation`: Delays for menu navigation (0.3-0.7s pre, 1.0-1.5s post)

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
            profile='normal',
            after='on_first_step'
        )
        
        self.add_transition_with_delays(
            'second_step', 'detecting', 'clicking',
            profile='menu_navigation',
            after='on_second_step'
        )
        
        self.add_transition_with_delays(
            'check_result', 'clicking', 'verifying',
            profile='long_wait',
            after='on_check_result'
        )
        
        self.add_transition_with_delays(
            'finish', 'verifying', 'succeeded', 
            profile='verification',
            conditions=['is_successful'], 
            after='on_success'
        )
        
        self.add_transition_with_delays(
            'finish', 'verifying', 'failed', 
            profile='verification',
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
