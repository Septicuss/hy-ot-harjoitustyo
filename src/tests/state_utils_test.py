import unittest

from blueprint.blueprints import ItemReference
import state.utils as utils


class TestGameStateUtils(unittest.TestCase):
    def setUp(self):
        self.first = [
            ItemReference("wheat", 2),
            ItemReference("berry", 1),
        ]
        self.second = [
            ItemReference("wheat", 1),
            ItemReference("soy", 3),
        ]

    def test_get_item_counts(self):
        self.assertDictEqual(utils.get_item_counts(self.first), {"wheat": 2, "berry": 1})
        self.assertDictEqual(utils.get_item_counts(self.second), {"wheat": 1, "soy": 3})
        self.assertDictEqual(utils.get_item_counts([]), {})

    def test_item_counts_match(self):
        self.assertTrue(utils.item_counts_match(self.first, self.first))
        self.assertFalse(utils.item_counts_match(self.first, self.second))

    pass