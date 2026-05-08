from typing import Literal
from uuid import uuid4

import pygame
from pygame import Surface

from state.game_state import GameState
from ui.assets import GameAssets
from ui.base_elements import UIElement


class ItemMoveEffect:

    def __init__(self, item: Surface, move_from: tuple[int, int], move_to: tuple[int, int]):
        self.id = uuid4()
        self.item = item
        self.move_from = move_from
        self.move_to = move_to
        self.current = self.move_from

class ToastEffect:

    default_color = (0, 0, 0)
    success_color = (3, 251, 11)
    error_color = (253, 3, 11)

    def __init__(self, variant: Literal['default', 'success', 'error'], text: str, duration: int = 3):
        self.color = self.error_color if variant == 'error' \
            else self.success_color if variant == 'success' \
            else self.default_color
        self.text: str = text
        self.duration: int = duration

        self.passed: float = 0
        self.toast: Surface | None = None

class EffectUI(UIElement):

    padding = 20
    fadeout_seconds = 1.5

    def __init__(self, assets: GameAssets, state: GameState):
        super().__init__()

        self.assets = assets
        self.state = state

        self.item_move_effects: list[ItemMoveEffect] = []
        self.toast_effects: list[ToastEffect] = []

    def submit_item_move(self, item_move: ItemMoveEffect):
        self.item_move_effects.append(item_move)

    def submit_toast(self, toast: ToastEffect):
        self.toast_effects.append(toast)

    def _process_item_move_effects(self, delta_time: float):
        for effect in self.item_move_effects:
            speed = 10
            target_x, target_y = effect.move_to
            current_x, current_y = effect.current

            current_x += (target_x - current_x) * speed * delta_time
            current_y += (target_y - current_y) * speed * delta_time

            close_enough = abs(current_x - target_x) < 5 and abs(current_y - target_y) < 5
            if close_enough:
                self.item_move_effects.remove(effect)
                return

            effect.current = (current_x, current_y)

    def _process_toast_effects(self, delta_time: float):
        for effect in self.toast_effects:
            effect.passed += delta_time
            fading_progress = (effect.passed / (effect.duration + self.fadeout_seconds)) * 100

            if not effect.toast:
                toast_text = self.assets.font.render(effect.text, True, (0, 0, 0))
                toast_width = toast_text.get_width() + self.padding
                toast_height = toast_text.get_height() + self.padding
                toast = pygame.Surface((toast_width, toast_height), pygame.SRCALPHA)
                pygame.draw.rect(toast, effect.color, toast.get_rect(), border_radius=10)
                toast.blit(toast_text, toast_text.get_rect(center=toast.get_rect().center))

                effect.toast = toast

            if fading_progress >= 100:
                self.toast_effects.remove(effect)

    def _draw_item_move_effects(self, surface: Surface):
        for effect in self.item_move_effects:
            surface.blit(effect.item, effect.current)

    def _draw_toast_effects(self, surface: Surface):
        index = 0

        for effect in sorted(self.toast_effects, key=lambda x: x.passed):
            if effect.toast:
                toast_rect = effect.toast.get_rect()
                toast_rect.x = self.assets.screen_width - toast_rect.width - self.padding
                toast_rect.y = (self.assets.screen_height - self.padding - effect.toast.get_height())  - (index * (effect.toast.get_height() + self.padding))
                surface.blit(effect.toast, toast_rect)

                index += 1

    def order(self) -> int:
        return 8

    def update(self, delta_time: float):

        # Process item move effects
        self._process_item_move_effects(delta_time)

        # Process toast effects
        self._process_toast_effects(delta_time)


    def draw(self, surface: Surface):
        self._draw_item_move_effects(surface)

        self._draw_toast_effects(surface)
