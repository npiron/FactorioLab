"""
Production Line Agent - First Iron Plate Production

This agent builds a complete production line:
1. Find iron ore patch
2. Place burner mining drills on iron
3. Place stone furnaces
4. Insert fuel (coal) into drills and furnaces
5. Set up basic iron plate production

User will see a real production line being built!
"""

PRODUCTION_ACTIONS = [
    # Step 0-2: Get resources and position
    "pos = inspect_inventory().position",
    "iron_patch = get_resource_patch(Resource.IronOre, pos)",
    "coal_patch = get_resource_patch(Resource.Coal, pos)",
    # Step 3-5: Harvest initial resources manually
    "harvest_resource(iron_patch.bounding_box.center, quantity=50)",
    "harvest_resource(coal_patch.bounding_box.center, quantity=50)",
    "sleep(60)",
    # Step 6-8: Craft initial buildings
    "craft_item(Prototype.BurnerMiningDrill, quantity=3)",
    "craft_item(Prototype.StoneFurnace, quantity=3)",
    "sleep(60)",
    # Step 9-11: Place 3 drills on iron patch
    "drill1_pos = iron_patch.bounding_box.left_top\nplace_entity(Prototype.BurnerMiningDrill, position=drill1_pos, direction=Direction.DOWN)",
    "drill2_pos = Position(x=drill1_pos.x + 3, y=drill1_pos.y)\nplace_entity(Prototype.BurnerMiningDrill, position=drill2_pos, direction=Direction.DOWN)",
    "drill3_pos = Position(x=drill2_pos.x + 3, y=drill2_pos.y)\nplace_entity(Prototype.BurnerMiningDrill, position=drill3_pos, direction=Direction.DOWN)",
    # Step 12: Fuel the drills
    "insert_item(Prototype.BurnerMiningDrill, drill1_pos, Prototype.Coal, quantity=5)\ninsert_item(Prototype.BurnerMiningDrill, drill2_pos, Prototype.Coal, quantity=5)\ninsert_item(Prototype.BurnerMiningDrill, drill3_pos, Prototype.Coal, quantity=5)",
    "sleep(120)",  # Watch drills start mining
    # Step 13-15: Place 3 furnaces next to drills
    "furnace1_pos = Position(x=drill1_pos.x, y=drill1_pos.y + 3)\nplace_entity(Prototype.StoneFurnace, position=furnace1_pos)",
    "furnace2_pos = Position(x=drill2_pos.x, y=drill2_pos.y + 3)\nplace_entity(Prototype.StoneFurnace, position=furnace2_pos)",
    "furnace3_pos = Position(x=drill3_pos.x, y=drill3_pos.y + 3)\nplace_entity(Prototype.StoneFurnace, position=furnace3_pos)",
    # Step 16: Fuel the furnaces
    "insert_item(Prototype.StoneFurnace, furnace1_pos, Prototype.Coal, quantity=10)\ninsert_item(Prototype.StoneFurnace, furnace2_pos, Prototype.Coal, quantity=10)\ninsert_item(Prototype.StoneFurnace, furnace3_pos, Prototype.Coal, quantity=10)",
    # Step 17-19: Add ore to furnaces manually
    "insert_item(Prototype.StoneFurnace, furnace1_pos, Prototype.IronOre, quantity=10)\ninsert_item(Prototype.StoneFurnace, furnace2_pos, Prototype.IronOre, quantity=10)\ninsert_item(Prototype.StoneFurnace, furnace3_pos, Prototype.IronOre, quantity=10)",
    "sleep(180)",  # Watch furnaces smelt iron
    # Step 20: Check production
    "print('Production line complete! Iron plates being produced.')\nscore()",
]


def get_production_code(step: int) -> str:
    """Get code for production line building."""
    if step < len(PRODUCTION_ACTIONS):
        return PRODUCTION_ACTIONS[step]
    else:
        # Monitor production
        return "score()"
