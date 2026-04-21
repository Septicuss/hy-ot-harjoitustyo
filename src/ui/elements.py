import uuid

import pygame
from pygame import Surface, Color

from blueprint.blueprints import MachineRenderType
from state.game_state import GameState, Machine
from ui.assets import GameAssets, LoadedItemSprites, LoadedMachineSprites

grid_rows = 3
grid_cols = 3
grid_cell_size = 100
grid_cell_gap = 20
grid_top_padding = 125

def grid_slot_to_pixel_coord(assets: GameAssets, grid_slot: int) -> tuple[int, int]:

    row = grid_slot // grid_rows
    col = grid_slot % grid_cols

    full_width = (grid_cell_size * grid_cols) + (grid_cell_gap * (grid_cols - 1))

    left_padding = ((assets.screen_width - full_width) / 2) + grid_cell_size / 2
    top_padding = grid_top_padding

    return (
        left_padding + (col * grid_cell_size) + (col * grid_cell_gap),
        top_padding + (row * grid_cell_size) + (row * grid_cell_gap),
    )

class UIElement:

    def __init__(self):
        self.id = uuid.uuid4()

    def order(self) -> int:
        """Returns the draw order of this element. Lower ordered element renders first."""
        return 0

    def handle_event(self, event):
        pass

    def update(self, delta_time: float):
        pass

    def draw(self, surface: Surface):
        pass

class NodeUIElement(UIElement):
    """Represents a drawn rectangular node."""
    global grid_cell_size

    # pixel size of the node
    size = grid_cell_size
    radius = 20
    border_width = 6

    def __init__(self, *,
                 bg_color: Color | tuple[int, int, int],
                 border_color: Color | tuple[int, int, int],
                 center: tuple[float, float]):
        super().__init__()
        self.bg_color = bg_color
        self.border_color = border_color
        self.center = center

        # Initialize the node rects
        self.node_rect = pygame.Rect(
            center[0] - (self.size / 2),
            center[1] - (self.size / 2),
            self.size,
            self.size
        )
        self.node_bg_rect = self.node_rect.inflate(-2 * self.border_width, -2 * self.border_width)

    def draw(self, surface: Surface):
        # border
        pygame.draw.rect(
            surface,
            self.border_color,
            self.node_rect,
            border_radius=self.radius
        )

        # background
        pygame.draw.rect(
            surface,
            self.bg_color,
            self.node_bg_rect,
            border_radius=self.radius - self.border_width
        )


class HotbarUI(NodeUIElement):

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
        self.inventory = state.player.inventory
        self.state = state
        self.font = assets.font
        self.assets = assets

        # Temporary
        self.text = self.font.render("Click anywhere to change selected item", True, (0, 0, 0))

        # Selected item sprites
        self.sprite_id = None
        self.sprite: LoadedItemSprites | None = None
        self.tooltip = None
        self.amount_text = None
        self.amount_rect = None

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONUP:
            self.state.player.cycle_selected_item()

    def update(self, delta_time: float):
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
        self.amount_rect = pygame.Rect((self.node_rect.x - (self.amount_text.get_width() - 5)), self.node_rect.y + self.node_rect.height - 20, self.amount_text.get_width() * 2, 40)

    def draw(self, surface: Surface):
        super().draw(surface)
        
        # Temporary help text
        surface.blit(self.text, (0, 0))

        # Draw selected item if present
        if self.sprite_id is not None:
            surface.blit( # Item sprite
                self.sprite.main,
                (self.node_rect.x + 10, self.node_rect.y + 10)
            )
            surface.blit( # Tooltip text
                self.tooltip,
                ((self.assets.screen_width / 2) - (self.tooltip.get_width() / 2),
                 self.node_rect.y - 50)
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


class MachineUI(NodeUIElement):

    bg_color = (255, 251, 210)
    border_color = (51, 51, 43)

    def __init__(self, assets: GameAssets, state: GameState, machine: Machine, grid_slot: int):
        super().__init__(
            bg_color=self.bg_color,
            border_color=self.border_color,
            center=grid_slot_to_pixel_coord(assets, grid_slot)
        )

        self.blueprint = machine.blueprint
        self.machine = machine

        self.is_crop = self.blueprint.render == MachineRenderType.CROP

        # do not initialize sprites, as crops use dynamic sprites
        if self.is_crop:
            return

        self.machine_sprites: LoadedMachineSprites = assets.get_machine_sprites(state.blueprint, machine.blueprint.id)
        self.machine_icon_dest = (
            (self.center[0] - self.machine_sprites.main.get_width() / 2),
            (self.center[1] - self.machine_sprites.main.get_height() / 2)
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

