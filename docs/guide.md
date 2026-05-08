# Usage Guide

Download the [latest releases](https://github.com/Septicuss/hy-ot-harjoitustyo/releases/latest) source code.

## Configuration

This step is entirely optional. The game has some default configurations,
which include various gameplay items like recipes and machines. 
If you wish to edit these values (and as such, the game itself), you can modify `blueprints.json`
file in `src/blueprint/blueprint.json`.

There are several sub categories for blueprints in the file:
```json
{
  "constants": {...} // variables constants
  "sprites": {...} // mappings of bitmap sprites in an 8x8 grid
  "recipes": {...} // all items, their recipes and properties
  "machines": {...} // machine properties, namely defining which recipes they can craft
}
```

## Starting the application

1. Install dependencies, while in the root of the project:

```
poetry install
```

2. Start the application:

```
poetry run invoke start
```

## The game

### The UI

<img width="325" height="340" alt="image" src="https://github.com/user-attachments/assets/44a46bea-3ceb-4bda-9fa9-a8bcf92af9d7" />

1. **Your hotbar**. Use buttons Q + E to cycle the selected item. By holding and dragging the item in the middle, you can move the item.
2. **Machine tiles**. Machines accept items dragged over them and craft them into recipes. Once done, they can be picked up. As you can see most tiles are locked behind a coin amount.
3. **Orders**. This is the goal of the game. By dragging the required items here, you will gain coins, which can be used to unlock more machines.

### Gameplay

#### **1. Grow crops**. 

Crops can be planted on empty farmland by dragging the crop from hotbar onto farmland.
<img width="232" height="238" alt="image" src="https://github.com/user-attachments/assets/e6d9bdfd-b2a8-42ee-8ed0-da9757afbfd2" />


#### **2. Collect items**. 

Once a crop / item is done, it can be collected by clicking it:
<img width="261" height="204" alt="image" src="https://github.com/user-attachments/assets/5a69fc69-0544-4d2f-8227-e50713c98473" />


#### **3. Submit the required items for orders**. 

To get more coins to unlock more tiles, complete orders in the bottom left corner by dragging required items from your hotbar onto the order tile:
<img width="251" height="122" alt="image" src="https://github.com/user-attachments/assets/d39d225a-1dc7-4d13-988f-221f9285984b" />


#### **4. Take on more difficult orders**. 

As you unlock tiles with a bakery or juice press, you will start to get more complex orders. These are crafted by dragging multiple items onto a machine. You can view recipes and their progress by hovering over the machine:
<img width="301" height="216" alt="image" src="https://github.com/user-attachments/assets/3dc7bf46-cdda-47f5-9f5e-a6223dc9f566" />
(TIP: If you put a wrong ingredient into a machine, you can refund it by clicking the machine)


#### **5. Unlock all tiles**. 

The final goal is to unlock all tiles, but the game can theoretically be played forever to reach a high coin amount. You can decide when you've played enough :)
