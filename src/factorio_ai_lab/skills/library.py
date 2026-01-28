# ==============================================================================
# 🧠 SKILL LIBRARY - HIGH LEVEL MACROS
# Simplified for Autonomous Agent Reliability
# ==============================================================================

from factorio_ai_lab.fle_api import *
import time


def _resolve(name):
    """Smart resolver for strings to FLE objects."""
    n = str(name).lower()
    if "stone" in n and "furnace" not in n:
        return Resource.Stone
    if "coal" in n:
        return Resource.Coal
    if "iron" in n and "ore" in n:
        return Resource.IronOre
    if "copper" in n:
        return Resource.CopperOre
    if "wood" in n:
        return Resource.Wood

    if "furnace" in n:
        return Prototype.StoneFurnace
    if "drill" in n:
        return Prototype.BurnerMiningDrill
    if "gear" in n:
        return Prototype.IronGearWheel
    if "plate" in n:
        return Prototype.IronPlate

    return name


def gather(resource_name, quantity=1):
    """Gathers a raw resource. Usage: gather('stone', 5)"""
    res_type = _resolve(resource_name)
    print(f"🌲 Action: Gathering {quantity} {res_type}...")

    # 1. Find
    pos = nearest(res_type)
    if not pos:
        print(f"❌ Error: Could not find {res_type}")
        return False

    # 2. Move
    move_to(pos)

    # 3. Harvest
    # Loop for safety in case of partial harvest
    harvested = 0
    for _ in range(3):  # Retry loop
        qty = harvest_resource(pos, quantity=quantity)
        harvested += qty
        if harvested >= quantity:
            break

    print(f"✅ Harvested {harvested}/{quantity}")
    return True


def craft(item_name, quantity=1):
    """Crafts an item. Usage: craft('furnace')"""
    proto = _resolve(item_name)
    print(f"🔨 Action: Crafting {quantity} {proto}...")

    # Check inventory? FLE api handles it and returns 0 if fail.
    count = craft_item(proto, quantity=quantity)
    if count > 0:
        print(f"✅ Crafted {count}")
        return True
    else:
        print("❌ Craft failed (missing resources?)")
        return False


def place(item_name):
    """Places a structure nearby. Usage: place('furnace')"""
    proto = _resolve(item_name)
    print(f"🏗️ Action: Placing {proto}...")

    # Check if we have it
    inv = inspect_inventory()
    if inv.get(proto, 0) == 0:
        print(f"⚠️ Do not have {proto}, trying to craft one...")
        craft(item_name, 1)

    # Simple placement heuristic
    # We use a fixed offset relative to origin (since we don't track player perfectly)
    # But for FLE, we must be CLOSE to the target position.
    target_pos = Position(x=5, y=5)

    # CRITICAL: Move to valid build distance
    move_to(target_pos)

    ent = place_entity(proto, position=target_pos, direction=Direction.NORTH)
    if ent:
        print(f"✅ Placed at {target_pos}")
        return ent
    else:
        # Retry slightly offset if collision
        target_pos = Position(x=8, y=8)
        move_to(target_pos)
        ent = place_entity(proto, position=target_pos, direction=Direction.NORTH)
        if ent:
            print(f"✅ Placed at {target_pos} (retry)")
            return ent
        print("❌ Placement failed")
        return None


def smelt(ore_name, product_name, count=1):
    """Smelts resources. Needs a furnace. Usage: smelt('iron_ore', 'iron_plate', 5)"""
    ore = _resolve(ore_name)
    product = _resolve(product_name)

    print(f"🔥 Action: Smelting {count} {ore} -> {product}...")

    # 1. Find Furnace
    furnaces = [e for e in get_entities() if "furnace" in e.name]
    if not furnaces:
        print("   No furnace found. Building one...")
        gather("stone", 5)
        craft("furnace")
        furnace = place("furnace")
        if not furnace:
            return False
    else:
        furnace = furnaces[0]

    move_to(furnace.position)

    # 2. Fuel (Coal)
    # Check if we have coal
    inv = inspect_inventory()
    if inv.get(Resource.Coal, 0) < count:
        print("   Need coal...")
        gather("coal", count)
        move_to(furnace.position)

    insert_item(Prototype.Coal, furnace, quantity=count)

    # 3. Ore
    inv = inspect_inventory()
    if inv.get(ore, 0) < count:
        print(f"   Need {ore}...")
        gather(ore_name, count)
        move_to(furnace.position)

    insert_item(ore, furnace, quantity=count)

    # 4. Wait
    print("   Smelting...")
    time.sleep(count * 1.0)

    # 5. Retrieve
    extract_item(product, furnace, quantity=count)
    print("✅ Smelt complete.")
    return True


# ==============================================================================
