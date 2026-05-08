# Specification

## Purpose


The purpose of this application is to be a 'Hay Day' -like idle game.
Core gameplay revolves around planting & harvesting crops and processing the crops to craft food.
Excess crops can be used to craft products to complete randomized orders and gain coins.

## 🛠️ Todo

**Current state**: Game is done.

* `[Blueprint]` Loading game blueprints from `blueprints.json` ✅
* `[State]` Machines and crafting ✅
* `[State]` Player & machine inventory ✅
* `[State]` Orders ✅
* `[State]` Automatic game saves using `save` module ✅
* `[State]` Tile system for machines & farmland ✅
* `[State]` Buying tiles ✅
* `[UI]` Loading UI assets from blueprints & bitmaps ✅
* `[UI]` Hotbar ✅
* `[UI]` Hotbar item selection (Q + E / left + right) ✅
* `[UI]` Dragging items from hotbar onto machines ✅
* `[UI]` Dragging items from hotbar onto orders ✅
* `[UI]` Machine UI (preparing items & showing recipes) ✅
* `[UI]` Order UI (rendering orders) ✅
* `[UI]` Rendering the tile system (machines) ✅
* `[UI]` Buying tiles (machines) ✅
* `[UI]` Tooltips ✅
* `[UI]` Notification Toasts ✅
* `[Save]` Saving and loading saves (`save` module) ✅


## Game

### Gameplay

The game is meant to be as simple as possible. 
All interactions are either tapping or dragging elements with the cursor. 

Flow:
1) Player plants crops by dragging them onto farmland 
2) Crops take time to grow 
3) When grown, crops are harvested by clicking on them
4) Crops are put into buildings to make recipes (or used in orders)
5) Recipes are taken from buildings and put into orders
6) Completing orders gives coins 
7) Coins can be used to buy more tiles

### UI

Final version of the UI can be seen here:
<img width="325" height="340" alt="image" src="https://github.com/user-attachments/assets/44a46bea-3ceb-4bda-9fa9-a8bcf92af9d7" />

1. **Your hotbar**. Use buttons Q + E to cycle the selected item. By holding and dragging the item in the middle, you can move the item.
2. **Machine tiles**. Machines accept items dragged over them and craft them into recipes. Once done, they can be picked up. As you can see most tiles are locked behind a coin amount.
3. **Orders**. This is the goal of the game. By dragging the required items here, you will gain coins, which can be used to unlock more machines.

See [The Guide](https://github.com/Septicuss/hy-ot-harjoitustyo/blob/main/docs/guide.md) to see more UI.

## Further development

- Separate farm save files to allow for multiple farms without resets
- More content: buildings, crops, items (can be pretty easy to do with a data-driven system)
- Farming statistics
