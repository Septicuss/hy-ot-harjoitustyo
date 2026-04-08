from blueprint.game_blueprint import GameBlueprint
from game.game import Game
from ui.game_ui import GameUI


def main():
    data = GameBlueprint.load_from_file("src/blueprint/blueprint.json")
    game = Game(data)
    ui = GameUI(game)
    ui.start()

if __name__ == '__main__':
    main()