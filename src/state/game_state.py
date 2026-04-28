from dataclasses import dataclass
from typing import Literal

from blueprint.blueprints import MachineBlueprint, ItemReference, RecipeBlueprint
from blueprint.game_blueprint import GameBlueprint
from save.save import GameSave
from state import utils

class GameState:
    """Class for holding and controlling the entire game state"""

    def __init__(self, blueprint: GameBlueprint, save: GameSave):
        self.blueprint = blueprint
        self.player = Player(self)
        self.timer: float = 0
        self.tiles: dict[int, Machine] = {}

        # Initialize defaults on first game run
        if save.is_first_run:
            # Set default tiles
            for tile, machine_id in self.blueprint.constants.default_tiles.items():
                machine_blueprint = self.blueprint.machines.get(machine_id)
                machine = Machine(self, machine_blueprint, tile)

                self.set_tile(tile, machine)

            # Add default items
            for item_ref in self.blueprint.constants.default_items:
                self.player.inventory.add_item(item_ref.id, item_ref.amount)

    def get_tile(self, tile: int) -> "Machine | None":
        self.tiles.get(tile)

    def set_tile(self, tile: int, machine: "Machine"):
        self.tiles[tile] = machine

    def update(self, delta_time: float):
        self.timer += delta_time

        # Set selected item if not set
        selected_item = self.player.get_selected_item()
        selected_item_amount = self.player.inventory.get_item_amount(selected_item)

        if selected_item is None and len(self.player.inventory.get_all_item_ids()) > 0 or selected_item_amount <= 0:
            self.player.cycle_selected_item()

        # Update machines
        for machine in self.tiles.values():
            machine.update(delta_time=delta_time)

class Inventory:
    """Represents an inventory which can hold items up to its item limit."""

    def __init__(self, item_limit: int = -1):
        self._items: dict[str, int] = {}
        self._item_limit = item_limit

    def is_full(self):
        """Returns whether the inventory is full and cannot accept any more items."""
        if self._item_limit == -1:
            return False
        return utils.item_count_sum(self.to_references()) >= self._item_limit

    def get_all_items(self) -> dict[str, int]:
        """Get a dict of all items [id, amount]"""
        return self._items

    def get_all_item_ids(self) -> list[str]:
        """Get all unique item ids."""
        return list(set(self._items.keys()))

    def get_item_amount(self, item_id: str) -> int:
        """Get the amount of the given item in the inventory."""
        return self._items.get(item_id, 0)

    def add_item(self, item_id: str, amount: int = 1):
        """Force adds an item with the given amount to the inventory."""
        previous = self._items.get(item_id, 0)
        self._items[item_id] = previous + amount

    def clear(self):
        """Fully clear the inventory."""
        self._items.clear()

    def remove_item(self, item_id: str, amount: int = 1) -> ItemReference | None:
        """Remove the given amount of the given item from the inventory.

        Returns:
            ItemReference | None: If found, returns a reference to
             the removed item and removed amount.
        """
        if item_id not in self._items:
            return None

        start_amount = self._items[item_id]

        self._items[item_id] -= amount

        if self._items[item_id] <= 0:
            del self._items[item_id]
            return ItemReference(item_id, start_amount)

        return ItemReference(item_id, amount)

    def to_references(self) -> list[ItemReference]:
        """Get all items as item references."""
        references = []

        for item in self.get_all_items().items():
            references.append(ItemReference(item[0], item[1]))

        return references

class Machine:
    def __init__(self, state: GameState, blueprint: MachineBlueprint, tile: int):
        self.state = state
        self.blueprint = blueprint
        self.tile = tile

        self.slots = state.blueprint.get_required_machine_slots(blueprint.id)
        self.inventory: Inventory = Inventory(self.slots)

        self.busy: bool = False
        self.time_remaining: float = 0
        self.result: str | None = None

    def get_recipes(self) -> list[RecipeBlueprint]:
        return [
            self.state.blueprint.recipes.get(recipe_id)
            for recipe_id, _ in self.blueprint.recipes
        ]

    def get_recipe_array(self) -> list[list[tuple[str, bool]]]:
        result = []

        recipes = self.get_recipes()

        for recipe in recipes:
            recipe_result: list[tuple[str, bool]] = []
            ingredient_ids = recipe.get_recipe_as_id_array() # [wheat, wheat]
            ingredient_amounts = {}

            for ingredient_id in ingredient_ids:
                if ingredient_id not in ingredient_amounts:
                    ingredient_amounts[ingredient_id] = 0
                ingredient_amounts[ingredient_id] += 1

                owned_amount = self.inventory.get_item_amount(ingredient_id)
                present = owned_amount >= ingredient_amounts[ingredient_id]

                recipe_result.append((ingredient_id, present))

            result.append(recipe_result)

        return result

    def get_items(self) -> list[ItemReference]:
        return self.inventory.to_references()

    def remove_last_item(self) -> ItemReference | None:
        if self.busy:
            return None

        item_ids = self.inventory.get_all_item_ids()

        if len(item_ids) >= 1:
            first = item_ids[0]
            removed = self.inventory.remove_item(first)
            return removed

        return None

    def add_item(self, item_id: str):
        if self.busy:
            return

        if self.inventory.is_full():
            return

        ids = {ingredient.id for recipe in self.get_recipes() for ingredient in recipe.recipe}

        if not item_id in ids:
            return

        # TODO: Check if adding an item actually contributes to the recipe
        # [wheat, wheat, berry]
        # [wheat, wheat, soy]

        self.state.player.inventory.remove_item(item_id, 1)
        self.inventory.add_item(item_id)

        # Check if any recipe has been matched
        recipes = self.state.blueprint.get_matching_recipes(
            items=self.get_items(),
            machine_id=self.blueprint.id,
            strict=True
        )

        if len(recipes) == 1:
            first = recipes[0]
            self.set_busy(first)

    def set_busy(self, recipe: RecipeBlueprint):

        # Consume items
        for ingredient_id, ingredient_amount in recipe.recipe:
            self.inventory.remove_item(ingredient_id, ingredient_amount)

        # Refund leftovers to player
        for item_id, item_amount in self.inventory.to_references():
            self.state.player.inventory.add_item(item_id, item_amount)

        self.inventory.clear()

        self.result = recipe.id
        self.busy = True
        self.time_remaining = recipe.time

    def update(self, delta_time: float):
        if not self.busy:
            return

        self.time_remaining -= delta_time

        if self.time_remaining <= 0:
            self.finish()

    def finish(self):
        self.state.player.inventory.add_item(self.result)

        self.result = None
        self.busy = False
        self.time_remaining = 0


class Player:

    def __init__(self, game: GameState):
        self.coins = game.blueprint.constants.default_coins
        self.inventory = Inventory()
        self._selected_item = None

    def get_selected_item(self) -> str | None:
        return self._selected_item

    def set_selected_item(self, item_id: str):
        self._selected_item = item_id

    def _item_keys(self):
        return list(self.inventory.get_all_items().keys())

    def cycle_selected_item(self, direction: Literal['left', 'right'] = 'left'):
        direction_index = -1 if direction == 'left' else 1
        keys = self._item_keys()

        if len(keys) == 0:
            self._selected_item = None
            return None

        if not keys:
            self._selected_item = None

        if self._selected_item not in keys:
            self._selected_item = keys[0]
            return self._selected_item

        i = keys.index(self._selected_item)
        self._selected_item = keys[(i + direction_index) % len(keys)]
        return self._selected_item
