import pygame

from game.game import Game


class GameAssets:
    def __init__(self):
        self.font = pygame.font.Font("src/ui/assets/font.ttf", 20)

class GameUI:

    def __init__(self, game: Game):
        self.screen = None
        self.assets = None
        self.game = game
        self.running = True

    def start(self):

        # Initialize pygame
        pygame.init()
        pygame.font.init()

        # Load assets
        self.assets = GameAssets()

        self.screen = pygame.display.set_mode((640, 640))

        # Start game logic & render loop
        self.__start_game_loop()

        # Clean up after quitting
        pygame.quit()

    def __start_game_loop(self):
        clock = pygame.time.Clock()

        while self.running:
            # Handle events
            self.__handle_events()

            # Render
            self.__render()

            pygame.display.flip()

        pass

    def __render(self):
        self.screen.fill((255, 255, 255))

        text = self.assets.font.render(str(self.game.farm.coins), True, (0, 0, 0))
        self.screen.blit(text, (300, 100))

    def __handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False