from blueprint.blueprints import (RecipeType)
from blueprint.game_blueprint import GameBlueprint
from save.save import GameSave, GameSaves
from state.machine import Machine
from state.orders import Orders
from state.player import Player


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
