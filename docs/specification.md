# Specification

## Purpose

The purpose of this application is to be a 'Hay Day' -like idle game.
Core gameplay revolves around planting and harvesting crops.
Excess crops can be used to craft products to complete randomized orders and gain coins.

## Game

### Gameplay

The game is meant to be as simple as possible. 
All interactions are either tapping or dragging elements with the cursor. 

Flow:
1) Player plants crops by dragging them onto farmland 
2) Crops take time to grow 
3) When grown, crops are harvested with a scythe 
4) Crops are put into buildings to make recipes (or used in orders)
5) Recipes are taken from buildings and put into orders
6) Completing orders gives coins 
7) Coins can be used to upgrade farmland grid size or buildings

### UI

A rough wireframe view of the game can be seen below 
(the final game will use stylized pixel art):

<img width="842" height="608" alt="image" src="https://github.com/user-attachments/assets/37409ae8-3272-4410-a245-c20b46e4e7da" />

**Hotbar**: Any item in the hotbar can be clicked and dragged onto other elements. 
For example dragging the scythe onto the farm will harvest the crops. 
Tapping on seeds or items opens up a small selection box with item icons and amounts, so
you can switch which item will be used.

**Farmland**: A grid of crops. Crops are planted by dragging them from the hotbar
onto a free grid slot. Once planted, a timer starts. When a timer is over 
(and crop has visually grown), it can be harvested with a draggable scythe from the hotbar.

**Buildings**: Each building has its own recipes for products. 
Tapping on a building shows a list of recipes. Dragging the appropriate items
onto the building will start a timer and once finished, tapping will
add the recipe result to the players items (bread for example).

**Orders**: A simple list, containing orders. Orders show which items they need.
Items can be dragged from hotbar onto orders to fulfill them. Once fulfilled,
orders will grant coins.

**HUD**: Displays the coins (and possibly a level) a player has. Tapping coins/level
three times will bring up a prompt to reset the farm progress.

## Further development

- Separate farm save files to allow for multiple farms without resets
- More content: buildings, crops, items (can be pretty easy to do with a data-driven system)
- More tools, for example a hose to water crops
