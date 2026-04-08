from blueprint.game_blueprint import GameBlueprint

class GameState:
    def __init__(self, blueprint: GameBlueprint):
        self.blueprint = blueprint
        self.inventory = Inventory()
        self.farm = Farm(self)

class Inventory:
    def __init__(self):
        self._items: dict[str, int] = dict()

    def get_all_items(self) -> dict[str, int]:
        return self._items

    def get_all_item_ids(self) -> list[str]:
        return list(self._items.keys())

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


class Farm:

    def __init__(self, game: GameState):
        self.coins = game.blueprint.constants.default_coins

