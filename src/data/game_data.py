import json
from pathlib import Path
from typing import Self

from data.game_elements import (
    Crop,
    Recipe,
    Machine, GameElement
)


class GameData:
    def __init__(self, crops: list[Crop], recipes: list[Recipe], machines: list[Machine]):
        self.crops = crops
        self.recipes = recipes
        self.machines = machines

    @classmethod
    def load_from_file(cls, file_path: str) -> Self | None:
        path = Path(file_path)
        with path.open() as file:
            return GameData.load_from_json(json_data=str(file.read()))

    @classmethod
    def load_from_json(cls, json_data: str) -> Self | None:
        data = json.loads(json_data)

        loaded_crops = []
        loaded_recipes = []
        loaded_machines = []

        if "crops" in data:
            loaded_crops = [Crop.from_dict(crop_data) for crop_data in data["crops"]]

        if "recipes" in data:
            loaded_recipes = [Recipe.from_dict(recipe_data) for recipe_data in data["recipes"]]

        if "machines" in data:
            loaded_machines = [Machine.from_dict(machine_data) for machine_data in data["machines"]]

        game_data = GameData(
            loaded_crops,
            loaded_recipes,
            loaded_machines
        )

        # Validate loaded data
        cls.__validate_or_throw(game_data)

        return game_data

    @classmethod
    def __validate_or_throw(cls, game_data: Self):

        # 1. Ensure that each game element ID is unique
        def ensure_unique_ids(elements: list[GameElement]):
            unique_ids = set([element.id for element in elements])
            if len(unique_ids) != len(elements):
                raise ValueError("duplicate ids")

        ensure_unique_ids(game_data.crops)
        ensure_unique_ids(game_data.recipes)
        ensure_unique_ids(game_data.machines)

        # 2. Ensure that each item reference exists
        all_item_ids = [element.id for element in [*game_data.crops, *game_data.recipes, *game_data.machines]]

        for recipe in game_data.recipes:
            for recipe_reference in recipe.recipe:
                if recipe_reference.id not in all_item_ids:
                    raise ValueError(f"recipe '{recipe.id}' uses an unknown reference '{recipe_reference.id}'")

        for machine in game_data.machines:
            for recipe_id in machine.recipes:
                if recipe_id.id not in all_item_ids:
                    raise ValueError(f"machine '{machine.id}' uses an unknown reference '{recipe_id.id}'")
