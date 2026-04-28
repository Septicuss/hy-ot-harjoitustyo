from uuid import uuid4

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

class EffectUI(UIElement):

    def __init__(self, assets: GameAssets, state: GameState):
        super().__init__()

        self.assets = assets
        self.state = state

        self.item_move_effects: list[ItemMoveEffect] = []

    def submit_item_move(self, item_move: ItemMoveEffect):
        self.item_move_effects.append(item_move)

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

    def _draw_item_move_effects(self, surface: Surface):
        for effect in self.item_move_effects:
            surface.blit(effect.item, effect.current)

    def order(self) -> int:
        return 8

    def update(self, delta_time: float):

        # Process item move effects
        self._process_item_move_effects(delta_time)

    def draw(self, surface: Surface):
        self._draw_item_move_effects(surface)
