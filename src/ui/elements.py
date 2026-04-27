import uuid

import pygame
from pygame import Surface, Color, Rect
from pygame.event import Event

from blueprint.blueprints import MachineRenderType
from state.game_state import GameState, Machine
from ui.assets import GameAssets, LoadedItemSprites, LoadedMachineSprites

grid_rows = 3
grid_cols = 3
grid_tile_size = 100
grid_tile_gap = 20
grid_top_padding = 125

def grid_tile_to_pixel_coord(assets: GameAssets, tile: int) -> tuple[int, int]:

    row = tile // grid_rows
    col = tile % grid_cols

    full_width = (grid_tile_size * grid_cols) + (grid_tile_gap * (grid_cols - 1))

    left_padding = ((assets.screen_width - full_width) / 2) + grid_tile_size / 2
    top_padding = grid_top_padding

    return (
        left_padding + (col * grid_tile_size) + (col * grid_tile_gap),
        top_padding + (row * grid_tile_size) + (row * grid_tile_gap),
    )

class UIElement:

    def __init__(self):
        self.id = uuid.uuid4()

    def order(self) -> int:
        """Returns the draw order of this element. Lower ordered element renders first."""
        return 0

    def handle_event(self, event: Event):
        pass

    def update(self, delta_time: float):
        pass

    def draw(self, surface: Surface):
        pass

class TileUIElement(UIElement):
    """Represents a drawn rectangular tile."""
    global grid_tile_size

    # pixel size of the tile
    size = grid_tile_size
    radius = 20
    border_width = 6

    def __init__(self, *,
                 bg_color: Color | tuple[int, int, int],
                 border_color: Color | tuple[int, int, int],
                 center: tuple[float, float]):
        super().__init__()
        self.hitbox: Rect | None = None
        self.bg_color = bg_color
        self.border_color = border_color
        self.center = center

        # Initialize the tile rects
        self.tile_rect = pygame.Rect(
            center[0] - (self.size / 2),
            center[1] - (self.size / 2),
            self.size,
            self.size
        )
        self.tile_bg_rect = self.tile_rect.inflate(-2 * self.border_width, -2 * self.border_width)

    def draw(self, surface: Surface):
        # border
        pygame.draw.rect(
            surface,
            self.border_color,
            self.tile_rect,
            border_radius=self.radius
        )

        # background
        self.hitbox = pygame.draw.rect(
            surface,
            self.bg_color,
            self.tile_bg_rect,
            border_radius=self.radius - self.border_width
        )


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

        # Whether the current item is being dragged
        self.dragging = False

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
                    self.dragging = True

        if event.type == pygame.MOUSEBUTTONUP:
            if not self.dragging:
                return

            self.dragging = False
            for tile in list(self.assets.tiles.values()):
                if tile.hitbox.collidepoint(mouse_pos):
                    tile.machine.add_item(self.state.player.get_selected_item())

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_q:
                self.state.player.cycle_selected_item('left')
            if event.key == pygame.K_e:
                self.state.player.cycle_selected_item('right')


    def update(self, delta_time: float):
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

        if self.dragging: # Draw the dragged item sprite
            mouse_pos = pygame.mouse.get_pos()
            item_width = self.sprite.main.get_width()
            item_height = self.sprite.main.get_height()

            surface.blit( # Item sprite
                self.sprite.main,
                (mouse_pos[0] - item_width / 2, mouse_pos[1] - item_height / 2)
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



class MachineUI(TileUIElement):

    bg_color = (255, 251, 210)
    border_color = (51, 51, 43)

    def __init__(self, assets: GameAssets, state: GameState, machine: Machine, tile: int):
        super().__init__(
            bg_color=self.bg_color,
            border_color=self.border_color,
            center=grid_tile_to_pixel_coord(assets, tile)
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

