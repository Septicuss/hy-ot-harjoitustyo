from blueprint.game_blueprint import GameBlueprint
from save.save import GameSave
from state.game_state import GameState
from ui.game_ui import GameUI


def main():
    blueprint = GameBlueprint.load_from_file("src/blueprint/blueprint.json")
    save = GameSave()
    state = GameState(blueprint, save)

    # Example game state with a few items
    state.player.inventory.add_item("wheat", 5)
    state.player.inventory.add_item("berry_juice", 135)

    ui = GameUI(state)
    ui.start()

if __name__ == '__main__':
    main()
