from typing import TypedDict

import pygame
from pygame import Surface, Rect

from state.game_state import GameState
from ui.assets import GameAssets
from ui.base_elements import UIElement


class HudState(TypedDict):
    coins: int

class HudUI(UIElement):

    padding = 20

    def __init__(self, assets: GameAssets, state: GameState):
        super().__init__()
        self.assets = assets
        self.state = state

        self.hud: Surface | None = None
        self.hitbox: Rect = pygame.Rect(0,0,0,0)
        self.hud_state = HudState(coins=self.state.player.coins)
        self.update_timer: float = 0

    def order(self) -> int:
        return 8

    def update(self, delta_time: float):

        # Update every 0.3s
        self.update_timer += delta_time
        if self.hud and self.update_timer < 0.3:
            return
        self.update_timer = 0

        # Update hud if states differ or hud is not yet set
        new_state = HudState(coins=self.state.player.coins)

        # Draw hud
        if not self.hud or self.hud_state != new_state:
            self.hud_state = new_state

            hud_text = self.assets.font.render(str(self.hud_state['coins']), True, (0, 0, 0))
            hud_icon = self.assets.get_single_sprite(self.state.blueprint, 'coin', 3).main

            width = hud_icon.get_width() + self.padding + hud_text.get_width()
            height = max(hud_text.get_height(), hud_icon.get_height()) + self.padding
            hud = pygame.Surface((width, height), pygame.SRCALPHA)

            hud.blit(hud_icon, (0,0))
            hud.blit(hud_text, (hud_icon.get_width() + 5,0))

            self.hud = hud
            self.hitbox = self.hud.get_rect().scale_by(1.1, 1.1)
            self.hitbox.x = int(self.padding / 2)
            self.hitbox.y = int(self.padding / 2)

    def draw(self, surface: Surface):

        if self.hud:
            surface.blit(self.hud, (self.padding,self.padding))
        pass