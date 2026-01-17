"""
Extract and save building blocks from knowledge base
Analyzes successful patterns and creates reusable building blocks
"""

import json


def extract_building_blocks():
    """Extract unique successful patterns as building blocks"""

    # Load knowledge base
    with open("knowledge_base.json") as f:
        kb = json.load(f)

    successful = kb["successful_patterns"]

    print(f"📊 Analyzing {len(successful)} successful patterns...")

    # Group by action type
    blocks = {}

    for pattern_data in successful:
        pattern = pattern_data["pattern"]

        # Skip if too short
        if len(pattern) < 20:
            continue

        # Detect pattern type
        if "harvest_resource" in pattern and "IronOre" in pattern:
            key = "harvest_iron"
            name = "Harvest Iron Ore"
            code = """iron_pos = nearest(Resource.IronOre)
move_to(iron_pos)
harvested = harvest_resource(iron_pos, quantity=50)
print(f'Harvested {harvested} iron ore')"""

        elif "harvest_resource" in pattern and "Stone" in pattern:
            key = "harvest_stone"
            name = "Harvest Stone"
            code = """stone_pos = nearest(Resource.Stone)
move_to(stone_pos)
harvested = harvest_resource(stone_pos, quantity=50)
print(f'Harvested {harvested} stone')"""

        elif "craft_item" in pattern and "StoneFurnace" in pattern:
            key = "craft_furnace"
            name = "Craft Stone Furnace"
            code = """crafted = craft_item(Prototype.StoneFurnace, quantity=1)
print(f'Crafted {crafted} stone furnaces')"""

        elif "inspect_inventory" in pattern:
            key = "check_inventory"
            name = "Check Inventory"
            code = """inventory = inspect_inventory()
print(f'Inventory: {inventory}')"""

        else:
            continue

        blocks[key] = {"name": key, "description": name, "code": code}

    # Add to knowledge base
    kb["building_blocks"] = []
    for block in blocks.values():
        kb["building_blocks"].append(
            {
                **block,
                "success_rate": 1.0,
                "created_at": "2026-01-11T21:21:30",
                "times_used": 0,
                "times_succeeded": 0,
            }
        )

    # Save
    with open("knowledge_base.json", "w") as f:
        json.dump(kb, f, indent=2)

    print(f"\n✅ Created {len(blocks)} building blocks:")
    for block in blocks.values():
        print(f"   📦 {block['name']}: {block['description']}")

    print("\n💾 Saved to: knowledge_base.json")

    return blocks


if __name__ == "__main__":
    blocks = extract_building_blocks()

    print("\n" + "=" * 60)
    print("BUILDING BLOCKS CREATED")
    print("=" * 60)

    for block in blocks.values():
        print(f"\n📦 {block['name'].upper()}")
        print(f"   Description: {block['description']}")
        print("   Code:")
        for line in block["code"].split("\n"):
            print(f"      {line}")
