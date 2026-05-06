import pygame
from pygame import Surface

from blueprint.game_blueprint import GameBlueprint
from ui.assets import GameAssets

_assets: GameAssets | None = None
_blueprint: GameBlueprint | None = None

def setup(assets: GameAssets, blueprint: GameBlueprint):
    global _assets, _blueprint
    _assets = assets
    _blueprint = blueprint

def is_setup() -> bool:
    global _assets, _blueprint
    return _assets is not None and _blueprint is not None

def centered_bg_text(text: str, bg_color: tuple[int, int, int], icon_id: str = None, padding: int = 5, *, text_color: tuple[int,int,int] = (255,255,255)) -> Surface:
    if not is_setup():
        raise RuntimeError('Tried rendering a common element without setup')

    c_text = _assets.font.render(text, True, text_color)
    c_icon = None

    width = c_text.get_width() + 2 * padding
    height = c_text.get_height() + padding

    if icon_id:
        c_icon = _assets.get_single_sprite(_blueprint, icon_id, 3).main
        width += c_icon.get_width() + padding

    c_surface = pygame.Surface((width, height), pygame.SRCALPHA)
    c_surface_center = c_surface.get_rect().center

    pygame.draw.rect(c_surface, bg_color, c_surface.get_rect(), border_radius=10)

    if c_icon:
        rect = c_icon.get_rect(center=c_surface_center)
        rect.x = padding

        c_surface.blit(c_icon, rect)

        rect.x += c_icon.get_width() + padding
        c_surface.blit(c_text, rect)
    else:
        c_surface.blit(c_text, c_text.get_rect(center=c_surface_center))

    return c_surface
