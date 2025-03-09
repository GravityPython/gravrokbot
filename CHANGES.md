# Changes

## Version 0.1.0 (Unreleased)

### Added
- Added built-in delay system for transitions in the state machine workflow
- Delays can be configured with minimum and maximum values for randomization
- Pre-execution delays happen before a state transition callback
- Post-execution delays happen after a state transition callback 
- Updated all existing actions to use the new delay system
- Added documentation for using delays in custom actions
- Created test cases for the delay system

### Changed
- Refactored action code to remove inline delay calls 
- Modified screen interaction's humanized_wait to return the actual wait time
- Updated package structure for better organization

### Fixed
- Fixed potential timing issues by centralizing all delay logic in transitions
- Improved human-like behavior with more configurable randomized delays 