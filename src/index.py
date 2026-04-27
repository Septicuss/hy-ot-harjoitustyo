from blueprint.game_blueprint import GameBlueprint
from save.save import GameSave
from state.game_state import GameState
from ui.game_ui import GameUI


def main():
    blueprint = GameBlueprint.load_from_file("src/blueprint/blueprint.json")
    save = GameSave()
    state = GameState(blueprint, save)

    ui = GameUI(state)
    ui.start()

if __name__ == '__main__':
    main()
