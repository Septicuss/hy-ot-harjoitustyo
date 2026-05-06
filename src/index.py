from blueprint.game_blueprint import GameBlueprint
from save.save import GameSaves
from state.game_state import GameState
from ui.game_ui import GameUI


def main():
    saves = GameSaves("src/save")
    saves.load_saves()

    blueprint = GameBlueprint.load_from_file("src/blueprint/blueprint.json")
    state = GameState(blueprint, saves)

    ui = GameUI(state)
    ui.start()

if __name__ == '__main__':
    main()
