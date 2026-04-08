import json
import unittest

from blueprint.game_blueprint import GameBlueprint

default_data_path = "src/blueprint/blueprint.json"

class TestGameData(unittest.TestCase):

    def test_default_game_data_valid(self):
        try:
            GameBlueprint.load_from_file(default_data_path)
        except ValueError as error:
            self.fail("default game blueprint failed validation: " +  str(error))

    def test_missing_reference_raises_error(self):
        # Recipe refers to non-existing "berry"
        data = {
            "recipes": [{"id": "test", "name": "test", "time": 10, "recipe": [{"id": "berry"}]}],
        }
        self.assertRaisesRegex(ValueError, "berry", GameBlueprint.load_from_json, json.dumps(data))

        # Machines recipe ingredient has a non-existing "berry"
        data = {
            "machines": [{"id": "test", "name": "test", "recipes": ["berry"]}],
        }
        self.assertRaisesRegex(ValueError, "berry", GameBlueprint.load_from_json, json.dumps(data))

    def test_duplicate_id_raises_error(self):
        # Both crops have the same id
        data = {
            "crops": [
                {"id": "wheat", "name": "wheat", "time": 5},
                {"id": "wheat", "name": "wheat", "time": 5}
            ],
        }
        self.assertRaisesRegex(ValueError, "duplicate ids", GameBlueprint.load_from_json, json.dumps(data))