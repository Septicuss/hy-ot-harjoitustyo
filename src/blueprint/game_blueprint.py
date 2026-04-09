import json
from pathlib import Path
from typing import Self

from blueprint.blueprints import (
    CropBlueprint,
    RecipeBlueprint,
    MachineBlueprint,
    GameElementBlueprint,
    ConstantsBlueprint
)


class GameBlueprint:
    """Represents a blueprint, containing smaller blueprints of in-game elements.
    As arguments takes a list of each type of game element blueprint.

    Args:
        constants: ConstantsBlueprint
        crops: list of CropBlueprint
        recipes: list of RecipeBlueprint
        machines: list of MachineBlueprint
    """

    def __init__(self, constants: ConstantsBlueprint, crops: list[CropBlueprint], recipes: list[RecipeBlueprint], machines: list[MachineBlueprint]):
        self.constants = constants
        self.crops: dict[str, CropBlueprint] = {crop.id: crop for crop in crops}
        self.recipes: dict[str, RecipeBlueprint] = {recipe.id: recipe for recipe in recipes}
        self.machines: dict[str, MachineBlueprint] = {machine.id: machine for machine in machines}

    def get_required_machine_slots(self, machine_id: str) -> int:
        machine: MachineBlueprint = self.machines.get(machine_id)

        if not machine:
            raise ValueError(f"Tried to get the required slots of a non-existent machine '{machine_id}'")

        required_slots: int = 0

        for recipe_reference in machine.recipes:
            recipe_blueprint = self.recipes.get(recipe_reference.id)
            required_slots = max(required_slots, len(recipe_blueprint.recipe))

        return required_slots

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
        constants = ConstantsBlueprint()

        if "crops" in data:
            loaded_crops = [CropBlueprint.from_dict(crop_data) for crop_data in data["crops"]]

        if "recipes" in data:
            loaded_recipes = [RecipeBlueprint.from_dict(recipe_data) for recipe_data in data["recipes"]]

        if "machines" in data:
            loaded_machines = [MachineBlueprint.from_dict(machine_data) for machine_data in data["machines"]]

        if "constants" in data:
            constants = ConstantsBlueprint.from_dict(data["constants"])

        game_blueprint = GameBlueprint(
            constants,
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

        # 1. Ensure that all game element IDs are unique
        def ensure_unique_ids(elements: list[GameElementBlueprint]):
            unique_ids = set([element.id for element in elements])
            if len(unique_ids) != len(elements):
                raise ValueError("duplicate ids")

        all_elements: list[GameElementBlueprint] = [
            *game_blueprint.crops.values(),
            *game_blueprint.recipes.values(),
            *game_blueprint.machines.values()
        ]

        ensure_unique_ids(all_elements)

        # 2. Ensure that each item reference exists

        all_ids: list[str] = [element.id for element in all_elements]

        for recipe in game_blueprint.recipes.values():
            for recipe_reference in recipe.recipe:
                if recipe_reference.id not in all_ids:
                    raise ValueError(f"recipe '{recipe.id}' uses an unknown reference '{recipe_reference.id}'")

        for machine in game_blueprint.machines.values():
            for recipe_id in machine.recipes:
                if recipe_id.id not in all_ids:
                    raise ValueError(f"machine '{machine.id}' uses an unknown reference '{recipe_id.id}'")
