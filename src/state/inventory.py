from blueprint.blueprints import ItemReference
from state import utils


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

    def size(self) -> int:
        """Returns the amount of unique items in the inventory"""
        return len(self._items)

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
