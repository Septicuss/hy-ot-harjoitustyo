from dataclasses import dataclass

import pygame
from pygame import Surface

from blueprint.game_blueprint import GameBlueprint


@dataclass
class LoadedCropSprites:
    main: Surface
    stage_1: Surface
    stage_2: Surface
    stage_3: Surface

@dataclass
class LoadedMachineSprites:
    main: Surface
    busy: Surface

@dataclass
class LoadedItemSprites:
    main: Surface

class GameAssets:
    """Utility class which stores values and assets used by the game UI"""

    def __init__(self, screen_size: tuple[int, int]):
        # Properties
        self.screen_size = screen_size
        self.screen_width = self.screen_size[0]
        self.screen_height = self.screen_size[1]

        # Objects
        self.font = pygame.font.Font("src/ui/assets/font.ttf", 20)

        # Spritesheet
        self.sheet = pygame.image.load("src/ui/assets/sprites.png").convert_alpha()
        self.scale = 10

    def get_crop_sprites(self, blueprint: GameBlueprint, crop_id: str) -> LoadedCropSprites:
        crop_sprite_mappings = blueprint.sprites.get_crop_sprites(crop_id)
        return LoadedCropSprites(
            self.get_sprite(crop_sprite_mappings.main),
            self.get_sprite(crop_sprite_mappings.stage_1),
            self.get_sprite(crop_sprite_mappings.stage_2),
            self.get_sprite(crop_sprite_mappings.stage_3),
        )

    def get_machine_sprites(self, blueprint: GameBlueprint, machine_id: str) -> LoadedMachineSprites:
        machine_sprite_mappings = blueprint.sprites.get_machine_sprites(machine_id)
        return LoadedMachineSprites(
            self.get_sprite(machine_sprite_mappings.main),
            self.get_sprite(machine_sprite_mappings.busy),
        )

    def get_recipe_sprites(self, blueprint: GameBlueprint, item_id: str) -> LoadedItemSprites:
        # TODO: Create an item sprites method in sprites blueprint
        recipe = blueprint.recipes.get(item_id)
        recipe_sprite_mappings = blueprint.sprites.get_recipe_sprites(recipe_id=item_id, recipe_type=recipe.type)
        return LoadedItemSprites(
            self.get_sprite(recipe_sprite_mappings.main),
        )

    def get_sprite(self, col_row: tuple[int, int], scale: int = None):
        """Gets the raw sprite image from the main 8x8 pixel spritesheet given a tuple of its position (col, row)"""
        if scale is None:
            scale = self.scale

        col, row = col_row
        rect = pygame.Rect(col * 8, row * 8, 8, 8)
        image = self.sheet.subsurface(rect)

        return pygame.transform.scale(
            image,
            (8 * scale, 8 * scale)
        )