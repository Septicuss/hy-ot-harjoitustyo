# Changelog

## Week 3

- Defined how game data and savefiles are structured in JSON
- Defined project structure, with documented READMEs in each source directory
- Implemented game data loading, validation and tests

## Week 4

- `refactor:` Refactored module names to better reflect usage `data` -> `blueprint`, `game` -> `state`
- `feat:` Expanded game blueprints to include game constants & sprite mappings
- `feat:` Added sprite loading system: sprites are mapped to items in blueprints and loaded in the UI
- `feat:` Added tests for constant and sprite blueprints
- `feat:` Initial game state and UI.
- `chore`: Drew the game sprites :P

Result of this week is a simple demo, which allows the user to click to switch selected item in the hotbar.
In the next weeks interaction with the hotbar & items will be more defined.
