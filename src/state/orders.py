import random

from blueprint.blueprints import ItemReference


class Orders:

    def __init__(self, state: "GameState"):
        self.state = state

        self.update_timer: float = 0

        self.order: ItemReference | None = None
        self.reward: int = 0

    def _timer(self, delta_time: float, time: float) -> bool:
        self.update_timer += delta_time
        if self.update_timer < time:
            return True
        self.update_timer = 0
        return False

    def _set_next_order(self) -> tuple[ItemReference, int]:
        available_items = self.state.get_available_items()

        next_item_id = random.choice(available_items)
        next_item = self.state.blueprint.recipes.get(next_item_id)
        next_item_amount = 2 if random.randint(1, 100) > 80 else 1
        next_item_reward = random.randint(next_item.price[0], next_item.price[1]) * next_item_amount

        self.order = ItemReference(next_item_id, next_item_amount)
        self.reward = next_item_reward

        return self.order, self.reward

    def complete(self):
        self.state.player.coins += self.reward
        self.order = None
        self.reward = 0

    def submit_one(self, item_id: str) -> tuple[bool, str | None]:
        """Submit an item to the order

        Returns a tuple, containing whether submission resulted in order
        completion and an optional error string
        """

        if self.order is None:
            return False, None

        if self.order.id != item_id:
            return False, 'Wrong item'

        if self.state.is_last_crop(item_id):
            return False, 'Cannot use last crop'

        # Transfer item
        self.state.player.inventory.remove_item(item_id, 1)

        if self.order.amount > 1:
            self.order = ItemReference(self.order.id, self.order.amount - 1)
            return False, None # Not yet complete

        # Order completed
        self.complete()
        return True, None

    def update(self, delta_time: float):

        # Update once a second
        if self._timer(delta_time, 1):
            return

        # Update order if not set
        if self.order is None:
            self._set_next_order()
            return
