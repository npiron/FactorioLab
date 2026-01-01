"""
Production Line Agent - OFFICIAL FLE PATTERNS

Based on real working examples from FLE documentation.
Uses nearest() for resource finding and Entity object persistence.
"""

PRODUCTION_ACTIONS = [
    # Step 0-1: Find and harvest iron using nearest()
    """
iron_pos = nearest(Resource.IronOre)
print(f'Found iron at {iron_pos}')
move_to(iron_pos)
harvested_iron = harvest_resource(iron_pos, quantity=50)
print(f'Harvested {harvested_iron} iron ore')
""",
    # Step 2-3: Find and harvest coal
    """
coal_pos = nearest(Resource.Coal)
print(f'Found coal at {coal_pos}')
move_to(coal_pos)
harvested_coal = harvest_resource(coal_pos, quantity=50)
print(f'Harvested {harvested_coal} coal')
""",
    # Step 4-5: Craft buildings
    """
crafted_drills = craft_item(Prototype.BurnerMiningDrill, quantity=2)
print(f'Crafted {crafted_drills} burner mining drills')
crafted_furnaces = craft_item(Prototype.StoneFurnace, quantity=2)
print(f'Crafted {crafted_furnaces} stone furnaces')
""",
    # Step 6: Place first drill on iron
    """
drill1 = place_entity(Prototype.BurnerMiningDrill, position=nearest(Resource.IronOre), direction=Direction.DOWN)
print(f'Placed drill 1 at {drill1.position}')
""",
    # Step 7: Fuel drill 1
    """
drill1 = insert_item(Prototype.Coal, drill1, quantity=10)
print(f'Fueled drill 1 - status: {drill1.status}')
""",
    # Step 8: Place second drill
    """
drill2_pos = Position(x=drill1.position.x + 3, y=drill1.position.y)
drill2 = place_entity(Prototype.BurnerMiningDrill, position=drill2_pos, direction=Direction.DOWN)
print(f'Placed drill 2 at {drill2.position}')
""",
    # Step 9: Fuel drill 2
    """
drill2 = insert_item(Prototype.Coal, drill2, quantity=10)
print(f'Fueled drill 2')
sleep(60)  # Watch drills start mining
""",
    # Step 10: Place furnace near drill 1
    """
furnace1_pos = Position(x=drill1.position.x, y=drill1.position.y + 3)
furnace1 = place_entity(Prototype.StoneFurnace, position=furnace1_pos, direction=Direction.UP)
print(f'Placed furnace 1 at {furnace1.position}')
""",
    # Step 11: Fuel and feed furnace 1
    """
furnace1 = insert_item(Prototype.Coal, furnace1, quantity=10)
furnace1 = insert_item(Prototype.IronOre, furnace1, quantity=20)
print(f'Fueled and loaded furnace 1')
""",
    # Step 12: Place furnace near drill 2
    """
furnace2_pos = Position(x=drill2.position.x, y=drill2.position.y + 3)
furnace2 = place_entity(Prototype.StoneFurnace, position=furnace2_pos, direction=Direction.UP)
print(f'Placed furnace 2 at {furnace2.position}')
""",
    # Step 13: Fuel and feed furnace 2
    """
furnace2 = insert_item(Prototype.Coal, furnace2, quantity=10)
furnace2 = insert_item(Prototype.IronOre, furnace2, quantity=20)
print(f'Fueled and loaded furnace 2')
sleep(120)  # Watch smelting
""",
    # Step 14: Verify production
    """
print(f'Drill 1 status: {drill1.status}')
print(f'Drill 2 status: {drill2.status}')
print(f'Furnace 1 status: {furnace1.status}')
print(f'Furnace 2 status: {furnace2.status}')
print('=== PRODUCTION LINE COMPLETE ===')
print('2 drills mining iron + 2 furnaces smelting = Iron plates!')
score()
""",
]


def get_production_code(step: int) -> str:
    """Get code for production line building."""
    if step < len(PRODUCTION_ACTIONS):
        return PRODUCTION_ACTIONS[step]
    else:
        return "score()"
