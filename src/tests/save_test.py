import os
import shutil
import unittest

from blueprint.blueprints import ItemReference
from save.save import GameSaves
from tests.constants import default_saves_path


class TestGameSaves(unittest.TestCase):

    def setUp(self):
        self.__prepare_test_files(1)
        self.saves_1 = GameSaves(f'{default_saves_path}/test')
        self.saves_1.load_saves()

    def __prepare_test_files(self, case: int):
        path = f'{default_saves_path}/{case}'
        dest = f'{default_saves_path}/test'

        # Clear existing files in test directory
        existing = os.listdir(dest)
        for file_name in existing:
            full_file_name = os.path.join(dest, file_name)
            if os.path.isfile(full_file_name):
                os.remove(full_file_name)

        # Copy test case save files into test directory
        files = os.listdir(path)
        for file_name in files:
            full_file_name = os.path.join(path, file_name)
            if os.path.isfile(full_file_name):
                shutil.copy(full_file_name, dest)

    def test_save_loads_values_correctly(self):
        save = self.saves_1.get_save(1)

        self.assertEqual(save.coins, 55)
        self.assertCountEqual(save.locked_tiles, [1, 2, 3])
        self.assertCountEqual(save.inventory, [ItemReference('wheat'), ItemReference('berry'), ItemReference('soy')])

    def test_save_is_saved_correctly_after_modification(self):
        save = self.saves_1.get_save(1)
        save.coins = 5

        self.saves_1.save(save, 1)
        self.saves_1.load_saves()

        after_save = self.saves_1.get_save(1)

        self.assertEqual(after_save.coins, 5)
        self.assertCountEqual(after_save.locked_tiles, [1, 2, 3])
        self.assertCountEqual(after_save.inventory, [ItemReference('wheat'), ItemReference('berry'), ItemReference('soy')])

    def test_save_without_inventory_loads_correctly(self):
        save = self.saves_1.get_save(2)

        self.assertCountEqual(save.inventory, [])

    def test_loading_empty_slots_returns_default_save(self):
        save = self.saves_1.load_save(3) # does not exist

        self.assertEqual(save.coins, 0)
        self.assertCountEqual(save.locked_tiles, [])
        self.assertCountEqual(save.inventory, [])

    def test_loading_emtpy_file_returns_default_save(self):
        save = self.saves_1.load_save(4) # exists but is empty

        self.assertEqual(save.coins, 0)
        self.assertCountEqual(save.locked_tiles, [])
        self.assertCountEqual(save.inventory, [])

class TestGameSave(unittest.TestCase):
    pass