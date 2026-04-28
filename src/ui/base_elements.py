import uuid

import pygame
from pygame import Surface, Color, Rect
from pygame.event import Event

from ui.assets import GameAssets

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
