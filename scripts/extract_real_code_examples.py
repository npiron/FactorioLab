"""
Extract REAL code examples from FLE agents and production code
This creates high-quality training data based on actual working code
"""

import json
from pathlib import Path


def create_extended_examples():
    """Create comprehensive code examples based on real FLE patterns"""
    examples = []

    # ============================================
    # HARVESTING EXAMPLES (Extended)
    # ============================================
    examples.extend(
        [
            {
                "instruction": "Generate Python code for Factorio",
                "input": "Find and harvest iron ore",
                "output": "iron_pos = nearest(Resource.IronOre)\nprint(f'Found iron at {iron_pos}')\nmove_to(iron_pos)\nharvested_iron = harvest_resource(iron_pos, quantity=50)\nprint(f'Harvested {harvested_iron} iron ore')",
            },
            {
                "instruction": "Generate Python code for Factorio",
                "input": "Find and harvest coal",
                "output": "coal_pos = nearest(Resource.Coal)\nprint(f'Found coal at {coal_pos}')\nmove_to(coal_pos)\nharvested_coal = harvest_resource(coal_pos, quantity=50)\nprint(f'Harvested {harvested_coal} coal')",
            },
            {
                "instruction": "Generate Python code for Factorio",
                "input": "Find and harvest wood from trees",
                "output": "wood_pos = nearest(Resource.Wood)\nprint(f'Wood at: {wood_pos}')\nmove_to(wood_pos)\nwood = harvest_resource(wood_pos, 20)\nprint(f'Harvested {wood} wood')",
            },
            {
                "instruction": "Generate Python code for Factorio",
                "input": "Harvest stone",
                "output": "stone_pos = nearest(Resource.Stone)\nmove_to(stone_pos)\nstone = harvest_resource(stone_pos, quantity=50)\nprint(f'Harvested {stone} stone')",
            },
            {
                "instruction": "Generate Python code for Factorio",
                "input": "Harvest copper ore",
                "output": "copper_pos = nearest(Resource.CopperOre)\nmove_to(copper_pos)\ncopper = harvest_resource(copper_pos, quantity=50)\nprint(f'Harvested {copper} copper ore')",
            },
        ]
    )

    # ============================================
    # CRAFTING EXAMPLES (Extended)
    # ============================================
    examples.extend(
        [
            {
                "instruction": "Generate Python code for Factorio",
                "input": "Craft burner mining drills",
                "output": "crafted_drills = craft_item(Prototype.BurnerMiningDrill, quantity=2)\nprint(f'Crafted {crafted_drills} burner mining drills')",
            },
            {
                "instruction": "Generate Python code for Factorio",
                "input": "Craft stone furnaces",
                "output": "crafted_furnaces = craft_item(Prototype.StoneFurnace, quantity=2)\nprint(f'Crafted {crafted_furnaces} stone furnaces')",
            },
            {
                "instruction": "Generate Python code for Factorio",
                "input": "Craft iron gear wheels",
                "output": "gears = craft_item(Prototype.IronGearWheel, quantity=10)\nprint(f'Crafted {gears} iron gear wheels')",
            },
            {
                "instruction": "Generate Python code for Factorio",
                "input": "Craft iron plates",
                "output": "plates = craft_item(Prototype.IronPlate, quantity=20)\nprint(f'Crafted {plates} iron plates')",
            },
            {
                "instruction": "Generate Python code for Factorio",
                "input": "Craft copper plates",
                "output": "copper_plates = craft_item(Prototype.CopperPlate, quantity=20)\nprint(f'Crafted {copper_plates} copper plates')",
            },
            {
                "instruction": "Generate Python code for Factorio",
                "input": "Craft copper wire",
                "output": "wire = craft_item(Prototype.CopperWire, quantity=20)\nprint(f'Crafted {wire} copper wire')",
            },
            {
                "instruction": "Generate Python code for Factorio",
                "input": "Check inventory before crafting",
                "output": "inv = inspect_inventory()\nprint(f'Inventory: {inv}')\nif inv.get('stone', 0) >= 5:\n    craft_item(Prototype.StoneFurnace, 1)\nelse:\n    print('Need more stone!')",
            },
        ]
    )

    # ============================================
    # BUILDING & PLACEMENT (Extended)
    # ============================================
    examples.extend(
        [
            {
                "instruction": "Generate Python code for Factorio",
                "input": "Place a burner mining drill on iron ore",
                "output": "drill1 = place_entity(Prototype.BurnerMiningDrill, position=nearest(Resource.IronOre), direction=Direction.DOWN)\nprint(f'Placed drill 1 at {drill1.position}')",
            },
            {
                "instruction": "Generate Python code for Factorio",
                "input": "Place stone furnace",
                "output": "craft_item(Prototype.StoneFurnace, 1)\nfurnace = place_entity(Prototype.StoneFurnace, position=Position(x=0, y=0), direction=Direction.UP)\nprint(f'Placed furnace at {furnace.position}')",
            },
            {
                "instruction": "Generate Python code for Factorio",
                "input": "Place assembling machine",
                "output": "craft_item(Prototype.AssemblingMachine1, 1)\nasm = place_entity(Prototype.AssemblingMachine1, position=Position(x=5, y=5), direction=Direction.UP)\nprint(f'Placed assembling machine at {asm.position}')",
            },
            {
                "instruction": "Generate Python code for Factorio",
                "input": "Place a wooden chest",
                "output": "craft_item(Prototype.WoodenChest, 1)\nchest = place_entity(Prototype.WoodenChest, position=Position(x=10, y=10))\nprint(f'Placed chest at {chest.position}')",
            },
        ]
    )

    # ============================================
    # INSERTING & FUELING (Extended)
    # ============================================
    examples.extend(
        [
            {
                "instruction": "Generate Python code for Factorio",
                "input": "Fuel a burner mining drill with coal",
                "output": "drill1 = insert_item(Prototype.Coal, drill1, quantity=10)\nprint(f'Fueled drill 1 - status: {drill1.status}')",
            },
            {
                "instruction": "Generate Python code for Factorio",
                "input": "Insert coal and iron ore into furnace",
                "output": "furnace = insert_item(Prototype.Coal, furnace, quantity=10)\nfurnace = insert_item(Prototype.IronOre, furnace, quantity=20)\nprint(f'Fueled and loaded furnace')",
            },
            {
                "instruction": "Generate Python code for Factorio",
                "input": "Insert items into entity",
                "output": "entity = insert_item(Prototype.Coal, entity, quantity=5)\nprint(f'Inserted 5 coal into entity')",
            },
        ]
    )

    # ============================================
    # MOVEMENT & INSPECTION (Extended)
    # ============================================
    examples.extend(
        [
            {
                "instruction": "Generate Python code for Factorio",
                "input": "Move to specific position",
                "output": "target = Position(x=10, y=10)\nmove_to(target)\nprint(f'Moved to {target}')",
            },
            {
                "instruction": "Generate Python code for Factorio",
                "input": "Move to nearest iron ore",
                "output": "iron_pos = nearest(Resource.IronOre)\nmove_to(iron_pos)\nprint(f'Moved to iron at {iron_pos}')",
            },
            {
                "instruction": "Generate Python code for Factorio",
                "input": "Check current inventory",
                "output": "inv = inspect_inventory()\nprint(f'Inventory: {inv}')",
            },
            {
                "instruction": "Generate Python code for Factorio",
                "input": "Check entity status",
                "output": "print(f'Drill status: {drill.status}')\nprint(f'Position: {drill.position}')",
            },
        ]
    )

    # ============================================
    # COMPLEX PRODUCTION SETUPS (NEW!)
    # ============================================
    examples.extend(
        [
            {
                "instruction": "Generate Python code for Factorio",
                "input": "Set up iron mining and smelting",
                "output": "# Harvest resources\niron_pos = nearest(Resource.IronOre)\nmove_to(iron_pos)\nharvest_resource(iron_pos, quantity=50)\ncoal_pos = nearest(Resource.Coal)\nmove_to(coal_pos)\nharvest_resource(coal_pos, quantity=50)\n\n# Craft buildings\ncraft_item(Prototype.BurnerMiningDrill, quantity=1)\ncraft_item(Prototype.StoneFurnace, quantity=1)\n\n# Place and fuel drill\ndrill = place_entity(Prototype.BurnerMiningDrill, position=nearest(Resource.IronOre), direction=Direction.DOWN)\ndrill = insert_item(Prototype.Coal, drill, quantity=10)\n\n# Place and load furnace\nfurnace_pos = Position(x=drill.position.x, y=drill.position.y + 3)\nfurnace = place_entity(Prototype.StoneFurnace, position=furnace_pos, direction=Direction.UP)\nfurnace = insert_item(Prototype.Coal, furnace, quantity=10)\nfurnace = insert_item(Prototype.IronOre, furnace, quantity=20)\nprint('Iron production setup complete!')",
            },
            {
                "instruction": "Generate Python code for Factorio",
                "input": "Place two drills with offset",
                "output": "drill1 = place_entity(Prototype.BurnerMiningDrill, position=nearest(Resource.IronOre), direction=Direction.DOWN)\nprint(f'Placed drill 1 at {drill1.position}')\n\ndrill2_pos = Position(x=drill1.position.x + 3, y=drill1.position.y)\ndrill2 = place_entity(Prototype.BurnerMiningDrill, position=drill2_pos, direction=Direction.DOWN)\nprint(f'Placed drill 2 at {drill2.position}')",
            },
            {
                "instruction": "Generate Python code for Factorio",
                "input": "Verify production line status",
                "output": "print(f'Drill 1 status: {drill1.status}')\nprint(f'Drill 2 status: {drill2.status}')\nprint(f'Furnace 1 status: {furnace1.status}')\nprint(f'Furnace 2 status: {furnace2.status}')\nprint('=== PRODUCTION LINE STATUS ===')",
            },
        ]
    )

    # ============================================
    # AUTOMATION PATTERNS (NEW!)
    # ============================================
    examples.extend(
        [
            {
                "instruction": "Generate Python code for Factorio",
                "input": "Wait and observe smelting",
                "output": "print('Waiting for smelting...')\nsleep(60)\nprint('Smelting complete!')",
            },
            {
                "instruction": "Generate Python code for Factorio",
                "input": "Calculate production score",
                "output": "current_score = score()\nprint(f'Current score: {current_score}')",
            },
            {
                "instruction": "Generate Python code for Factorio",
                "input": "Build coal self-sustaining drill",
                "output": "# Find coal patch\ncoal_patch = nearest(Resource.Coal)\nmove_to(coal_patch)\n\n# Harvest initial coal\nharvest_resource(coal_patch, quantity=20)\n\n# Craft drill\ncraft_item(Prototype.BurnerMiningDrill, quantity=1)\n\n# Place drill on coal\ndrill = place_entity(Prototype.BurnerMiningDrill, position=coal_patch, direction=Direction.DOWN)\n\n# Fuel with initial coal\ndrill = insert_item(Prototype.Coal, drill, quantity=5)\nprint('Self-sustaining coal drill active!')",
            },
        ]
    )

    return examples


