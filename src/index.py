from blueprint.game_blueprint import GameBlueprint
from state.game_state import GameState
from ui.game_ui import GameUI


def main():
    data = GameBlueprint.load_from_file("src/blueprint/blueprint.json")
    state = GameState(data)
    ui = GameUI(state)
    ui.start()

if __name__ == '__main__':
    main()