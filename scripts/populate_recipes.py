import json
import os

recipes = {
    # RAW
    "wood": {"category": "raw", "ingredients": []},
    "stone": {"category": "raw", "ingredients": []},
    "iron-ore": {"category": "raw", "ingredients": []},
    "copper-ore": {"category": "raw", "ingredients": []},
    "coal": {"category": "raw", "ingredients": []},
    "water": {"category": "fluid", "ingredients": []},
    "crude-oil": {"category": "fluid", "ingredients": []},
    # INTERMEDIATES
    "iron-plate": {"category": "smelting", "ingredients": [{"name": "iron-ore", "amount": 1}]},
    "copper-plate": {"category": "smelting", "ingredients": [{"name": "copper-ore", "amount": 1}]},
    "steel-plate": {"category": "smelting", "ingredients": [{"name": "iron-plate", "amount": 5}]},
    "stone-brick": {"category": "smelting", "ingredients": [{"name": "stone", "amount": 2}]},
    "iron-stick": {
        "category": "crafting",
        "ingredients": [{"name": "iron-plate", "amount": 1}],
        "yield": 2,
    },
    "iron-gear-wheel": {
        "category": "crafting",
        "ingredients": [{"name": "iron-plate", "amount": 2}],
    },
    "copper-cable": {
        "category": "crafting",
        "ingredients": [{"name": "copper-plate", "amount": 1}],
        "yield": 2,
    },
    "electronic-circuit": {
        "category": "crafting",
        "ingredients": [{"name": "iron-plate", "amount": 1}, {"name": "copper-cable", "amount": 3}],
    },
    "advanced-circuit": {
        "category": "crafting",
        "ingredients": [
            {"name": "electronic-circuit", "amount": 2},
            {"name": "plastic-bar", "amount": 2},
            {"name": "copper-cable", "amount": 4},
        ],
    },
    "plastic-bar": {
        "category": "chemistry",
        "ingredients": [{"name": "coal", "amount": 1}, {"name": "petroleum-gas", "amount": 20}],
    },
    "sulfur": {
        "category": "chemistry",
        "ingredients": [{"name": "water", "amount": 30}, {"name": "petroleum-gas", "amount": 30}],
        "yield": 2,
    },
    "battery": {
        "category": "chemistry",
        "ingredients": [
            {"name": "sulfuric-acid", "amount": 20},
            {"name": "iron-plate", "amount": 1},
            {"name": "copper-plate", "amount": 1},
        ],
    },
    "engine-unit": {
        "category": "crafting",
        "ingredients": [
            {"name": "steel-plate", "amount": 1},
            {"name": "iron-gear-wheel", "amount": 1},
            {"name": "pipe", "amount": 2},
        ],
    },
    # LOGISTICS
    "wooden-chest": {"category": "crafting", "ingredients": [{"name": "wood", "amount": 2}]},
    "iron-chest": {"category": "crafting", "ingredients": [{"name": "iron-plate", "amount": 8}]},
    "transport-belt": {
        "category": "crafting",
        "ingredients": [
            {"name": "iron-plate", "amount": 1},
            {"name": "iron-gear-wheel", "amount": 1},
        ],
        "yield": 2,
    },
    "underground-belt": {
        "category": "crafting",
        "ingredients": [
            {"name": "iron-plate", "amount": 10},
            {"name": "transport-belt", "amount": 5},
        ],
        "yield": 2,
    },
    "splitter": {
        "category": "crafting",
        "ingredients": [
            {"name": "electronic-circuit", "amount": 5},
            {"name": "iron-plate", "amount": 5},
            {"name": "transport-belt", "amount": 4},
        ],
    },
    "burner-inserter": {
        "category": "crafting",
        "ingredients": [
            {"name": "iron-plate", "amount": 1},
            {"name": "iron-gear-wheel", "amount": 1},
        ],
    },
    "inserter": {
        "category": "crafting",
        "ingredients": [
            {"name": "electronic-circuit", "amount": 1},
            {"name": "iron-gear-wheel", "amount": 1},
            {"name": "iron-plate", "amount": 1},
        ],
    },
    "long-handed-inserter": {
        "category": "crafting",
        "ingredients": [
            {"name": "iron-gear-wheel", "amount": 1},
            {"name": "iron-plate", "amount": 1},
            {"name": "inserter", "amount": 1},
        ],
    },
    "pipe": {"category": "crafting", "ingredients": [{"name": "iron-plate", "amount": 1}]},
    "pipe-to-ground": {
        "category": "crafting",
        "ingredients": [{"name": "pipe", "amount": 10}, {"name": "iron-plate", "amount": 5}],
        "yield": 2,
    },
    # PRODUCTION
    "stone-furnace": {"category": "crafting", "ingredients": [{"name": "stone", "amount": 5}]},
    "steel-furnace": {
        "category": "crafting",
        "ingredients": [
            {"name": "steel-plate", "amount": 6},
            {"name": "stone-brick", "amount": 10},
        ],
    },
    "burner-mining-drill": {
        "category": "crafting",
        "ingredients": [
            {"name": "stone-furnace", "amount": 1},
            {"name": "iron-plate", "amount": 3},
            {"name": "iron-gear-wheel", "amount": 3},
        ],
    },
    "electric-mining-drill": {
        "category": "crafting",
        "ingredients": [
            {"name": "electronic-circuit", "amount": 3},
            {"name": "iron-gear-wheel", "amount": 5},
            {"name": "iron-plate", "amount": 10},
        ],
    },
    "offshore-pump": {
        "category": "crafting",
        "ingredients": [
            {"name": "electronic-circuit", "amount": 2},
            {"name": "pipe", "amount": 1},
            {"name": "iron-gear-wheel", "amount": 1},
        ],
    },
    "boiler": {
        "category": "crafting",
        "ingredients": [{"name": "stone-furnace", "amount": 1}, {"name": "pipe", "amount": 4}],
    },
    "steam-engine": {
        "category": "crafting",
        "ingredients": [
            {"name": "iron-gear-wheel", "amount": 8},
            {"name": "pipe", "amount": 5},
            {"name": "iron-plate", "amount": 10},
        ],
    },
    "assembling-machine-1": {
        "category": "crafting",
        "ingredients": [
            {"name": "electronic-circuit", "amount": 3},
            {"name": "iron-gear-wheel", "amount": 5},
            {"name": "iron-plate", "amount": 9},
        ],
    },
    # MILITARY
    "pistol": {
        "category": "crafting",
        "ingredients": [{"name": "copper-plate", "amount": 5}, {"name": "iron-plate", "amount": 5}],
    },
    "firearm-magazine": {
        "category": "crafting",
        "ingredients": [{"name": "iron-plate", "amount": 4}],
    },
    "radar": {
        "category": "crafting",
        "ingredients": [
            {"name": "electronic-circuit", "amount": 5},
            {"name": "iron-gear-wheel", "amount": 5},
            {"name": "iron-plate", "amount": 10},
        ],
    },
    # SCIENCE
    "automation-science-pack": {
        "category": "crafting",
        "ingredients": [
            {"name": "copper-plate", "amount": 1},
            {"name": "iron-gear-wheel", "amount": 1},
        ],
    },
    "logistic-science-pack": {
        "category": "crafting",
        "ingredients": [{"name": "transport-belt", "amount": 1}, {"name": "inserter", "amount": 1}],
    },
}

output_path = "data/knowledge/recipes.json"
# Ensure directory exists
os.makedirs(os.path.dirname(output_path), exist_ok=True)

with open(output_path, "w") as f:
    json.dump({"recipes": recipes}, f, indent=2)

print(f"✅ Generated {len(recipes)} recipes in {output_path}")