if __name__ == "__main__":
    # Create extended examples
    examples = create_extended_examples()

    # Save to file
    output_file = Path("training_data/factorio_code_extended.jsonl")
    with open(output_file, "w") as f:
        for ex in examples:
            f.write(json.dumps(ex, ensure_ascii=False) + "\n")

    print(f"✅ Created {len(examples)} extended code examples!")
    print(f"📁 Saved to: {output_file}")

    # Show statistics
    categories = {
        "Harvesting": sum(
            1
            for ex in examples
            if "harvest" in ex["input"].lower() or "mine" in ex["input"].lower()
        ),
        "Crafting": sum(1 for ex in examples if "craft" in ex["input"].lower()),
        "Building": sum(
            1 for ex in examples if "place" in ex["input"].lower() or "build" in ex["input"].lower()
        ),
        "Fueling": sum(
            1 for ex in examples if "fuel" in ex["input"].lower() or "insert" in ex["input"].lower()
        ),
        "Movement": sum(1 for ex in examples if "move" in ex["input"].lower()),
        "Inspection": sum(
            1
            for ex in examples
            if "check" in ex["input"].lower()
            or "status" in ex["input"].lower()
            or "inventory" in ex["input"].lower()
        ),
        "Complex": sum(
            1
            for ex in examples
            if "setup" in ex["input"].lower() or "production" in ex["input"].lower()
        ),
    }

    print("\n📊 Categories:")
    for category, count in categories.items():
        print(f"   {category}: {count} examples")

    print("\n📝 Example:")
    print(json.dumps(examples[0], indent=2, ensure_ascii=False))

    print("\n🎯 Next steps:")
    print("   1. Run: python scripts/generate_code_variations.py")
    print("   2. Run: python scripts/convert_code_to_mlx.py")
    print("   3. Fine-tune with improved dataset!")
