import json
import unittest

from data.game_data import GameData

default_data_path = "src/data/data.json"

class TestGameData(unittest.TestCase):

    def test_default_game_data_valid(self):
        try:
            GameData.load_from_file(default_data_path)
        except ValueError as error:
            self.fail("default game data failed validation: " +  str(error))

    def test_missing_reference_raises_error(self):
        # Recipe refers to non-existing "berry"
        data = {
            "recipes": [{"id": "test", "name": "test", "time": 10, "recipe": [{"id": "berry"}]}],
        }
        self.assertRaisesRegex(ValueError, "berry", GameData.load_from_json, json.dumps(data))

    def test_duplicate_id_raises_error(self):
        # Both crops have the same id
        data = {
            "crops": [
                {"id": "wheat", "name": "wheat", "time": 5},
                {"id": "wheat", "name": "wheat", "time": 5}
            ],
        }
        self.assertRaisesRegex(ValueError, "duplicate ids", GameData.load_from_json, json.dumps(data))