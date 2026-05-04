# Usage Guide

Download the [latest releases](https://github.com/Septicuss/hy-ot-harjoitustyo/releases/latest) source code.

## Configuration

This step is entirely optional. The game has some default configurations,
which include various gameplay items like recipes and machines. 
If you wish to edit these values (and as such, the game itself), you can modify `blueprints.json`
file in `src/blueprint/blueprint.json`.

There are several sub categories for blueprints in the file:
```json
{
  "constants": {...} // variables constants
  "sprites": {...} // mappings of bitmap sprites in an 8x8 grid
  "recipes": {...} // all items, their recipes and properties
  "machines": {...} // machine properties, namely defining which recipes they can craft
}
```

## Starting the application

1. Install dependencies, while in the root of the project:

```
poetry install
```

2. Start the application:

```
poetry run invoke start
```

## The game

[TODO: Final game UI guide]