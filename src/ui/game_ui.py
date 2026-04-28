import pygame
from pygame.event import Event

from state.game_state import GameState
from ui.assets import GameAssets
from ui.base_elements import UIElement, MachineUI, HotbarUI
from ui.elements.tooltip import TooltipUI


class GameUI:

    SCREEN_SIZE = (640, 640)
    BG_COLOR = (255, 252, 224)

    def __init__(self, state: GameState):
        # Initialize pygame
        pygame.init()
        pygame.font.init()

        self.assets = None
        self.screen = None
        self.state = state
        self.running = True

        self.grid = None
        self.elements: list[UIElement] = []

    def start(self):
        # Create screen
        flags = pygame.SCALED
        self.screen = pygame.display.set_mode(
            size=self.SCREEN_SIZE,
            flags=flags
        )

        self.assets = GameAssets(self.SCREEN_SIZE)

        # Load grid of machines
        self.assets.tiles = {
            tile: MachineUI(self.assets, self.state, machine, tile) for tile, machine in self.state.tiles.items()
        }

        # Load ui elements
        self.elements: list[UIElement] = [
            TooltipUI(self.assets, self.state),
            HotbarUI(self.assets, self.state),
            *self.assets.tiles.values(),
        ]

        # Start state logic & render loop
        self.__start_game_loop()

        # Clean up after quitting
        pygame.quit()

    def set_grid_item(self, index: int, item: UIElement):
        existing = self.grid.get(index)

        if existing:
            for element in self.elements:
                if element.id == existing.id:
                    self.elements.remove(element)

        self.elements.append(item)

    def __start_game_loop(self):
        clock = pygame.time.Clock()

        while self.running:
            delta_time = clock.tick(60) / 1000

            # Handle events
            self.__handle_events()

            # Update state
            self.state.update(delta_time)

            # Update UI elements
            self.__update(delta_time)

            # Render screen
            self.__draw()

            pygame.display.flip()

        pass

    def __update(self, delta_time: float):
        for element in self.elements:
            element.update(delta_time)

    def __draw(self):
        self.screen.fill(self.BG_COLOR)

        # Draw elements based on order
        for element in sorted(self.elements, key=lambda e: e.order()):
            element.draw(self.screen)

    def __handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                continue

            self.__handle_event(event)

    def __handle_event(self, event: Event):
        for element in self.elements:
            element.handle_event(event)