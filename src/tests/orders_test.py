import json
import unittest

from blueprint.blueprints import ItemReference
from blueprint.game_blueprint import GameBlueprint
from save.save import GameSaves
from state.game_state import GameState
from state.orders import Orders


class TestOrders(unittest.TestCase):

    def setUp(self):
        self.price_ranges = {
            "A": (1, 10),
            "B": (11, 20),
            "C": (21, 30),
        }

        data = {
            "recipes": [
                {"id": "A", "name": "A", "price": {"low": 1, "high": 10}, "type": "crop", "time": 1},
                {"id": "B", "name": "B", "price": {"low": 11, "high": 20}, "type": "crop", "time": 1},
                {"id": "C", "name": "C", "price": {"low": 21, "high": 30}, "type": "crop", "time": 1},
            ],
            "machines": [
                {"id": "D", "name": "D", "recipes": ["A", "B", "C"]},
            ],
            "constants": {
                "tiles": {
                    "0": "D"
                }
            }
        }
        save = {
            "inventory": [
                {"id": "A", "amount": 2},
                {"id": "B"},
                {"id": "C"},
            ],
            "coins": 10
        }

        blueprint = GameBlueprint.load_from_json(json.dumps(data), ignore_sprites=True)
        save = GameSaves.load_from_json(json.dumps(save))
        saves = GameSaves("", {1: save})

        self.state = GameState(blueprint, saves)
        self.orders = Orders(self.state)
        self.state.orders = self.orders

    def test_order_initially_empty(self):
        self.assertIsNone(self.orders.order)
        self.assertEqual(self.orders.reward, 0)
        self.assertEqual(self.orders.update_timer, 0)

    def test_next_order_works_correctly(self):

        found = []

        while {"A", "B", "C"} != set(found):
            order, reward = self.orders._set_next_order()

            if self.orders.order.amount > 1:
                reward = reward / self.orders.order.amount

            # Ensure reward for this item ID is in correct range
            low, high = self.price_ranges[order.id]
            self.assertTrue(low <= reward <= high, f"Reward {reward} for item id {order.id} was out of range")

            if not order.id in found:
                found.append(order.id)

        # Ensure all items have been met
        self.assertEqual(set(found), {"A", "B", "C"})

    def test_next_order_is_set_automatically(self):

        # Ensure order not set at first
        self.assertIsNone(self.orders.order)
        self.assertEqual(self.orders.reward, 0)

        # Move time forward, but not enough to trigger update
        self.state.update(delta_time=0.5)

        # Ensure order still not set
        self.assertIsNone(self.orders.order)
        self.assertEqual(self.orders.reward, 0)

        # Move time forward to trigger update
        self.state.update(delta_time=0.5)

        # Ensure order has now been set
        self.assertIsNotNone(self.orders.order)
        self.assertNotEqual(self.orders.reward, 0)

    def test_submitting_final_item_updates_state_correctly(self):
        # Set the order
        self.orders.order = ItemReference("A")
        self.orders.reward = 5

        # Ensure player has two "A"'s before submitting
        self.assertEqual(self.state.player.inventory.get_item_amount("A"), 2)

        # Submit the item required in the order
        result = self.orders.submit_one("A")

        # Ensure result correctly signifies that the order is complete
        self.assertEqual(result, (True, None))

        # Ensure player got coins
        self.assertEqual(self.state.player.coins, 15)

        # Ensure player has one less "A"
        self.assertEqual(self.state.player.inventory.get_item_amount("A"), 1)

        # Ensure state is reset
        self.assertIsNone(self.orders.order)
        self.assertEqual(self.orders.reward, 0)

    def test_submitting_part_item_updates_state_correctly(self):
        self.orders.order = ItemReference("A", 2)
        self.orders.reward = 5

        # Submit only one "A" when two are needed
        self.orders.submit_one("A")

        # Ensure that required count went down
        self.assertEqual(self.orders.order.amount, 1)

    def test_invalid_submissions_return_correct_error(self):

        result = self.orders.submit_one("A")
        self.assertEqual(result, (False, None)) # No order set, nothing should happen

        # Set order
        self.orders.order = ItemReference("A", 2)
        self.orders.reward = 5

        result = self.orders.submit_one("B")
        self.assertEqual(result, (False, "Wrong item")) # Unable to submit wrong items

        result = self.orders.submit_one("A")
        self.assertEqual(result, (False, None))  # Partial submission successful (1/2)

        result = self.orders.submit_one("A")
        self.assertEqual(result, (False, 'Cannot use last crop'))  # Trying to submit players last crop item
