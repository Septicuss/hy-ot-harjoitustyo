class GameElementBlueprint:
    def __init__(self, id: str, name: str):
        self.id = id
        self.name = name

class ItemReference:
    def __init__(self, id: str, amount: int):
        self.id = id
        self.amount = amount

    def __repr__(self):
        return f"ItemReference({self.id}, {self.amount})"

    @classmethod
    def from_dict(cls, data):
        return cls(
            id = data["id"],
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
            default_items = [ItemReference.from_dict(item_data) for item_data in data["default_items"]]
        )

class CropBlueprint(GameElementBlueprint):
    def __init__(self, id: str, name: str, time: float):
        super().__init__(id, name)
        self.id = id
        self.name = name
        self.growth_time = time

    def __repr__(self):
        return f"CropBlueprint({self.id}, {self.name}, {self.growth_time})"

    @classmethod
    def from_dict(cls, data):
        return cls(
            id = data["id"],
            name = data["name"],
            time = data["time"]
        )


class RecipeBlueprint(GameElementBlueprint):
    def __init__(self, id: str, name: str, time: float, recipe: list[ItemReference]):
        super().__init__(id, name)
        self.id = id
        self.name = name
        self.time = time
        self.recipe = recipe

    def __repr__(self):
        return f"RecipeBlueprint({self.id}, {self.name}, {self.time}, {self.recipe})"

    @classmethod
    def from_dict(cls, data):
        return cls(
            id = data["id"],
            name = data["name"],
            time = data["time"],
            recipe = [ItemReference.from_dict(recipe_data) for recipe_data in data["recipe"]]
        )


class MachineBlueprint(GameElementBlueprint):
    def __init__(self, id: str, name: str, recipes: list[ItemReference]):
        super().__init__(id, name)
        self.id = id
        self.name = name
        self.recipes = recipes

    def __repr__(self):
        return f"MachineBlueprint({self.id}, {self.name})"

    @classmethod
    def from_dict(cls, data):
        return cls(
            id = data["id"],
            name = data["name"],
            recipes = [ItemReference.from_dict({"id": recipe_id}) for recipe_id in data["recipes"]]
        )