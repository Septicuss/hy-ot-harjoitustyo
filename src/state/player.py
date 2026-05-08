from typing import Literal, TYPE_CHECKING

from state.inventory import Inventory

if TYPE_CHECKING:
    from state.game_state import GameState

class Player:
    """Class representing the players state."""

    def __init__(self, game: "GameState"):
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
