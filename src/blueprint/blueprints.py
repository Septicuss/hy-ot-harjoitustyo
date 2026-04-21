from dataclasses import dataclass
from enum import Enum


class RecipeType(Enum):
    """Represents the type of the recipe item"""
    ITEM = "item"
    """Default. Regular item with a single sprite"""
    CROP = "crop"
    """Crop item with additional crop sprites"""

class MachineRenderType(Enum):
    """Represents how a machine is rendered"""
    DEFAULT = "default"
    """Default. Machine is rendered having a regular and a busy state"""
    CROP = "crop"
    """Machine is rendered """

class GameElementBlueprint:
    def __init__(self, element_id: str, name: str):
        self.id = element_id
        self.name = name

class ItemReference:
    def __init__(self, reference_id: str, amount: int = 1):
        self.id = reference_id
        self.amount = amount

    def __repr__(self):
        return f"ItemReference({self.id}, {self.amount})"

    def __eq__(self, other):
        return self.id == other.id and self.amount == other.amount

    @classmethod
    def from_dict(cls, data):
        return cls(
            reference_id= data["id"],
            amount = data.get("amount", 1)
        )

class ConstantsBlueprint:
    def __init__(self, default_coins: int = 0, default_items: list[ItemReference]=None):
        self.default_coins = default_coins
        self.default_items: list[ItemReference] = [] if default_items is None else default_items

    @classmethod
    def from_dict(cls, data):
        return cls(
            default_coins = int(data["default_coins"]),
            default_items = [
                ItemReference.from_dict(item_data)
                for item_data in data["default_items"]
            ]
        )

@dataclass
class CropSprites:
    main: tuple[int, int]
    stage_1: tuple[int, int]
    stage_2: tuple[int, int]
    stage_3: tuple[int, int]

@dataclass
class MachineSprites:
    main: tuple[int, int]
    busy: tuple[int, int]

@dataclass
class RecipeSprites:
    main: tuple[int, int]

class SpritesBlueprint:
    def __init__(self, mappings: dict[str, tuple[int, int]]):
        self._mappings = mappings

    def get_crop_sprites(self, crop_id: str) -> CropSprites:
        return CropSprites(
            self._mappings.get(crop_id),
            self._mappings.get(f"{crop_id}_stage_1"),
            self._mappings.get(f"{crop_id}_stage_2"),
            self._mappings.get(f"{crop_id}_stage_3")
        )

    def get_machine_sprites(self, machine_id: str) -> MachineSprites:
        return MachineSprites(
            self._mappings.get(machine_id),
            self._mappings.get(f"{machine_id}_busy"),
        )

    def get_recipe_sprites(self,
                           recipe_id: str,
                           recipe_type: RecipeType) -> RecipeSprites | CropSprites:
        if recipe_type == RecipeType.CROP:
            return CropSprites(
                self._mappings.get(recipe_id),
                self._mappings.get(f"{recipe_id}_stage_1"),
                self._mappings.get(f"{recipe_id}_stage_2"),
                self._mappings.get(f"{recipe_id}_stage_3")
            )

        return RecipeSprites(
            self._mappings.get(recipe_id),
        )

    def get_sprite(self, item_id: str) -> tuple[int, int]:
        return self._mappings.get(item_id)

    @classmethod
    def from_dict(cls, data):
        mappings = {}

        for key in data.keys():
            array = data[key]
            mappings[key] = (array[0], array[1])

        return cls(
            mappings = mappings
        )

class RecipeBlueprint(GameElementBlueprint):
    def __init__(self,
                 recipe_id: str,
                 name: str,
                 time: float,
                 *,
                 recipe_type: RecipeType,
                 recipe: list[ItemReference]):
        super().__init__(recipe_id, name)
        self.id = recipe_id
        self.name = name
        self.time = time
        self.type = recipe_type
        self.recipe = recipe

    def __repr__(self):
        return f"RecipeBlueprint({self.id}, {self.name}, {self.time}, {self.recipe})"

    @classmethod
    def from_dict(cls, data):
        recipe_id = data["id"]
        default_recipe = [ItemReference(data["id"], 1)] # crafts one of self
        recipe = ([ItemReference.from_dict(recipe_entry) for recipe_entry in data["recipe"]]
                  if "recipe" in data else default_recipe) # use default recipe above if missing

        return cls(
            recipe_id= recipe_id,
            name = data["name"],
            time = data["time"],
            recipe_type=RecipeType(data.get("type", "item")),
            recipe = recipe
        )


class MachineBlueprint(GameElementBlueprint):
    def __init__(self,
                 machine_id: str,
                 name: str,
                 render: MachineRenderType,
                 recipes: list[ItemReference]):
        super().__init__(machine_id, name)
        self.id = machine_id
        self.name = name
        self.render: MachineRenderType = render
        self.recipes: list[ItemReference] = recipes

    def __repr__(self):
        return f"MachineBlueprint({self.id}, {self.name})"

    @classmethod
    def from_dict(cls, data):
        return cls(
            machine_id= data["id"],
            name = data["name"],
            render=MachineRenderType(data.get("render", "default")),
            recipes = [ItemReference.from_dict({"id": recipe_id}) for recipe_id in data["recipes"]]
        )
