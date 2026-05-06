import pygame
from pygame import Surface

from blueprint.blueprints import ItemReference
from state.game_state import GameState
from ui.assets import GameAssets
from ui.base_elements import TileUIElement
from ui.common import centered_bg_text


class OrderUI(TileUIElement):

    padding = 5
    bg_color = (227, 222, 172)
    reward_bg_color = (194, 185, 29)
    reward_text_color = (255, 255, 255)
    amount_bg_color = (56, 56, 56)
    amount_text_color = (255, 255, 255)

    def __init__(self, assets: GameAssets, state: GameState):
        super().__init__(
            bg_color=self.bg_color,
            border_color=self.bg_color,
            center=(assets.screen_width / 2 / 2 / 2, assets.screen_height - 100)
        )
        self.assets = assets
        self.state = state

        self.orders = self.state.orders

        self.order_item: ItemReference | None = None
        self.order_surface: Surface | None = None

    def reset(self):
        self.order_item = None
        self.order_surface = None

    def order(self) -> int:
        return 1

    def update(self, delta_time: float):

        # No order yet
        if not self.orders.order or not self.tile_rect:
            return

        # No updates needed
        if self.order_item and self.orders.order == self.order_item:
            return

        self.order_item = self.orders.order


        surface = pygame.Surface((self.tile_rect.width + 100, self.tile_rect.height + 100), pygame.SRCALPHA)

        icon = self.assets.get_recipe_sprites(self.state.blueprint, self.order_item.id).main
        amount = centered_bg_text(str(self.order_item.amount), self.amount_bg_color, padding=self.padding)
        reward = centered_bg_text(str(self.orders.reward), self.reward_bg_color, "coin", padding=self.padding)

        surface_rect = surface.get_rect()
        surface_rect.size = (self.tile_rect.width, self.tile_rect.height)
        surface_rect.center = surface.get_rect().center

        surface.blit(icon, icon.get_rect(center=surface_rect.center))
        surface.blit(reward, reward.get_rect(center=surface_rect.midtop))
        surface.blit(amount, amount.get_rect(center=surface_rect.bottomleft))

        self.order_surface = surface

    def draw(self, surface: Surface):
        super().draw(surface)

        if self.order_surface:
            surface.blit(self.order_surface, self.order_surface.get_rect(center=self.tile_rect.center))

        pass
