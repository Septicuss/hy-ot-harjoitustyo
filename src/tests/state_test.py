import json
import unittest

from blueprint.blueprints import MachineRenderType, RecipeType
from blueprint.game_blueprint import GameBlueprint
from save.save import GameSaves
from state.game_state import GameState
from tests.constants import default_blueprint_path, default_saves_path


class GameStateTest(unittest.TestCase):

    def setUp(self):
        save = GameSaves.load_from_json(json.dumps({
            "inventory": [],
            "coins": 0,
        }))
        save.is_first_run = True # Pretend game is running for the first time

        self.blueprint = GameBlueprint.load_from_file(default_blueprint_path)
        self.saves = GameSaves(f'{default_saves_path}/test',  {1: save})
        self.state = GameState(self.blueprint, self.saves)

    def test_crop_can_be_planted_and_collected(self):
        """End-to-end test for planting a crop into a fitting machine and collecting it when ready."""

        # --- [0] Setup ---
        # Find first farmland
        farmland = next(
            machine
            for machine in self.state.tiles.values()
            if not machine.is_locked() and machine.blueprint.render == MachineRenderType.CROP
        )

        self.assertIsNotNone(farmland, "Could not find a valid crop machine")

        # Find first crop
        crop = next(
            crop
            for crop in self.state.blueprint.recipes.values()
            if crop.type == RecipeType.CROP
        )

        self.assertIsNotNone(crop, "Could not find a valid crop")

        # Make sure player has 10 of the crop
        crop_amount = self.state.player.inventory.get_item_amount(crop.id)
        self.state.player.inventory.add_item(crop.id, 10 - crop_amount)

        # Plant the crop
        farmland.add_item(crop.id)

        # 1. Planting
        # Ensure that item was taken
        self.assertEqual(self.state.player.inventory.get_item_amount(crop.id), 9)
        # Ensure that the machine has set proper state
        self.assertTrue(farmland.busy, 'Farmland machine should have been busy')
        self.assertFalse(farmland.collectable, 'Farmland machine should NOT have been collectable')
        self.assertEqual(farmland.result, crop)
        self.assertEqual(farmland.time_remaining, crop.time)

        # 2. Half growth
        # Advance time so crop is grown half-way
        self.state.update(crop.time / 2)

        # Test that crop has progressed
        self.assertEqual(farmland.time_remaining, (crop.time / 2), 'Crop should have progressed')

        # 3. Full growth
        # Advance time so crop is fully grown
        self.state.update(crop.time)

        self.assertEqual(farmland.time_remaining, 0, 'Crop should have grown')
        self.assertTrue(farmland.collectable, 'Crop should have been collectable')

        # 4. Collection
        # Collect the crop
        farmland.collect()

        # Test that state has been reset
        self.assertFalse(farmland.busy, 'Farmland machine should NOT have been busy')
        self.assertFalse(farmland.collectable, 'Farmland machine should NOT have been collectable')
        self.assertIsNone(farmland.result)
        self.assertEqual(farmland.time_remaining, 0)

        # Test that the result has been given (+2 from crops)
        self.assertEqual(self.state.player.inventory.get_item_amount(crop.id), 11)

    def test_unlocking_tiles_works(self):
        """End-to-end test to test unlocking new tiles"""

        # Test that configured tiles to be locked are locked
        self.assertCountEqual(self.state.locked_tiles, self.blueprint.constants.locked_tiles_prices.keys())

        # Get a sample locked tile
        sample_tile = next(
            tile
            for tile in self.state.tiles.values()
            if tile.is_locked()
        )

        # Ensure tile has the correct price
        blueprint_tile_price = self.blueprint.constants.locked_tiles_prices[sample_tile.tile]
        self.assertEqual(sample_tile.get_unlock_price(), blueprint_tile_price)

        # Reset player money
        self.state.player.coins = 0

        # Attempt to buy tile without money
        result = sample_tile.unlock()
        self.assertFalse(result, "Should NOT have been able to unlock a tile without money")

        # Set money to required amount
        self.state.player.coins = blueprint_tile_price

        # Attempt to buy tile again
        result = sample_tile.unlock()
        self.assertTrue(result, "Should have been able to unlock a tile")
        self.assertEqual(self.state.player.coins, 0, 'Coins should have been taken')
