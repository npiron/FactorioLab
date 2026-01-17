"""
Create manual Python code examples for Factorio AI fine-tuning
These are high-quality, hand-crafted examples
"""

import json
from pathlib import Path


def create_code_examples():
    """Create manual code examples"""
    examples = []

    # Harvesting examples
    examples.extend(
        [
            {
                "instruction": "Generate Python code for Factorio",
                "input": "Harvest iron ore",
                "output": "game.harvest_resource(Prototype.IronOre, quantity=5)",
            },
            {
                "instruction": "Generate Python code for Factorio",
                "input": "Harvest 10 coal",
                "output": "game.harvest_resource(Prototype.Coal, quantity=10)",
            },
            {
                "instruction": "Generate Python code for Factorio",
                "input": "Mine copper ore patches",
                "output": "copper_patches = game.get_resource_patch(Prototype.CopperOre)\nfor patch in copper_patches:\n    game.harvest_resource(Prototype.CopperOre, position=patch)",
            },
        ]
    )

    # Crafting examples
    examples.extend(
        [
            {
                "instruction": "Generate Python code for Factorio",
                "input": "Craft iron plates",
                "output": "game.craft_item(Prototype.IronPlate, quantity=10)",
            },
            {
                "instruction": "Generate Python code for Factorio",
                "input": "Craft iron gear wheels from iron plates",
                "output": "game.craft_item(Prototype.IronGearWheel, quantity=5)",
            },
            {
                "instruction": "Generate Python code for Factorio",
                "input": "Smelt iron ore into plates",
                "output": "furnace = game.place_entity(Prototype.StoneFurnace, position=Position(x=0, y=0))\ngame.insert_item(furnace, Prototype.IronOre, quantity=10)\ngame.insert_item(furnace, Prototype.Coal, quantity=5)",
            },
        ]
    )

    # Building examples
    examples.extend(
        [
            {
                "instruction": "Generate Python code for Factorio",
                "input": "Build a stone furnace",
                "output": "game.place_entity(Prototype.StoneFurnace, position=Position(x=0, y=0))",
            },
            {
                "instruction": "Generate Python code for Factorio",
                "input": "Place a burner mining drill on iron ore",
                "output": "iron_patch = game.get_resource_patch(Prototype.IronOre)[0]\ngame.place_entity(Prototype.BurnerMiningDrill, position=iron_patch, direction=Direction.UP)",
            },
            {
                "instruction": "Generate Python code for Factorio",
                "input": "Build an assembling machine",
                "output": "game.place_entity(Prototype.AssemblingMachine1, position=Position(x=5, y=5))",
            },
        ]
    )

    # Inserter examples
    examples.extend(
        [
            {
                "instruction": "Generate Python code for Factorio",
                "input": "Place an inserter between chest and furnace",
                "output": "chest_pos = Position(x=0, y=0)\nfurnace_pos = Position(x=2, y=0)\ngame.place_entity(Prototype.BurnerInserter, position=Position(x=1, y=0), direction=Direction.RIGHT)",
            },
            {
                "instruction": "Generate Python code for Factorio",
                "input": "Insert coal into furnace",
                "output": "furnace = game.get_entity(Prototype.StoneFurnace, Position(x=0, y=0))\ngame.insert_item(furnace, Prototype.Coal, quantity=5)",
            },
        ]
    )

    # Complex automation examples
    examples.extend(
        [
            {
                "instruction": "Generate Python code for Factorio",
                "input": "Create an iron production line",
                "output": "# Place mining drill\niron_patch = game.get_resource_patch(Prototype.IronOre)[0]\ndrill = game.place_entity(Prototype.BurnerMiningDrill, position=iron_patch)\n\n# Place furnace\nfurnace = game.place_entity(Prototype.StoneFurnace, position=Position(x=iron_patch.x + 2, y=iron_patch.y))\n\n# Connect with inserter\ngame.place_entity(Prototype.BurnerInserter, position=Position(x=iron_patch.x +1, y=iron_patch.y), direction=Direction.RIGHT)\n\n# Fuel both\ngame.insert_item(drill, Prototype.Coal, quantity=5)\ngame.insert_item(furnace, Prototype.Coal, quantity=5)",
            },
            {
                "instruction": "Generate Python code for Factorio",
                "input": "Build a coal-powered setup",
                "output": "# Find coal patch\ncoal_patch = game.get_resource_patch(Prototype.Coal)[0]\n\n# Place drill on coal\ndrill = game.place_entity(Prototype.BurnerMiningDrill, position=coal_patch)\n\n# Place chest to collect coal\nchest = game.place_entity(Prototype.WoodenChest, position=Position(x=coal_patch.x + 2, y=coal_patch.y))\n\n# Connect with inserter\ngame.place_entity(Prototype.BurnerInserter, position=Position(x=coal_patch.x + 1, y=coal_patch.y), direction=Direction.RIGHT)\n\n# Initial fuel\ngame.insert_item(drill, Prototype.Coal, quantity=2)",
            },
        ]
    )

    # Movement examples
    examples.extend(
        [
            {
                "instruction": "Generate Python code for Factorio",
                "input": "Move to position (10, 10)",
                "output": "game.move_to(Position(x=10, y=10))",
            },
            {
                "instruction": "Generate Python code for Factorio",
                "input": "Move to nearest iron ore",
                "output": "iron_patch = game.get_resource_patch(Prototype.IronOre)[0]\ngame.move_to(iron_patch)",
            },
        ]
    )

    # Inspection examples
    examples.extend(
        [
            {
                "instruction": "Generate Python code for Factorio",
                "input": "Check inventory for iron plates",
                "output": "iron_count = game.inspect_inventory()[Prototype.IronPlate]\nprint(f'Iron plates: {iron_count}')",
            },
            {
                "instruction": "Generate Python code for Factorio",
                "input": "Find all stone furnaces nearby",
                "output": "furnaces = game.get_entities(Prototype.StoneFurnace, radius=10)\nprint(f'Found {len(furnaces)} furnaces')",
            },
        ]
    )

    return examples


if __name__ == "__main__":
    examples = create_code_examples()

    output_file = Path("training_data/factorio_code_manual.jsonl")
    with open(output_file, "w") as f:
        for ex in examples:
            f.write(json.dumps(ex, ensure_ascii=False) + "\n")

    print(f"✅ Created {len(examples)} manual code examples")
    print(f"📁 Saved to: {output_file}")
    print()
    print("📊 Example:")
    print(json.dumps(examples[0], indent=2, ensure_ascii=False))
