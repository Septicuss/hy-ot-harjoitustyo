# Blueprint

This module contains the primitives and logic to load **blueprints**. 

**Blueprints** are:
- descriptions of in-game elements and how they work
- loaded from .json files
- used during the games runtime

**Blueprints**:
- Crops
- Recipes
- Machines

**Module responsibilities**
- Loading of blueprints, either from raw JSON of .json files
- Defining types of blueprints and their properties
- Validating the correctness of blueprints:
  - Ensuring that item references refer to existing items
  - Ensuring that item IDs are unique

Default game blueprint is stored in `blueprint.json`. It is validated at runtime and via tests.