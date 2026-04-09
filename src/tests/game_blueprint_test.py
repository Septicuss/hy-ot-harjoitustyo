import json
import unittest

from blueprint.game_blueprint import GameBlueprint

default_blueprint_path = "src/blueprint/blueprint.json"

class TestGameBlueprint(unittest.TestCase):

    def test_default_game_blueprint_valid(self):
        try:
            GameBlueprint.load_from_file(default_blueprint_path)
        except ValueError as error:
            self.fail("default game blueprint failed validation: " +  str(error))

    def test_missing_reference_raises_error(self):
        # Recipe refers to non-existing "berry"
        data = {
            "sprites": {"test": [0,0]},
            "recipes": [{"id": "test", "name": "test", "time": 10, "recipe": [{"id": "berry"}]}],
        }
        self.assertRaisesRegex(ValueError, "berry", GameBlueprint.load_from_json, json.dumps(data))

        # Machines recipe ingredient has a non-existing "berry"
        data = {
            "sprites": {"test": [0,0], "test_busy": [0,0]},
            "machines": [{"id": "test", "name": "test", "recipes": ["berry"]}],
        }
        self.assertRaisesRegex(ValueError, "berry", GameBlueprint.load_from_json, json.dumps(data))

    def test_duplicate_id_raises_error(self):
        # A crop and a machine have the same id
        data = {
            "sprites": {"wheat": [0,0], "wheat_stage_1": [0,0], "wheat_stage_2": [0,0], "wheat_stage_3": [0,0], "wheat_busy": [0,0]},
            "crops": [
                {"id": "wheat", "name": "wheat", "time": 5},
                {"id": "wheat", "name": "wheat", "time": 5}
            ],
            "machines": [
                {"id": "wheat", "name": "wheat", "recipes": []},
            ]
        }
        self.assertRaisesRegex(ValueError, "duplicate ids", GameBlueprint.load_from_json, json.dumps(data))

    def test_missing_sprites_raises_error(self):
        # A crop with no sprites
        data = {
            "crops": [
                {"id": "wheat", "name": "wheat", "time": 5}
            ]
        }
        self.assertRaisesRegex(ValueError, "crop 'wheat' did not have sprite", GameBlueprint.load_from_json, json.dumps(data))

        # A crop with stage_1 sprite missing
        data = {
            "sprites": {
                "wheat": [0,0],
                "wheat_stage_2": [0,0],
                "wheat_stage_3": [0,0],
            },
            "crops": [
                {"id": "wheat", "name": "wheat", "time": 5}
            ]
        }
        self.assertRaisesRegex(ValueError, "crop 'wheat' did not have sprite 'wheat_stage_1'", GameBlueprint.load_from_json, json.dumps(data))

        # A machine without _busy sprite
        data = {
            "sprites": {
                "test": [0,0],
            },
            "machines": [
                {"id": "test", "name": "test", "recipes": []}
            ]
        }
        self.assertRaisesRegex(ValueError, "machine 'test' did not have sprite 'test_busy'", GameBlueprint.load_from_json, json.dumps(data))

    def test_required_machine_slots_fails_with_nonexistent_machine(self):
        # Calling without a defined machine fails
        data = {}
        blueprint = GameBlueprint.load_from_json(json.dumps(data))

        self.assertRaisesRegex(ValueError, "Tried to get the required slots of a non-existent machine 'test'", blueprint.get_required_machine_slots, "test")

    def test_require_machine_slots_returns_correct_value(self):
        # A machine that crafts a recipe with two distinct ingredients returns 2 slots required
        data = {
            # Two ingredients
            "crops": [
                {"id": "a", "name": "a", "time": 5},
                {"id": "b", "name": "b", "time": 5}
            ],
            # Recipe with above two ingredients
            "recipes": [
                {"id": "c", "name": "c", "time": 5, "recipe": [
                    {"id": "a"},
                    {"id": "b"}
                ]},
            ],
            # Machine 'd' which crafts recipe 'c'
            "machines": [
                {"id": "d", "name": "d", "recipes": ["c"]},
            ]
        }
        blueprint = GameBlueprint.load_from_json(json.dumps(data), True)
        required_slots = blueprint.get_required_machine_slots("d")

        self.assertIs(required_slots, 2)
