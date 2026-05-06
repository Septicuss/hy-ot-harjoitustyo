import pygame
from pygame import Surface

from blueprint.blueprints import MachineRenderType, RecipeType
from state.game_state import GameState, Machine
from ui.assets import GameAssets, LoadedMachineSprites
from ui.base_elements import TileUIElement, grid_tile_to_pixel_coord
from ui.elements.effects import ItemMoveEffect, ToastEffect


class MachineUI(TileUIElement):

    bg_color = (255, 251, 210)
    default_border_color = (51, 51, 43)
    pressed_border_color = (140, 140, 140)

    def __init__(self, assets: GameAssets, state: GameState, machine: Machine, tile: int):
        super().__init__(
            bg_color=self.bg_color,
            border_color=self.default_border_color,
            center=grid_tile_to_pixel_coord(assets, tile)
        )

        self.state = state
        self.assets = assets
        self.blueprint = machine.blueprint
        self.machine = machine
        self.machine.on_finish = lambda: self._trigger_finished_effect()
        self.tile = tile

        # State
        self.previously_hit = False
        self.update_timer = 0

        # Crop
        self.is_crop = self.blueprint.render == MachineRenderType.CROP
        self.crop_surface: Surface | None = None

        # Drawn when can collect
        self.collectable_surface: Surface | None = None

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
                (self.assets.screen_width / 2, self.assets.screen_height - 100)
            )
        )

    def order(self) -> int:
        return 1

    def update(self, delta_time: float):

        # Update the things below once every 0.5s
        self.update_timer += delta_time
        if self.update_timer < 0.5:
            return
        self.update_timer = 0

        # If this is a crop machine, update the growth stage sprite
        if self.is_crop:
            result = self.machine.result

            # Not busy
            if not self.machine.busy or result is None:
                self.crop_surface = None
                return

            # Cannot render non crops
            if not result.type == RecipeType.CROP:
                self.crop_surface = None
                return

            time_passed = result.time - self.machine.time_remaining
            done_percentage = (time_passed / result.time) * 100
            stage = 3 if done_percentage >= 99 else 2 if done_percentage >= 50 else 1
            
            sprite = self.assets.get_crop_sprites(self.state.blueprint, result.id)
            sprite_surface = sprite.stage_3 if stage == 3 else sprite.stage_2 if stage == 2 else sprite.stage_1

            self.crop_surface = sprite_surface

        # If item can be collected, pre-render the sprite
        if self.machine.collectable and self.collectable_surface is None:
            result_sprite = self.assets.get_recipe_sprites(self.state.blueprint, self.machine.result.id).main
            result_sprite = pygame.transform.smoothscale(result_sprite, (52, 52))

            # Set cached surface
            self.collectable_surface = result_sprite

    def draw(self, surface: Surface):
        super().draw(surface)

        # Draw crop stage
        if self.is_crop:
            if self.crop_surface:
                surface.blit(self.crop_surface, self.crop_surface.get_rect(center=self.tile_rect.center))
        # Draw regular machine
        else:
            # Draw sprite depending on busy state
            sprite_to_use = self.machine_sprites.busy if self.machine.busy else self.machine_sprites.main
            surface.blit(sprite_to_use, self.machine_icon_dest)

        # Draw collectable item
        if self.collectable_surface is not None:
            surface.blit(self.collectable_surface, self.collectable_surface.get_rect(center=self.tile_rect.midtop))

    def handle_event(self, event):
        mouse_pos = pygame.mouse.get_pos()

        def hit() -> bool:
            return self.hitbox.collidepoint(mouse_pos)


        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.machine.busy:
                return
            if hit() and self.machine.inventory.size() > 0:
                self.border_color = self.pressed_border_color
                self.previously_hit = True

        if event.type == pygame.MOUSEBUTTONUP:
            if hit() and self.machine.collectable:
                self.assets.effects.submit_toast(ToastEffect('success', f'+ {self.machine.result.amount} {self.machine.result.name}'))
                self.machine.collect()
                self.collectable_surface = None
                self.crop_surface = None

            if self.machine.busy:
                return

            if self.border_color == self.pressed_border_color:
                self.border_color = self.default_border_color

            if self.previously_hit:
                self.previously_hit = False

                item = self.machine.remove_last_item()

                # If successfully removed last item, play effect of item going to hotbar
                if item is not None:
                    item_sprite = self.assets.get_recipe_sprites(self.state.blueprint, item.id).main
                    item_sprite = pygame.transform.scale(item_sprite, (32, 32))

                    self.assets.effects.submit_item_move(ItemMoveEffect(
                        item_sprite,
                        self.tile_rect.center,
                        (self.assets.screen_width / 2, self.assets.screen_height - 100)
                    ))
