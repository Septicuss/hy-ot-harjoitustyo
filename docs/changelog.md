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

## Week 7

- `feat(ui):` Improve tooltips (padding / style, recipe names, icons)
- `feat(ui):` Implement crop growth stages based on progress in farmland
- `feat(ui/state):` Items have to now be picked up from machines, instead of automatically being ready
- `feat(ui):` Notification toasts appear in bottom right corner. They have variants success/error/default.
- `feat(ui):` Added HUD to display player coins (with a tooltip to explain what they are)
- `feat(ui/state):` Added an order system. In the bottom left there is a tile, onto which orders can be dragged and completed. Shows a user friendy tooltip on hover.
- `feat(ui/state):` Added a system for locked tiles, which can be unlocked with coins
- `feat(save/state):` Added a save slot system, which loads and saves the state as JSON files
- `test(state):` Added tests for orders, state (e2e tests) and saves
- `chore/refactor:` Cleaned up the project, refactored classes into their own files

Must be a common occurrence in university projects like these to
implement such primary systems so late, but only in recent weeks have
I fully gained clarity into what this game should play like.
The result of this week is a functioning, mostly polished game.