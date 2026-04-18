import pygame
from pygame import Surface

from state.game_state import GameState
from ui.assets import GameAssets, LoadedItemSprites


class UIElement:

    def order(self) -> int:
        """Returns the draw order of this element. Lower ordered element renders first."""
        return 0

    def handle_event(self, event):
        pass

    def update(self):
        pass

    def draw(self, surface: Surface):
        pass


class HotbarUI(UIElement):

    bottom_padding_percentage: float = 0.1
    hotbar_bg_color = (227, 222, 172)
    hotbar_tooltip_text_color = (0, 0, 0)
    hotbar_amount_text_color = (255, 255, 255)
    hotbar_amount_bg_color = (56, 56, 56)

    def __init__(self, assets: GameAssets, state: GameState):
        self.inventory = state.player.inventory
        self.state = state
        self.font = assets.font
        self.assets = assets

        # Temporary
        self.text = self.font.render("Click anywhere to change selected item", True, (0, 0, 0))

        # Compute hotbar rectangle pos & size
        width = 100
        self.rect = pygame.Rect(
            (assets.screen_width / 2) - (width / 2),
            (assets.screen_height - width) - (assets.screen_height * self.bottom_padding_percentage),
            width,
            width
        )

        # Selected item sprites
        self.sprite_id = None
        self.sprite: LoadedItemSprites | None = None
        self.tooltip = None
        self.amount_text = None
        self.amount_rect = None

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONUP:
            self.state.player.cycle_selected_item()

    def update(self):
        selected_item_id = self.state.player.get_selected_item()

        if selected_item_id is self.sprite_id:
            return

        item_amount = self.state.player.inventory.get_item_amount(selected_item_id)
        item_name = self.state.blueprint.get_game_element(selected_item_id).name

        # Update displayed selected hotbar item UI
        self.sprite: LoadedItemSprites = self.assets.get_recipe_sprites(self.state.blueprint, selected_item_id)
        self.sprite_id = selected_item_id
        self.tooltip = self.font.render(item_name, True, self.hotbar_tooltip_text_color)
        self.amount_text = self.font.render(str(item_amount), True, self.hotbar_amount_text_color)
        self.amount_rect = pygame.Rect((self.rect.x - (self.amount_text.get_width() - 5)), self.rect.y + self.rect.height - 20, self.amount_text.get_width() * 2, 40)

    def draw(self, surface: Surface):

        # Temporary help text
        surface.blit(self.text, (0, 0))

        # Draw the main hotbar background
        pygame.draw.rect(surface, self.hotbar_bg_color, self.rect, border_radius=20)

        # Draw selected item if present
        if self.sprite_id is not None:
            surface.blit( # Item sprite
                self.sprite.main,
                (self.rect.x + 10, self.rect.y + 10)
            )
            surface.blit( # Tooltip text
                self.tooltip,
                ((self.assets.screen_width / 2) - (self.tooltip.get_width() / 2),
                 self.rect.y - 50)
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

        pass


# TODO: Implement
class MachineUI(UIElement):

    def __init__(self, assets: GameAssets, state: GameState):
        pass

    def order(self) -> int:
        return 1

    def update(self):
        pass

    def draw(self, surface: Surface):
        pass

    def handle_event(self, event):
        pass

