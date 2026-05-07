import json
import os
from json import JSONDecodeError

from blueprint.blueprints import ItemReference


class GameSave:
    """Represents the saved state of a game."""

    def __init__(self,
                 *,
                 is_first_run: bool = True,
                 inventory: list[ItemReference] = None,
                 coins: int = 0,
                 locked_tiles: list[int] = None):
        self.is_first_run = is_first_run
        self.inventory: list[ItemReference] = inventory if inventory else []
        self.coins: int = coins
        self.locked_tiles: list[int] = locked_tiles if locked_tiles else []

    def to_dict(self) -> dict:
        return {
            "inventory": [
                {"id": reference.id, "amount": reference.amount}
                for reference in self.inventory
            ],
            "coins": self.coins,
            "locked_tiles": self.locked_tiles,
        }

    @classmethod
    def from_dict(cls, data):

        inventory: list[ItemReference] = []

        if "inventory" in data:
            for reference in data["inventory"]:
                inventory.append(ItemReference.from_dict(reference))

        return cls(
            is_first_run=False,
            inventory=inventory,
            coins=data.get("coins", 0),
            locked_tiles=data.get("locked_tiles", [])
        )

class GameSaves:
    """Represents a container and reader/writer of saved game slots."""

    save_slot_amount = 2 # 1-indexed

    def __init__(self, path: str, slots: dict[int, GameSave] = None):
        self.slots: dict[int, GameSave] = slots if slots is not None else {}
        self.path: str = path

    def load_saves(self):
        for index in range(1, self.save_slot_amount + 1):
            save = self.load_save(index)
            self.slots[index] = save

    def load_save(self, slot: int) -> GameSave:
        file_name = f'slot_{slot}.json'
        file_path = os.path.join(self.path, file_name)

        if not os.path.exists(file_path):
            return GameSave()

        data: dict | None = None

        try:
            with open(file_path, 'r', encoding='UTF-8') as file:
                data = json.load(file)
        except JSONDecodeError:
            pass

        if not data:
            return GameSave()

        return GameSave.from_dict(data)

    def get_save(self, slot: int) -> GameSave | None:
        return self.slots.get(slot)

    def save(self, save: GameSave, slot: int):
        self.slots[slot] = save
        self._save_slot_to_disk(slot)

    def _save_slot_to_disk(self, slot: int):
        file_name = f'slot_{slot}.json'
        file_path = os.path.join(self.path, file_name)

        os.makedirs(self.path, exist_ok=True)

        data = self.get_save(slot).to_dict()

        with open(file_path, 'w', encoding='UTF-8') as file:
            json.dump(data, file)

    @classmethod
    def load_from_json(cls, data: str) -> GameSave | None:
        data = json.loads(data)

        if not data:
            return None

        return GameSave.from_dict(data)