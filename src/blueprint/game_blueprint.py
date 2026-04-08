import json
from pathlib import Path
from typing import Self

from blueprint.blueprints import (
    CropBlueprint,
    RecipeBlueprint,
    MachineBlueprint,
    GameElementBlueprint
)


class GameBlueprint:
    """Represents a blueprint, containing smaller blueprints of in-game elements.
    As arguments takes a list of each type of game element blueprint.

    Args:
        crops: list of CropBlueprint
        recipes: list of RecipeBlueprint
        machines: list of MachineBlueprint
    """

    def __init__(self, crops: list[CropBlueprint], recipes: list[RecipeBlueprint], machines: list[MachineBlueprint]):
        self.crops = crops
        self.recipes = recipes
        self.machines = machines

    @classmethod
    def load_from_file(cls, file_path: str) -> Self | None:
        """Loads game JSON blueprint into a GameData class from a JSON file"""

        path = Path(file_path)
        with path.open() as file:
            return GameBlueprint.load_from_json(json_data=str(file.read()))

    @classmethod
    def load_from_json(cls, json_data: str) -> Self | None:
        """Loads game blueprint into a GameBlueprint class from a JSON string

        This method will throw a ValueError if blueprint validation fails.
        """

        data = json.loads(json_data)

        loaded_crops = []
        loaded_recipes = []
        loaded_machines = []

        if "crops" in data:
            loaded_crops = [CropBlueprint.from_dict(crop_data) for crop_data in data["crops"]]

        if "recipes" in data:
            loaded_recipes = [RecipeBlueprint.from_dict(recipe_data) for recipe_data in data["recipes"]]

        if "machines" in data:
            loaded_machines = [MachineBlueprint.from_dict(machine_data) for machine_data in data["machines"]]

        game_blueprint = GameBlueprint(
            loaded_crops,
            loaded_recipes,
            loaded_machines
        )

        # Validate loaded blueprint
        cls.__validate_or_throw(game_blueprint)

        return game_blueprint

    @classmethod
    def __validate_or_throw(cls, game_blueprint: Self):
        """Internal method to validate the loaded game blueprint so that it can be safely used at runtime."""

        # 1. Ensure that each game element ID is unique
        def ensure_unique_ids(elements: list[GameElementBlueprint]):
            unique_ids = set([element.id for element in elements])
            if len(unique_ids) != len(elements):
                raise ValueError("duplicate ids")

        ensure_unique_ids(game_blueprint.crops)
        ensure_unique_ids(game_blueprint.recipes)
        ensure_unique_ids(game_blueprint.machines)

        # 2. Ensure that each item reference exists
        all_item_ids = [element.id for element in [*game_blueprint.crops, *game_blueprint.recipes, *game_blueprint.machines]]

        for recipe in game_blueprint.recipes:
            for recipe_reference in recipe.recipe:
                if recipe_reference.id not in all_item_ids:
                    raise ValueError(f"recipe '{recipe.id}' uses an unknown reference '{recipe_reference.id}'")

        for machine in game_blueprint.machines:
            for recipe_id in machine.recipes:
                if recipe_id.id not in all_item_ids:
                    raise ValueError(f"machine '{machine.id}' uses an unknown reference '{recipe_id.id}'")
