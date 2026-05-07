import unittest

from blueprint.game_blueprint import GameBlueprint
from state.game_state import GameState
from tests.constants import default_blueprint_path


class GameStateTest(unittest.TestCase):

    def setUp(self):
        self.blueprint = GameBlueprint.load_from_file(default_blueprint_path)
        self.state = GameState(self.blueprint)
        self.inventory = self.state.player.inventory

    pass