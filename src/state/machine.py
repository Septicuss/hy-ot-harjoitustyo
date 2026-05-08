from typing import TYPE_CHECKING
from blueprint.blueprints import MachineBlueprint, RecipeBlueprint, ItemReference, MachineRenderType
from state.inventory import Inventory

if TYPE_CHECKING:
    from state.game_state import GameState

class Machine:
    """Class for handling the state of a machine."""

    def __init__(self, state: "GameState", blueprint: MachineBlueprint, tile: int, on_finish=None):
        self.state = state
        self.blueprint = blueprint
        self.tile = tile
        self.on_finish = on_finish

        self.slots = state.blueprint.get_required_machine_slots(blueprint.id)
        self.inventory: Inventory = Inventory(self.slots)

        self.collectable: bool = False
        self.busy: bool = False
        self.time_remaining: float = 0
        self.result: RecipeBlueprint | None = None

    def get_unlock_price(self) -> int | None:
        """Returns the price to unlock or none if not locked"""
        if not self.is_locked():
            return None

        return self.state.blueprint.constants.locked_tiles_prices[self.tile]

    def is_locked(self):
        """Returns true if this machine is locked"""
        return self.tile in self.state.locked_tiles

    def unlock(self) -> bool:
        """Attempt to unlock the machine by paying for it

        Returns true if successful, false otherwise
        """
        price = self.get_unlock_price()

        if self.state.player.coins < price:
            return False

        self.state.player.coins -= price
        self.state.unlock_tile(self.tile)
        return True

    def get_recipes(self) -> list[RecipeBlueprint]:
        """Get a list of recipes available for this machine."""
        return [
            self.state.blueprint.recipes.get(recipe_id)
            for recipe_id, _ in self.blueprint.recipes
        ]

    def get_recipe_map(self) -> dict[str, list[tuple[str, bool]]]:
        """Get a map of current recipe status of this machine

        Returns a dictionary, mapping recipe IDs to
        a list of its ingredient tuples in form:
        [ingredient ID, boolean (true = fulfilled)]
        """
        result = {}

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

            result[recipe.id] = recipe_result

        return result

    def get_items(self) -> list[ItemReference]:
        """Get a list of all items in the machines inventory."""
        return self.inventory.to_references()

    def remove_last_item(self) -> ItemReference | None:
        """Attempt to refund the last item added to the inventory.

        Returns none if nothing was removed or
        an item reference if successful.
        """

        if self.busy or self.is_locked():
            return None

        item_ids = self.inventory.get_all_item_ids()

        if len(item_ids) >= 1:
            first = item_ids[0]
            removed = self.inventory.remove_item(first)
            self.state.player.inventory.add_item(removed.id, removed.amount)
            return removed

        return None

    def add_item(self, item_id: str) -> tuple[bool, str | None]:
        """Attempt to add the given item to the machine.

        Returns the result with an optional error message.
        """
        if self.is_locked():
            return False, f'This {self.blueprint.name} is locked'

        if self.busy:
            return False, f'{self.blueprint.name} is already busy'

        if self.inventory.is_full():
            return False, f'{self.blueprint.name} is full'

        ids = {ingredient.id for recipe in self.get_recipes() for ingredient in recipe.recipe}
        item = self.state.blueprint.recipes.get(item_id)

        if not item_id in ids:
            item_name = item.name
            return False, f'{item_name} is not used in {self.blueprint.name}'

        is_farm = self.blueprint.render == MachineRenderType.CROP

        # Prevent player from using their last crop
        if not is_farm and self.state.is_last_crop(item.id):
            return False, 'Cannot use last crop'

        # Transfer item from players to machines inventory
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
            self._set_busy(first)

        return True, None

    def _set_busy(self, recipe: RecipeBlueprint):

        # Consume items
        for ingredient_id, ingredient_amount in recipe.recipe:
            self.inventory.remove_item(ingredient_id, ingredient_amount)

        # Refund leftovers to player
        for item_id, item_amount in self.inventory.to_references():
            self.state.player.inventory.add_item(item_id, item_amount)

        self.inventory.clear()

        self.result = recipe
        self.busy = True
        self.time_remaining = recipe.time

    def update(self, delta_time: float):
        # Not working on anything
        if not self.busy:
            return

        # Waiting for player to collect
        if self.collectable:
            return

        self.time_remaining -= delta_time

        if self.time_remaining <= 0:
            self._finish()

    def collect(self):
        """A method to trigger collecting the machines result item."""

        self.state.player.inventory.add_item(self.result.id, self.result.amount)

        if self.on_finish:
            self.on_finish()

        self.result = None
        self.busy = False
        self.collectable = False
        self.time_remaining = 0

    def _finish(self):
        self.collectable = True
        self.time_remaining = 0
