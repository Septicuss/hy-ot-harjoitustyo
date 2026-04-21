import json
from dataclasses import fields, dataclass
from pathlib import Path
from typing import Self
from state import utils

from blueprint.blueprints import (
    RecipeBlueprint,
    MachineBlueprint,
    GameElementBlueprint,
    ConstantsBlueprint,
    SpritesBlueprint,
    ItemReference
)


def _validate_sprites(item_type: str, ids: list[str], get_sprites_func):
    for item_id in ids:
        sprites = get_sprites_func(item_id)

        for field in fields(sprites):
            if getattr(sprites, field.name) is None:
                sprite_name = f'{item_id}{f'_{field.name}' if field.name != 'main' else ''}'
                raise ValueError(f"{item_type} '{item_id}' did not have sprite '{sprite_name}'")

def _validate_references(item_type: str, items, ids: list[str], get_refs_func):
    for item in items:
        for ref_id in get_refs_func(item):
            if ref_id not in ids:
                msg = f"{item_type} '{item.id}' uses an unknown reference '{ref_id}'"
                raise ValueError(msg)

@dataclass
class GameBlueprintData:
    constants: ConstantsBlueprint
    sprites: SpritesBlueprint
    recipes: list[RecipeBlueprint]
    machines: list[MachineBlueprint]

class GameBlueprint:
    """Represents a blueprint, containing smaller blueprints of in-game elements.
    As arguments takes a list of each type of game element blueprint.
    """

    def __init__(self, data: GameBlueprintData):
        self.constants = data.constants
        self.sprites = data.sprites
        self.recipes: dict[str, RecipeBlueprint] = {
            recipe.id: recipe
            for recipe in data.recipes
        }
        self.machines: dict[str, MachineBlueprint] = {
            machine.id: machine
            for machine in data.machines
        }

    def get_required_machine_slots(self, machine_id: str) -> int:
        machine: MachineBlueprint = self.machines.get(machine_id)

        if not machine:
            raise ValueError(f"Unknown machine '{machine_id}'")

        required_slots: int = 0

        for recipe_reference in machine.recipes:
            recipe_blueprint = self.recipes.get(recipe_reference.id)
            required_slots = max(required_slots, len(recipe_blueprint.recipe))

        return required_slots

    def get_game_element(self, item_id) -> GameElementBlueprint | None:
        if item_id in self.recipes:
            return self.recipes.get(item_id)
        if item_id in self.machines:
            return self.machines.get(item_id)

        return None

    def get_matching_recipes(self,
                             items: list[ItemReference],
                             machine_id: str = None,
                             strict: bool = False) -> list[RecipeBlueprint]:
        """Returns a list of recipes matching the given list of items

        Args:
            items (list[ItemReference]): the ingredients to check
            machine_id (str): optional id to scope recipes to a machine
            strict (bool): optional, false by default, if true will
                only return recipes for which all requirements are satisfied

        """

        recipe_filter: list[str] | None = None

        if machine_id is not None:
            machine = self.machines.get(machine_id)
            recipe_filter = [item_reference.id for item_reference in machine.recipes]

        matched: list[RecipeBlueprint] = []
        blueprints: list[RecipeBlueprint] = [
            recipe
            for recipe in list(self.recipes.values())
            if recipe_filter is None or recipe.id in recipe_filter
        ]

        for blueprint in blueprints:
            if strict:
                if utils.item_counts_match(blueprint.recipe, items):
                    matched.append(blueprint)
            else:
                if utils.item_counts_match(items, blueprint.recipe):
                    matched.append(blueprint)

        return matched

    @classmethod
    def load_from_file(cls, file_path: str, ignore_sprites: bool = False) -> Self | None:
        """Loads game JSON blueprint into a GameData class from a JSON file"""

        path = Path(file_path)
        with path.open(encoding='UTF-8') as file:
            return GameBlueprint.load_from_json(
                json_data=str(file.read()),
                ignore_sprites=ignore_sprites
            )

    @classmethod
    def load_from_json(cls, json_data: str, ignore_sprites: bool = False) -> Self | None:
        """Loads game blueprint into a GameBlueprint class from a JSON string

        This method will throw a ValueError if blueprint validation fails.
        """

        data = json.loads(json_data)

        loaded_recipes = []
        loaded_machines = []
        constants = ConstantsBlueprint()
        sprites = SpritesBlueprint({})

        if "recipes" in data:
            loaded_recipes = [
                RecipeBlueprint.from_dict(recipe_data)
                for recipe_data in data["recipes"]
            ]

        if "machines" in data:
            loaded_machines = [
                MachineBlueprint.from_dict(machine_data)
                for machine_data in data["machines"]
            ]

        if "constants" in data:
            constants = ConstantsBlueprint.from_dict(data["constants"])

        if "sprites" in data:
            sprites = SpritesBlueprint.from_dict(data["sprites"])

        game_blueprint_data = GameBlueprintData(
            constants,
            sprites,
            loaded_recipes,
            loaded_machines
        )

        game_blueprint = GameBlueprint(game_blueprint_data)

        # Validate loaded blueprint
        cls.__validate_or_throw(game_blueprint, ignore_sprites)

        return game_blueprint

    @classmethod
    def __validate_or_throw(cls, game_blueprint: Self, ignore_sprites: bool = False):
        """Method to validate a given blueprint or throw an error

        Internal method to validate the loaded game blueprint
        so that it can be safely used at runtime.
        """

        # 1. Ensure that all game element IDs are unique
        def ensure_unique_ids(elements: list[GameElementBlueprint]):
            unique_ids = {element.id for element in elements}
            if len(unique_ids) != len(elements):
                raise ValueError("duplicate ids")

        all_elements: list[GameElementBlueprint] = [
            *game_blueprint.recipes.values(),
            *game_blueprint.machines.values()
        ]

        ensure_unique_ids(all_elements)

        # 2. Ensure that each item reference exists

        all_ids: list[str] = [element.id for element in all_elements]

        # Recipes refer to ingredients by ID
        _validate_references(
            "recipe",
            list(game_blueprint.recipes.values()),
            all_ids,
            lambda r: (ref.id for ref in r.recipe)
        )

        # Machines refer to recipe IDs
        _validate_references(
            "machine",
            list(game_blueprint.machines.values()),
            all_ids,
            lambda m: (m.id for m in m.recipes)
        )

        # 3. Ensure that all elements have sprites
        if ignore_sprites:
            return

        # Validate machines
        _validate_sprites(
            "machine",
            list(game_blueprint.machines.keys()),
            game_blueprint.sprites.get_machine_sprites
        )


        # Validate recipes
        _validate_sprites(
            "recipe",
            list(game_blueprint.recipes.keys()),
            lambda recipe_id: ( # get recipe sprite accounting for the recipe type
                game_blueprint.sprites.get_recipe_sprites(
                    recipe_id,
                    game_blueprint.recipes.get(recipe_id).type
                )
            )
        )
