from __future__ import annotations

try:
    from fle.api import (
        Prototype,
        Resource,
        Position,
        Direction,
        nearest,
        move_to,
        harvest_resource,
        craft_item,
        place_entity,
        insert_item,
        extract_item,
        inspect_inventory,
        get_entities,
        sleep,
    )
except ImportError:
    pass  # In FLE REPL, these symbols are already in globals()


def smart_harvest(resource_type: Resource, quantity: int = 1) -> int:
    """Finds nearest resource, moves to it, and harvests it."""
    pos = nearest(resource_type)
    if not pos:
        print(f"❌ Skill Error: No {resource_type} found nearby.")
        return 0
    move_to(pos)
    amount = harvest_resource(pos, quantity=quantity)
    print(f"✅ Skill: Harvested {amount} of {resource_type} at {pos}")
    return amount


def smart_craft(item_type: Prototype, quantity: int = 1) -> int:
    """Crafts an item, auto-harvesting raw materials if possible (basic only)."""
    # Note: Full recursive crafting is complex, we assume raw materials are mostly there
    # or let the agent handle logic. This is a wrapper.
    amount = craft_item(item_type, quantity=quantity)
    if amount < quantity:
        print(f"⚠️ Skill: Requested {quantity} {item_type}, but only crafted {amount}.")
    else:
        print(f"✅ Skill: Crafted {amount} {item_type}")
    return amount


def extract_and_store(source_entity, chest_entity, item_type: Prototype, quantity: int = 50):
    """Extracts items from a machine and puts them in a chest."""
    if not source_entity or not chest_entity:
        return

    move_to(source_entity.position)
    extracted = extract_item(item_type, source_entity, quantity=quantity)

    if extracted > 0:
        move_to(chest_entity.position)
        insert_item(item_type, chest_entity, quantity=extracted)
        print(f"✅ Skill: Transferred {extracted} {item_type} from {source_entity.name} to chest.")
    else:
        print(f"ℹ️ Skill: Nothing to extract ({item_type}) from {source_entity.name}")


def auto_smelt(
    furnace_entity, ore_type: Prototype, fuel_type: Prototype = Prototype.Coal, amount: int = 10
):
    """Inserts ore and fuel into a furnace."""
    if not furnace_entity:
        return

    # Fuel
    move_to(furnace_entity.position)
    inv = inspect_inventory()
    fuel_has = inv.get(fuel_type, 0)
    if fuel_has > 0:
        insert_item(fuel_type, furnace_entity, quantity=min(fuel_has, 5))  # Keep some fuel

    # Ore
    ore_has = inv.get(ore_type, 0)
    to_insert = min(ore_has, amount)
    if to_insert > 0:
        insert_item(ore_type, furnace_entity, quantity=to_insert)
        print(f"✅ Skill: Smelting {to_insert} {ore_type} in {furnace_entity.name}")
