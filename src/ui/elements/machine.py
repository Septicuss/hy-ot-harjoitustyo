import pygame
from pygame import Surface

from blueprint.blueprints import MachineRenderType
from state.game_state import GameState, Machine
from ui.assets import GameAssets, LoadedMachineSprites
from ui.base_elements import TileUIElement, grid_tile_to_pixel_coord
from ui.elements.effects import ItemMoveEffect


class MachineUI(TileUIElement):

    bg_color = (255, 251, 210)
    border_color = (51, 51, 43)

    def __init__(self, assets: GameAssets, state: GameState, machine: Machine, tile: int):
        super().__init__(
            bg_color=self.bg_color,
            border_color=self.border_color,
            center=grid_tile_to_pixel_coord(assets, tile)
        )

        self.state = state
        self.assets = assets
        self.blueprint = machine.blueprint
        self.machine = machine
        self.machine.on_finish = lambda: self._trigger_finished_effect()
        self.tile = tile

        self.is_crop = self.blueprint.render == MachineRenderType.CROP

        # do not initialize sprites, as crops use dynamic sprites
        if self.is_crop:
            return

        self.machine_sprites: LoadedMachineSprites = assets.get_machine_sprites(state.blueprint, machine.blueprint.id)
        self.machine_icon_dest = (
            (self.center[0] - self.machine_sprites.main.get_width() / 2),
            (self.center[1] - self.machine_sprites.main.get_height() / 2)
        )

    def _trigger_finished_effect(self):
        icon_sprite = self.assets.get_recipe_sprites(self.state.blueprint, self.machine.result.id).main
        icon_sprite = pygame.transform.scale(icon_sprite, (32, 32))

        self.assets.effects.submit_item_move(ItemMoveEffect(
                icon_sprite,
                self.tile_rect.center,
                (self.assets.screen_width / 2, self.assets.screen_height + 50)
            )
        )

    def order(self) -> int:
        return 1

    def update(self, delta_time: float):
        pass

    def draw(self, surface: Surface):
        super().draw(surface)

        if self.is_crop:
            return

        # Draw sprite depending on busy state
        sprite_to_use = self.machine_sprites.busy if self.machine.busy else self.machine_sprites.main
        surface.blit(sprite_to_use, self.machine_icon_dest)

    def handle_event(self, event):
        pass

