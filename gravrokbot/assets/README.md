# GravRokBot Asset Images

This directory contains the image assets used by GravRokBot to detect and interact with the Rise of Kingdoms game.

## Required Images

### Gather Resources Action
- `gather_button.png`: The button to gather resources
- `resource_icon.png`: Icon representing resources on the map
- `march_button.png`: The march button to send troops
- `gather_confirmation.png`: Confirmation that gathering has started

### Collect City Resources Action
- `city_view.png`: Image to identify that we're in the city view
- `farm.png`: Farm building
- `lumber_camp.png`: Lumber camp building
- `quarry.png`: Quarry building
- `gold_mine.png`: Gold mine building
- `collect_all.png`: The collect all button if available
- `collect_confirmation.png`: Confirmation that resources were collected

### Change Character Action
- `settings_button.png`: The settings button
- `character_button.png`: The character selection button
- `switch_button.png`: Button to switch characters
- `switch_confirmation.png`: Confirmation that character was switched

### Close Game Action
- `settings_button.png`: The settings button
- `exit_button.png`: Button to exit the game
- `exit_confirmation.png`: Confirmation dialog for exiting

### Start Game Action
- `game_icon.png`: The game icon on desktop/start menu
- `start_button.png`: Button to start the game
- `login_button.png`: Button to login to the game

## Image Requirements

For best results, capture these images:
1. At the same resolution as your game (1600x900)
2. With clear visibility of the button/icon
3. Without any overlapping elements
4. In PNG format with transparency if possible
5. Cropped tightly to the relevant element

## Adding Custom Images

If adding custom images, update the `config/settings.json` file to point to your custom images.