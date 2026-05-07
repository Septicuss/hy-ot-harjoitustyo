from typing import Literal

from blueprint.blueprints import (MachineBlueprint,
                                  ItemReference,
                                  RecipeBlueprint,
                                  RecipeType,
                                  MachineRenderType)
from blueprint.game_blueprint import GameBlueprint
from save.save import GameSave, GameSaves
from state.inventory import Inventory
from state.orders import Orders


class GameState:
    """Class for holding and controlling the entire game state"""

    def __init__(self, blueprint: GameBlueprint, saves: GameSaves):
        self.save_slot: int = 1
        self.saves = saves

        save = self.saves.get_save(self.save_slot)

        if save is None:
            raise RuntimeError('Unable to load save')

        self.blueprint = blueprint

        # State objects
        self.player = Player(self)
        self.orders = Orders(self)

        # State
        self.timer: float = 0
        self.autosave_timer: float = 0
        self.tiles: dict[int, Machine] = {}
        self.locked_tiles: list[int] = []

        self._initialize_tiles()
        self._load_defaults(save)
        self._load_save(save)

    def _initialize_tiles(self):
        for tile, machine_id in self.blueprint.constants.default_tiles.items():
            machine_blueprint = self.blueprint.machines.get(machine_id)
            machine = Machine(self, machine_blueprint, tile)
            self.tiles[tile] = machine

    def _load_save(self, save: GameSave):
        if not save.is_first_run:
            self.locked_tiles = save.locked_tiles
            self.player.coins = save.coins

            for item_id, item_amount in save.inventory:
                self.player.inventory.add_item(item_id, item_amount)

    def _load_defaults(self, save: GameSave):
        # Initialize defaults on first game run
        if save.is_first_run:
            # Set default locked tiles
            self.locked_tiles = [
                int(tile)
                for tile in self.blueprint.constants.locked_tiles_prices.keys()
            ]

            # Add default items
            for item_ref in self.blueprint.constants.default_items:
                self.player.inventory.add_item(item_ref.id, item_ref.amount)

            # Save now to keep defaults
            self.save_state()

    def save_state(self):
        """Write the current state to the current save slot."""

        save = self._current_state_to_save()
        self.saves.save(save, self.save_slot)

    def _current_state_to_save(self) -> GameSave:
        """Returns the current state as a GameSave."""

        return GameSave(
            is_first_run=False,
            inventory=self.player.inventory.to_references(),
            coins=self.player.coins,
            locked_tiles=self.locked_tiles
        )

    def get_available_items(self) -> list[str]:
        """Returns a list of IDs that the player can access at this moment in the game."""

        items = []

        for machine in self.tiles.values():
            if machine.is_locked():
                continue

            items += [recipe.id for recipe in machine.blueprint.recipes]

        return list(set(items))

    def unlock_tile(self, tile: int):
        """Unlocks the given tile."""

        self.locked_tiles.remove(tile)

    def is_last_crop(self, item_id: str) -> bool:
        """Returns true if the given item is the players last crop."""

        item = self.blueprint.recipes.get(item_id)
        return item.type == RecipeType.CROP and self.player.inventory.get_item_amount(item.id) == 1

    def update(self, delta_time: float):
        """Primary update loop of the game state."""

        self.timer += delta_time
        self.autosave_timer += delta_time

        if self.autosave_timer > 10:
            self.autosave_timer = 0
            self.save_state()

        # Set selected item if not set
        selected_item = self.player.get_selected_item()
        selected_item_amount = self.player.inventory.get_item_amount(selected_item)

        has_any_items = len(self.player.inventory.get_all_item_ids()) > 0

        if selected_item is None and has_any_items or selected_item_amount <= 0:
            self.player.cycle_selected_item()

        # Update orders
        self.orders.update(delta_time=delta_time)

        # Update machines
        for machine in self.tiles.values():
            machine.update(delta_time=delta_time)


class Machine:
    def __init__(self, state: GameState, blueprint: MachineBlueprint, tile: int, on_finish=None):
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
