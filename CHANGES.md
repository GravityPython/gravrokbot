# Changes

## Version 0.1.0 (Unreleased)

### Added
- Added built-in delay system for transitions in the state machine workflow
- Delays can be configured with minimum and maximum values for randomization
- Pre-execution delays happen before a state transition callback
- Post-execution delays happen after a state transition callback 
- Added predefined delay profiles for common action types
- Support for custom delay profiles via configuration
- Updated all existing actions to use the new delay system
- Added documentation for using delays in custom actions
- Created test cases for the delay system

### Changed
- Refactored action code to remove inline delay calls 
- Modified screen interaction's humanized_wait to return the actual wait time
- Updated package structure for better organization
- Simplified action implementations by using delay profiles

### Fixed
- Fixed potential timing issues by centralizing all delay logic in transitions
- Improved human-like behavior with more configurable randomized delays 

## Summary of the Delay Profiles Feature

We've enhanced GravRokBot with a flexible delay profiles system that makes it easier to configure realistic delays between actions. Here's what we've implemented:

1. **Built-in Delay Profiles**:
   - Quick profile for simple, fast actions
   - Normal profile for standard actions
   - Verification profile for checking results
   - Long wait profile for actions that need extended waiting time
   - Menu navigation profile for UI interactions

2. **Three Ways to Configure Delays**:
   - Use predefined profiles: `profile='normal'`
   - Use custom delay values: `pre_delay_min=0.5, pre_delay_max=1.0`
   - Combine profiles with custom overrides: `profile='normal', post_delay_min=2.0`

3. **Configurable via JSON**:
   - Global delay profiles in the main configuration
   - Action-specific delay profiles for fine-tuning

4. **Updated Action Implementation**:
   - Cleaner, more readable action code
   - Actions can reference profiles by name
   - Standardized timing across similar types of actions

This feature makes the bot more:
- **Maintainable**: Timing settings are centralized and easily changed
- **Realistic**: Consistent but randomized delays for human-like behavior 
- **Customizable**: Users can adjust timing profiles to match their game's performance
- **Extensible**: New actions can reuse existing profiles for consistent behavior

### Example of Using Delay Profiles

Before:
```python
def setup_transitions(self):
    self.add_transition_with_delays(
        'find_resource', 'starting', 'detecting', 
        pre_delay_min=0.5, pre_delay_max=1.0,
        post_delay_min=0.8, post_delay_max=1.2,
        after='on_find_resource'
    )
    # ...multiple other transitions with hardcoded delays
```

After:
```python
def setup_transitions(self):
    self.add_transition_with_delays(
        'find_resource', 'starting', 'detecting', 
        profile='normal',  # Use predefined profile
        after='on_find_resource'
    )
    # ...cleaner, more consistent transitions
```

This improvement makes GravRokBot more flexible and user-friendly while maintaining its human-like interaction patterns.

Don't forget to commit!
```
git commit -m "Feat(workflow): add delay profiles for easier action configuration"
``` 