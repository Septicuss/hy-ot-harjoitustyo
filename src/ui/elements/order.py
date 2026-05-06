import pygame
from pygame import Surface

from blueprint.blueprints import ItemReference
from state.game_state import GameState
from ui.assets import GameAssets
from ui.base_elements import TileUIElement


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

        def centered_bg_text(text: str, bg_color: tuple[int, int, int], icon_id: str = None) -> Surface:
            c_text = self.assets.font.render(text, True, (255, 255, 255))
            c_icon = None

            width = c_text.get_width() + 2 * self.padding
            height = c_text.get_height() + self.padding

            if icon_id:
                c_icon = self.assets.get_single_sprite(self.state.blueprint, icon_id, 3).main
                width += c_icon.get_width() + self.padding

            c_surface = pygame.Surface((width, height), pygame.SRCALPHA)
            c_surface_center = c_surface.get_rect().center

            pygame.draw.rect(c_surface, bg_color, c_surface.get_rect(), border_radius=10)


            if c_icon:
                rect = c_icon.get_rect(center=c_surface_center)
                rect.x = self.padding

                c_surface.blit(c_icon, rect)

                rect.x += c_icon.get_width() + self.padding
                c_surface.blit(c_text, rect)
            else:
                c_surface.blit(c_text, c_text.get_rect(center=c_surface_center))


            return c_surface

        surface = pygame.Surface((self.tile_rect.width + 100, self.tile_rect.height + 100), pygame.SRCALPHA)

        icon = self.assets.get_recipe_sprites(self.state.blueprint, self.order_item.id).main
        amount = centered_bg_text(str(self.order_item.amount), self.amount_bg_color)
        reward = centered_bg_text(str(self.orders.reward), self.reward_bg_color, "coin")

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
