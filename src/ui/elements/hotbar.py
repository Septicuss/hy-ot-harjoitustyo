from enum import Enum

import pygame
from pygame import Surface

from state.game_state import GameState
from ui.assets import GameAssets, LoadedItemSprites
from ui.base_elements import TileUIElement


class HotbarState(Enum):
    IDLE=0,
    DRAGGING=1,
    SPRING=2,


class HotbarUI(TileUIElement):

    bottom_padding_percentage: float = 0.1
    hotbar_bg_color = (227, 222, 172)
    hotbar_tooltip_text_color = (0, 0, 0)
    hotbar_amount_text_color = (255, 255, 255)
    hotbar_amount_bg_color = (56, 56, 56)

    def __init__(self, assets: GameAssets, state: GameState):
        super().__init__(
            bg_color=self.hotbar_bg_color,
            border_color=self.hotbar_bg_color,
            center=(assets.screen_width / 2, assets.screen_height - 100)
        )

        # Assets
        self.inventory = state.player.inventory
        self.state = state
        self.font = assets.font
        self.assets = assets

        # Dragging state
        self.drag_state: HotbarState = HotbarState.IDLE
        self.drag_position: tuple[int, int] | None = None

        # Hints (Q, E)
        hint_padding = 10
        hint_size = 40
        hint_y = self.tile_rect.y + self.tile_rect.height/2 - hint_size/2

        def create_hint(key, x):
            rect = pygame.Rect(x, hint_y, hint_size, hint_size)
            text = self.font.render(key, True, self.hotbar_tooltip_text_color)
            return rect, text

        self.hints = [
            create_hint('Q', self.tile_rect.x - hint_padding - hint_size),
            create_hint('E', self.tile_rect.x + self.tile_rect.width + hint_padding)
        ]

        # Selected item sprites
        self.selected_item_id = None
        self.selected_item_amount = None
        self.sprite: LoadedItemSprites | None = None
        self.tooltip = None
        self.amount_text = None
        self.amount_rect = None

    def order(self) -> int:
        return 2

    def handle_event(self, event):
        mouse_pos = pygame.mouse.get_pos()

        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.hitbox.collidepoint(mouse_pos):
                if self.selected_item_id is not None:
                    self.drag_state = HotbarState.DRAGGING

        if event.type == pygame.MOUSEBUTTONUP:
            if self.drag_state != HotbarState.DRAGGING:
                return

            for tile in list(self.assets.tiles.values()):
                if tile.hitbox.collidepoint(mouse_pos):
                    success = tile.machine.add_item(self.state.player.get_selected_item())
                    if success:
                        self.drag_state = HotbarState.IDLE
                        return

            self.drag_state = HotbarState.SPRING
            self.drag_position = mouse_pos

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_q:
                self.state.player.cycle_selected_item('left')
            if event.key == pygame.K_e:
                self.state.player.cycle_selected_item('right')

    def _update_animation(self, delta_time: float):

        # Animate item returning back to inventory
        if self.drag_state == HotbarState.SPRING:

            if self.drag_position is None:
                self.drag_state = HotbarState.IDLE
                return

            speed = 10
            target_x, target_y = self.tile_rect.center
            current_x, current_y = self.drag_position

            current_x += (target_x - current_x) * speed * delta_time
            current_y += (target_y - current_y) * speed * delta_time

            close_enough = abs(current_x - target_x) < 5 and abs(current_y - target_y) < 5
            if close_enough:
                self.drag_state = HotbarState.IDLE
                self.drag_position = None
                return

            self.drag_position = (current_x, current_y)

    def update(self, delta_time: float):
        self._update_animation(delta_time)

        selected_item_id = self.state.player.get_selected_item()
        selected_item_amount = self.state.player.inventory.get_item_amount(selected_item_id)

        # Only update if selected item or its amount changed
        if selected_item_id is self.selected_item_id and selected_item_amount == self.selected_item_amount:
            return

        if selected_item_id is None:
            self.selected_item_id = None
            self.selected_item_amount = None
            self.sprite = None
            self.tooltip = None
            self.amount_text = None
            self.amount_rect = None
            return

        selected_item_name = self.state.blueprint.get_game_element(selected_item_id).name

        # Update displayed selected hotbar item UI
        self.sprite: LoadedItemSprites = self.assets.get_recipe_sprites(self.state.blueprint, selected_item_id)
        self.selected_item_id = selected_item_id
        self.tooltip = self.font.render(selected_item_name, True, self.hotbar_tooltip_text_color)
        self.amount_text = self.font.render(str(selected_item_amount), True, self.hotbar_amount_text_color)
        self.amount_rect = pygame.Rect((self.tile_rect.x - (self.amount_text.get_width() - 5)), self.tile_rect.y + self.tile_rect.height - 20, self.amount_text.get_width() * 2, 40)

    def draw(self, surface: Surface):
        super().draw(surface)

        # Draw hints
        for rect, text in self.hints:
            pygame.draw.rect(surface, self.hotbar_bg_color, rect, border_radius=5)
            surface.blit(
                text,
                text.get_rect(center=rect.center)
            )

        if self.drag_state == HotbarState.DRAGGING or self.drag_state == HotbarState.SPRING: # Draw the dragged item sprite

            # If dragging, use cursor pos, if animating use state position
            dragging = self.drag_state == HotbarState.DRAGGING
            x, y = pygame.mouse.get_pos() if dragging else self.drag_position

            item_width = self.sprite.main.get_width()
            item_height = self.sprite.main.get_height()

            surface.blit( # Item sprite
                self.sprite.main,
                (x - item_width / 2, y - item_height / 2)
            )

        # Draw selected item if present
        if self.selected_item_id is not None:
            surface.blit( # Item sprite
                self.sprite.main,
                (self.tile_rect.x + 10, self.tile_rect.y + 10)
            )
            surface.blit( # Tooltip text
                self.tooltip,
                ((self.assets.screen_width / 2) - (self.tooltip.get_width() / 2),
                 self.tile_rect.y - 50)
            )
            pygame.draw.rect( # Item amount background
                surface,
                self.hotbar_amount_bg_color,
                self.amount_rect,
                border_radius=20
            )
            surface.blit( # Item amount text
                self.amount_text,
                (self.amount_rect.x + (self.amount_text.get_width() / 2), self.amount_rect.y + (self.amount_text.get_height() / 2))
            )
