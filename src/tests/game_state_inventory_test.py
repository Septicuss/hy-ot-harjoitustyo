import unittest

from blueprint.blueprints import ItemReference
from state.game_state import Inventory


class GameStateInventoryTest(unittest.TestCase):

    def setUp(self):
        self.inventory = Inventory()
        self.inventory.add_item("wheat")
        self.inventory.add_item("berry", 5)

    def test_default_inventory_infinite_slots(self):
        self.assertEqual(self.inventory._item_limit, -1)

    def test_inventory_adding_items_works(self):
        self.assertDictEqual(self.inventory.get_all_items(), {"wheat": 1, "berry": 5})

    def test_inventory_removing_items_works(self):
        self.inventory.remove_item("wheat")

        self.assertDictEqual(self.inventory.get_all_items(), {"berry": 5})

        self.inventory.remove_item("berry", 2)

        self.assertDictEqual(self.inventory.get_all_items(), {"berry": 3})

    def test_inventory_to_reference_correct(self):
        expected: list[ItemReference] = [ItemReference("wheat", 1), ItemReference("berry", 5)]
        references: list[ItemReference] = self.inventory.to_references()

        self.assertListEqual(expected, references)

    def test_infinite_inventory_is_not_full_initially(self):
        self.assertFalse(self.inventory.is_full(), "infinite inventory should not be full")

    def test_is_full_behavior_correct(self):
        inventory = Inventory(2)
        self.assertFalse(inventory.is_full(), "on first creation, inventory should not be full")

        inventory.add_item("wheat", 2)
        self.assertTrue(inventory.is_full(), "inventory should be full")

        inventory.add_item("wheat", 1)
        self.assertTrue(inventory.is_full(), "inventory should be full")

        inventory.remove_item("wheat", 3)
        inventory.add_item("berry", 1)
        self.assertFalse(inventory.is_full(), "inventory should not be full")

    def test_unique_item_ids_correct(self):
        self.assertCountEqual(self.inventory.get_all_item_ids(), ("wheat", "berry"))

    def test_getting_item_amount_correct(self):
        self.assertEqual(self.inventory.get_item_amount("wheat"), 1)
        self.assertEqual(self.inventory.get_item_amount("berry"), 5)

    def test_clearing_inventory_works(self):
        self.assertDictEqual(self.inventory.get_all_items(), {"wheat": 1, "berry": 5})
        self.inventory.clear()
        self.assertDictEqual(self.inventory.get_all_items(), {})

    def test_removing_nonexistent_item_fails(self):
        result = self.inventory.remove_item("soy")
        self.assertIsNone(result, "result of removing a non-existent item should be None")