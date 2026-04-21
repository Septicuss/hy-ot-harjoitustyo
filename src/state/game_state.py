from blueprint.blueprints import MachineBlueprint, ItemReference
from blueprint.game_blueprint import GameBlueprint
from state import utils

class GameState:
    def __init__(self, blueprint: GameBlueprint):
        self.blueprint = blueprint
        self.player = Player(self)
        self.timer: float = 0

        # TODO: Switch counter for either default machines & slots or loaded from savefile
        counter = 0
        self.machines: list[Machine] = []
        for machine_blueprint in blueprint.machines.values():
            machine = Machine(self, machine_blueprint, counter)
            self.machines.append(machine)
            counter += 1


    def update(self, delta_time: float):
        self.timer += delta_time

        # Set selected item if not set
        selected_item = self.player.get_selected_item()

        if selected_item is None and len(self.player.inventory.get_all_item_ids()) > 0:
            self.player.cycle_selected_item()

        # Update machines
        for machine in self.machines:
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
    def __init__(self, state: GameState, blueprint: MachineBlueprint, slot: int):
        self.state = state
        self.blueprint = blueprint
        self.slot = slot

        self.slots = state.blueprint.get_required_machine_slots(blueprint.id)
        self.inventory: Inventory = Inventory(self.slots)

        self.busy: bool = False
        self.time_remaining: float = 0
        self.result: str | None = None

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

        self.inventory.add_item(item_id)

        # Check if any recipe has been matched
        recipes = self.state.blueprint.get_matching_recipes(
            items=self.get_items(),
            machine_id=self.blueprint.id,
            strict=True
        )

        if len(recipes) == 1:
            first = recipes[0]
            self.result = first.id
            self.busy = True
            self.time_remaining = first.time


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

    def cycle_selected_item(self):
        if self._selected_item is None:
            self.set_selected_item(self.inventory.get_all_item_ids()[0])
            return

        for item_id in self.inventory.get_all_item_ids():
            if item_id != self._selected_item:
                self.set_selected_item(item_id)
                break
