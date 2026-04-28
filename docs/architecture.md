# Architecture

## Package Diagram

![Package Diagram](./images/package_diagram.png)

(Each package is described in detail inside their respective READMEs (for ex. src/ui/README.md) )

Each package has a primary class which is injected as a dependency.

- Package _ui_ contains pygame UI code
- Package _state_ contains objects to control the game's state
- Package _blueprint_ contains code to load game configuration
- Package _save_ contains code to load player saves

## Description

The game first loads blueprints from a default .json file.
Blueprints define how all elements of the game work.
They for example define which machines, recipes and defaults the game has.
Once those are loaded, they are passed to the `GameState` instance, which uses
them to progress the game.

The game separates the game logic into a simple `state` package.
There is a single primary `GameState` instance, which has
references to blueprints and for example the tiles (machines).

State is injected into `GameUI`, which uses it as a source of truth to draw the UI.
The UI also calls `GameState#update(delta: float)`,
which in turn propagates the updates to machines.
Machines use the delta to calculate when recipes
are complete using a timer.

