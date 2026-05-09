# Testing

## Unit tests

**Unit tests focus on testing the *state*, *blueprints* and *saves*.** Separate classes are tested in separate documents.
Tests attempt in most cases to resemble the real use case (default game configuration) and in case of blueprints all
invalid scenarios are tested.

### Blueprints

Blueprints are easily testable, as they can be loaded for raw JSON strings.
Blueprints also have runtime validation, which raises a `ValueError` 
if the configuration is incorrect (otherwise the game could not function properly)

In most of the blueprint tests, we test for specific error messages like `"duplicate ids"` or `"recipe 'wheat' did not have sprite"`.
For blueprint methods that also have to map JSON syntax to blueprint dataclasses, the tests ensure that those are correct.

Utility functions in blueprints, such as `GameBlueprint#get_matching_recipes()` are also tested on the real game blueprints.

### Saves

Saves are tested in a unique way. We have to ensure that the saves we output are correct and that slots actually exist.
This testing is done as close as possible to the real environment through having the saves actually load and save real files.
On each test, the `src/tests/saves/test` directory gets cleared. 
Test cases are directories with save slot files ie. `.../tests/saves/1/slot_[x].json` for test case 1, which during
a test are copied into the `src/tests/saves/test` directory and are then tested.

### State

For state, we test the core state objects like `Inventory` and `Orders`, state utility functions and the full state.
State is tested by simulating the inputs of the UI, like adding an item to a machine, calling `#update(time)` until
the recipe is complete and then trying to collect the result.

Because we test all dependencies of a state like blueprints and saves, we can do larger end-to-end tests for `GameState`.
There are currently two primary tests, which use the default blueprint and an empty save. 

1. Testing planting a crop, waiting for it to grow and collecting it. 
Tests ensure that it's not ready too soon and that the state variables are updated correctly.
2. Testing unlocking tiles. 
Tests ensure that tiles marked as locked in the blueprint are correctly initialized to be locked, and buying with insufficient balance fails.

### Coverage

<img width="1277" height="635" alt="image" src="https://github.com/user-attachments/assets/3623401e-9985-473e-9403-1fc977a63d66" />
Coverage is about 90%, with most of the missing coverage being specific state scenarios that are not a priority.

## Manual Tests

The game has been developed by iteratively adding on things and testing them in-game right away.
Manual tests include playing the game and trying to break things, by for example placing items in wrong places.
The state and UI are pretty restrictive in what is allowed, plus the UI and game is somewhat simple, so large issues are unlikely.
