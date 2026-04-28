import pygame
from pygame import Surface
from pygame.event import Event

from state.game_state import GameState, Machine
from ui.assets import GameAssets
from ui.base_elements import UIElement, TileUIElement, MachineUI


class TooltipUI(UIElement):

    icon_size = 32
    icon_padding = 10
    icon_bg_color = (189, 184, 142)
    icon_present_bg_color = (170, 201, 147)
    tooltip_bg_color = (227, 222, 172)
    bar_width = 100
    bar_height = 20
    bar_bg_color = (189, 184, 142)
    bar_filled_bg_color = (170, 201, 147)

    def __init__(self, assets: GameAssets, state: GameState):
        super().__init__()
        self.assets = assets
        self.state = state

        # Tracking which tile to show tooltip for
        self.previous_mouse_pos = None
        self.potential_tile = None
        self.potential_tile_timer = 0

        # Chosen tile that a tooltip is shown for
        self.tooltip_tile = None

        # Pre-rendered tooltip
        self.tooltip: Surface | None = None
        self.tooltip_update_timer: float = 0

    def order(self) -> int:
        return 9 # tooltips render above everything

    def _reset(self):
        self.potential_tile = None
        self.potential_tile_timer = 0
        self.tooltip_tile = None
        self.tooltip = None

    def handle_event(self, event: Event):
        mouse_pos = pygame.mouse.get_pos()

        if event.type == pygame.MOUSEMOTION:

            # Reset tooltip if mouse left original tile
            if self.tooltip_tile:
                if not self.tooltip_tile.hitbox.collidepoint(mouse_pos):
                    self._reset()

            # Check for new potential tiles
            for tile in list(self.assets.tiles.values()):
                if tile is None or tile.hitbox is None: continue
                if tile.hitbox.collidepoint(mouse_pos) and self.potential_tile is not tile:
                    self._reset()
                    self.potential_tile = tile
                    break

    def _handle_set_tooltip(self, tile: TileUIElement):

        def tooltip(surface: Surface, title_text: str = "Tooltip", padding: int = 10) -> Surface:
            """Wraps a surface within a tooltip background with given padding"""

            title = self.assets.font.render(title_text, True, (0, 0, 0))

            padding_top = title.get_height() + padding

            wrapper = pygame.Surface((surface.get_width() + 2 * padding, surface.get_height() + padding_top + padding), pygame.SRCALPHA)
            wrapper_rect = pygame.Rect(0, 0, wrapper.get_width(), wrapper.get_height())
            pygame.draw.rect(wrapper, self.tooltip_bg_color, wrapper_rect, border_radius=10)
            wrapper.blit(surface, (padding, padding_top))

            title_rect = title.get_rect(center=wrapper_rect.midtop)
            title_rect.y = title_rect.centery + padding
            wrapper.blit(title, title_rect)

            return wrapper

        # Set machine tooltip
        if isinstance(tile, MachineUI):
            machine: Machine = tile.machine

            def item_icon(item_id: str, present: bool = False) -> Surface:
                icon_surface = pygame.Surface((self.icon_size + self.icon_padding, self.icon_size + self.icon_padding), pygame.SRCALPHA)
                icon_bg = pygame.Rect(
                    0, 0, icon_surface.get_width(), icon_surface.get_height()
                )
                icon = pygame.transform.scale(
                    surface=self.assets.get_recipe_sprites(self.state.blueprint, item_id).main,
                    size=(self.icon_size, self.icon_size)
                )

                bg_color = self.icon_present_bg_color if present else self.icon_bg_color

                pygame.draw.rect(icon_surface, bg_color, icon_bg, border_radius=10)
                icon_surface.blit(icon, icon.get_rect(center=icon_bg.center))
                return icon_surface

            def item_row(items: list[tuple[str, bool]]) -> Surface:
                item_icons = [item_icon(item_id, present) for item_id, present in items]
                item_icon_width = max(icon.get_width() for icon in item_icons)
                item_icon_height = max(icon.get_height() for icon in item_icons)

                row_surface = pygame.Surface(
                    (len(item_icons) * (item_icon_width + self.icon_padding) - self.icon_padding, item_icon_height),
                    pygame.SRCALPHA
                ).convert_alpha()

                index = 0
                for icon in item_icons:
                    x = (index * (item_icon_width + self.icon_padding))
                    row_surface.blit(icon, (x, 0))
                    index += 1

                return row_surface

            def machine_info(item_rows: list[list[tuple[str, bool]]]):
                rows = [item_row(items) for items in item_rows]
                width = max(r.get_width() for r in rows) + (2 * self.icon_padding)
                height = sum(r.get_height() for r in rows) + self.icon_padding * (len(rows) + 1)

                surface = pygame.Surface((width, height), pygame.SRCALPHA).convert_alpha()

                y = self.icon_padding
                for row in rows:
                    surface.blit(row, (self.icon_padding, y))
                    y += row.get_height() + self.icon_padding

                return surface

            def machine_progress_bar():
                total_time = self.state.blueprint.recipes.get(machine.result).time
                time_remaining = machine.time_remaining
                time_passed = total_time - time_remaining
                progress_width = self.bar_width * (time_passed / total_time)

                bar_surface = pygame.Surface((self.bar_width, self.bar_height), pygame.SRCALPHA)
                bar_bg = bar_surface.get_rect()

                pygame.draw.rect(bar_surface, self.bar_bg_color, bar_bg, border_radius=50)
                bar_bg.width = int(progress_width)
                pygame.draw.rect(bar_surface, self.bar_filled_bg_color, bar_bg, border_radius=50)

                return bar_surface

            self.tooltip = tooltip(
                surface=machine_progress_bar() if machine.busy else machine_info(machine.get_recipe_array()),
                padding=self.icon_padding,
                title_text=machine.blueprint.name
            )


    def update(self, delta_time: float):
        self.tooltip_update_timer += delta_time

        # Update tooltip every 100ms
        if self.tooltip_update_timer >= 0.1:
            self._handle_set_tooltip(self.tooltip_tile)
            self.tooltip_update_timer = 0

        if self.tooltip_tile is not None:
            return

        self.potential_tile_timer += delta_time

        if self.potential_tile is not None and self.potential_tile_timer >= 0.5:
            self.tooltip_tile = self.potential_tile
            self._handle_set_tooltip(self.tooltip_tile)

    def draw(self, surface: Surface):

        # TODO: avoid recalculation by checking last mouse pos & save coord
        if self.tooltip_tile and self.tooltip:
            mx, my = pygame.mouse.get_pos()
            width = self.tooltip.get_width()
            height = self.tooltip.get_height()
            x = mx
            y = my - height

            if mx + width > self.assets.screen_width:
                x = mx - width

            surface.blit(
                self.tooltip,
                (x, y)
            )

            self.previous_mouse_pos = pygame.mouse.get_pos()
