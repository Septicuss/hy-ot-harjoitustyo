from blueprint.blueprints import ItemReference

def item_ids_to_references(item_ids: list[str]) -> list[ItemReference]:
    """Returns a list of ids turned into a list of item references."""
    return [ItemReference(item_id) for item_id in item_ids]

def item_count_sum(items: list[ItemReference]) -> int:
    """Returns the sum of all item amounts."""
    return sum(item.amount for item in items)

def item_counts_match(first: list[ItemReference], second: list[ItemReference]) -> bool:
    """True if the amount of items in both arrays match by item id."""

    first_counts = get_item_counts(first)
    second_counts = get_item_counts(second)

    for item in first_counts.items():
        item_id = item[0]
        item_amount = item[1]

        if item_id not in second_counts:
            return False
        if second_counts[item_id] < item_amount:
            return False

    return True

def get_item_counts(items: list[ItemReference]) -> dict[str, int]:
    """Returns a dict mapping unique item ids to their total amount."""

    result = {}
    for item in items:
        if not item.id in result:
            result[item.id] = 0
        result[item.id] += item.amount
    return result
