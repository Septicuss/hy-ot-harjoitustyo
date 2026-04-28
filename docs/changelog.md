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

## Week 5

- `refactor(blueprint):` Changed the blueprint schema so that crops are also recipes, instead of separate objects
- `feat(state):` Implemented the game state machine flow, so that items can be added and crafted
- `feat(ui):` Implemented dragging and dropping items onto machines
- `test(state):` Implemented more tests for the state

Result of this week was to make the state be able to handle future ui interactions,
like adding items to machines and preparing items. 

## Week 6


- `feat(ui/state):` Finalized tile system, where all machines are on a 3x3 grid. Includes detection via hitboxes and loading default tiles.
- `feat(blueprint):` Recipes can now have amounts, so that a farm returns double the crops planted
- `feat(ui):` Added tooltips, that when hovering over a machine show its live status (recipes & crafting progress)

This week has mostly been UI work and finishing up the crafting system. 
The result is a demo in which you are given a crop of each type, can plant them to grow
more and then refine them in bakery or juice machine.

