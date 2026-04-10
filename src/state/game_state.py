from blueprint.blueprints import MachineBlueprint
from blueprint.game_blueprint import GameBlueprint

class GameState:
    def __init__(self, blueprint: GameBlueprint):
        self.blueprint = blueprint
        self.player = Player(self)
        self.timer: float = 0
        self.machines: list[Machine] = [Machine(self, machine_blueprint) for machine_blueprint in blueprint.machines.values()]

    def update(self, delta_time: float):
        self.timer += delta_time

        # Set selected item if not set
        if self.player.get_selected_item() is None and len(self.player.inventory.get_all_item_ids()) > 0:
            self.player.cycle_selected_item()


class Inventory:
    def __init__(self, slot_limit: int = -1):
        self._items: dict[str, int] = dict()
        self._slot_limit = slot_limit

    def is_full(self):
        if self._slot_limit == -1:
            return False
        return len(self.get_all_item_ids()) > self._slot_limit

    def get_all_items(self) -> dict[str, int]:
        return self._items

    def get_all_item_ids(self) -> list[str]:
        return list(set(self._items.keys()))

    def get_item_amount(self, item_id: str) -> int:
        return self._items.get(item_id, 0)

    def add_item(self, item_id: str, amount: int = 1):
        previous = self._items.get(item_id, 0)
        self._items[item_id] = previous + amount

    def remove_item(self, item_id: str, amount: int = 1):
        if item_id not in self._items:
            return

        self._items[item_id] -= amount

        if self._items[item_id] <= 0:
            del self._items[item_id]

class Machine:
    def __init__(self, game: GameState, blueprint: MachineBlueprint):
        self.blueprint = blueprint

        # Initialize inventory with slot limit required for this machine
        required_slots = game.blueprint.get_required_machine_slots(blueprint.id)
        self._inventory = Inventory(required_slots)

class Player:

    def __init__(self, game: GameState):
        self.coins = game.blueprint.constants.default_coins
        self.inventory = Inventory()
        self._selected_item = None

    def get_selected_item(self) -> str | None:
        return self._selected_item

    def set_selected_item(self, item_id: str):
        self._selected_item = item_id

    def cycle_selected_item(self):
        if self._selected_item is None:
            self.set_selected_item(self.inventory.get_all_item_ids()[0])
            return

        for item_id in self.inventory.get_all_item_ids():
            if item_id != self._selected_item:
                self.set_selected_item(item_id)
                break