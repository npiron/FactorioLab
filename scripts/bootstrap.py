"""
Bootstrap COMPLET pour une mini-base automatisée
Objectif: Produire les composants de base pour les Green Circuits

PROGRESSION:
1. Extraction automatique (foreuses + belts)
2. Fonderie en ligne (plusieurs fourneaux)
3. Production de composants (gears, copper wire)
4. Finalement: Green Circuits

"""

import json
from datetime import datetime
from pathlib import Path

# Objectif clair
GOAL = """
🎯 OBJECTIF MINI-BASE:
Construire une base automatisée qui produit:
1. Un BELT de plaques de fer (10+ fourneaux en ligne)
2. Un BELT de plaques de cuivre (10+ fourneaux en ligne)
3. Une machine d'assemblage qui fait des engrenages (iron gears)
4. Une machine d'assemblage qui fait des câbles de cuivre
5. Finalement: Une machine qui fait des circuits électroniques (green circuits)

Tout doit être AUTOMATISÉ avec des belts et des inserters!
"""

# Patterns pour construire la mini-base
MINIBASE_CURRICULUM = [
    # ============================================
    # PHASE A: Préparation (craft items de base)
    # ============================================
    {
        "type": "A1_craft_initial_items",
        "category": "A_preparation",
        "order": 1,
        "description": "Fabriquer les items de base nécessaires (fourneaux, drills, inserters, belts)",
        "code": """# Fabriquer les items de base avec l'inventaire de départ
# On a déjà les ressources, on peut directement fabriquer!

# Fourneaux (beaucoup!)
craft_item(Prototype.StoneFurnace, quantity=12)

# Burner mining drills
craft_item(Prototype.BurnerMiningDrill, quantity=4)

# Burner inserters
craft_item(Prototype.BurnerInserter, quantity=10)

# Transport belts (beaucoup!)
craft_item(Prototype.TransportBelt, quantity=100)

inventory = inspect_inventory()
print(f'Crafted basic items: {inventory}')""",
    },
    # ============================================
    # PHASE B: Ligne de fonderie FER
    # ============================================
    {
        "type": "B1_place_iron_drill",
        "category": "B_iron_smelting",
        "order": 3,
        "description": "Placer une foreuse sur le fer",
        "code": """# Placer la foreuse sur le minerai de fer
iron_pos = nearest(Resource.IronOre)
move_to(iron_pos)

# Foreuse qui extrait vers le bas
iron_drill = place_entity(
    Prototype.BurnerMiningDrill,
    position=iron_pos,
    direction=Direction.DOWN
)

# Alimenter avec charbon
insert_item(Prototype.Coal, iron_drill, quantity=50)
print(f'Iron drill placed at {iron_drill.position}')""",
    },
    {
        "type": "B2_iron_furnace_line",
        "category": "B_iron_smelting",
        "order": 4,
        "description": "Créer une ligne de fourneaux pour le fer",
        "code": """# Créer une ligne de 6 fourneaux pour le fer
# Les fourneaux doivent être alignés pour que le belt passe

base_x = iron_drill.drop_position.x
base_y = iron_drill.drop_position.y + 2

furnaces = []
for i in range(6):
    pos = Position(x=base_x + (i * 2), y=base_y)
    furnace = place_entity(
        Prototype.StoneFurnace,
        position=pos,
        direction=Direction.UP
    )
    insert_item(Prototype.Coal, furnace, quantity=20)
    furnaces.append(furnace)
    print(f'Furnace {i+1} at {furnace.position}')

print(f'Created line of {len(furnaces)} furnaces')""",
    },
    {
        "type": "B3_iron_input_belt",
        "category": "B_iron_smelting",
        "order": 5,
        "description": "Belt pour amener le minerai aux fourneaux",
        "code": """# Belt pour transporter le minerai de fer du drill aux furnaces
# Le belt va du drill jusqu'aux furnaces

start = iron_drill.drop_position
end = furnaces[0].position

# Placer des belts en ligne
for i in range(10):
    pos = Position(x=start.x, y=start.y + i)
    place_entity(
        Prototype.TransportBelt,
        position=pos,
        direction=Direction.DOWN
    )

print('Input belt created for iron ore')""",
    },
    {
        "type": "B4_iron_inserters",
        "category": "B_iron_smelting",
        "order": 6,
        "description": "Inserters pour alimenter les fourneaux",
        "code": """# Placer des inserters pour prendre le minerai du belt et le mettre dans les fourneaux
for i, furnace in enumerate(furnaces):
    # Inserter devant chaque fourneau
    inserter_pos = Position(x=furnace.position.x, y=furnace.position.y - 1)
    inserter = place_entity(
        Prototype.BurnerInserter,
        position=inserter_pos,
        direction=Direction.DOWN  # Prend du belt, met dans furnace
    )
    insert_item(Prototype.Coal, inserter, quantity=10)
    print(f'Inserter {i+1} placed')

print('All inserters placed for iron line')""",
    },
    {
        "type": "B5_iron_output_belt",
        "category": "B_iron_smelting",
        "order": 7,
        "description": "Belt de sortie pour les plaques de fer",
        "code": """# Belt de sortie pour récupérer les plaques de fer des fourneaux
for i, furnace in enumerate(furnaces):
    # Belt derrière chaque fourneau (sortie)
    belt_pos = Position(x=furnace.position.x, y=furnace.position.y + 1)
    place_entity(
        Prototype.TransportBelt,
        position=belt_pos,
        direction=Direction.RIGHT  # Les plaques vont vers la droite
    )

print('Output belt created for iron plates')""",
    },
    # ============================================
    # PHASE C: Ligne de fonderie CUIVRE (similaire)
    # ============================================
    {
        "type": "C1_place_copper_drill",
        "category": "C_copper_smelting",
        "order": 8,
        "description": "Placer une foreuse sur le cuivre",
        "code": """# Placer la foreuse sur le minerai de cuivre
copper_pos = nearest(Resource.CopperOre)
move_to(copper_pos)

copper_drill = place_entity(
    Prototype.BurnerMiningDrill,
    position=copper_pos,
    direction=Direction.DOWN
)

insert_item(Prototype.Coal, copper_drill, quantity=50)
print(f'Copper drill placed at {copper_drill.position}')""",
    },
    {
        "type": "C2_copper_furnace_line",
        "category": "C_copper_smelting",
        "order": 9,
        "description": "Créer une ligne de fourneaux pour le cuivre",
        "code": """# Créer une ligne de 6 fourneaux pour le cuivre
base_x = copper_drill.drop_position.x
base_y = copper_drill.drop_position.y + 2

copper_furnaces = []
for i in range(6):
    pos = Position(x=base_x + (i * 2), y=base_y)
    furnace = place_entity(
        Prototype.StoneFurnace,
        position=pos,
        direction=Direction.UP
    )
    insert_item(Prototype.Coal, furnace, quantity=20)
    copper_furnaces.append(furnace)

print(f'Created copper smelting line with {len(copper_furnaces)} furnaces')""",
    },
    # ============================================
    # PHASE D: Machines d'assemblage
    # ============================================
    {
        "type": "D1_craft_assemblers",
        "category": "D_assembly",
        "order": 10,
        "description": "Fabriquer des machines d'assemblage",
        "code": """# Fabriquer des machines d'assemblage
# Besoin: circuits électroniques, engrenages, plaques de fer

# D'abord faire les circuits manuellement
craft_item(Prototype.ElectronicCircuit, quantity=10)
craft_item(Prototype.IronGearWheel, quantity=20)

# Maintenant les assemblers
craft_item(Prototype.AssemblingMachine1, quantity=3)

inventory = inspect_inventory()
print(f'Crafted assemblers: {inventory}')""",
    },
    {
        "type": "D2_place_gear_assembler",
        "category": "D_assembly",
        "order": 11,
        "description": "Placer l'assembleur de Iron Gear Wheels",
        "code": """# Placer l'assembleur pour les engrenages
# Il doit recevoir des plaques de fer du belt

# Position après la ligne de fourneaux de fer
gear_assembler_pos = Position(x=furnaces[-1].position.x + 4, y=furnaces[-1].position.y)
move_to(gear_assembler_pos)

gear_assembler = place_entity(
    Prototype.AssemblingMachine1,
    position=gear_assembler_pos,
    direction=Direction.UP
)

# Configurer la recette (Iron Gear Wheel)
set_entity_recipe(gear_assembler, Prototype.IronGearWheel)

print(f'Gear assembler placed at {gear_assembler.position}')""",
    },
    {
        "type": "D3_place_wire_assembler",
        "category": "D_assembly",
        "order": 12,
        "description": "Placer l'assembleur de Copper Wire",
        "code": """# Placer l'assembleur pour les câbles de cuivre
wire_assembler_pos = Position(x=copper_furnaces[-1].position.x + 4, y=copper_furnaces[-1].position.y)
move_to(wire_assembler_pos)

wire_assembler = place_entity(
    Prototype.AssemblingMachine1,
    position=wire_assembler_pos,
    direction=Direction.UP
)

# Configurer la recette (Copper Cable)
set_entity_recipe(wire_assembler, Prototype.CopperCable)

print(f'Wire assembler placed at {wire_assembler.position}')""",
    },
    # ============================================
    # PHASE E: Green Circuits!
    # ============================================
    {
        "type": "E1_place_circuit_assembler",
        "category": "E_circuits",
        "order": 13,
        "description": "Placer l'assembleur de Green Circuits",
        "code": """# L'assembleur final: Electronic Circuits!
# Il a besoin de: Iron Plates + Copper Cables

circuit_assembler_pos = Position(
    x=gear_assembler.position.x + 4,
    y=gear_assembler.position.y
)
move_to(circuit_assembler_pos)

circuit_assembler = place_entity(
    Prototype.AssemblingMachine1,
    position=circuit_assembler_pos,
    direction=Direction.UP
)

# Configurer la recette
set_entity_recipe(circuit_assembler, Prototype.ElectronicCircuit)

print(f'🟢 GREEN CIRCUIT ASSEMBLER at {circuit_assembler.position}')
print('MINI-BASE COMPLETE!')""",
    },
    {
        "type": "E2_connect_circuit_inputs",
        "category": "E_circuits",
        "order": 14,
        "description": "Connecter les entrées du circuit assembler",
        "code": """# Connecter les entrées pour les green circuits
# Besoin: belt de fer plates + belt de copper cables

# Inserter pour les plaques de fer
iron_inserter = place_entity_next_to(
    entity=Prototype.BurnerInserter,
    reference_position=circuit_assembler.position,
    direction=Direction.LEFT
)
insert_item(Prototype.Coal, iron_inserter, quantity=10)

# Inserter pour les câbles de cuivre
copper_inserter = place_entity_next_to(
    entity=Prototype.BurnerInserter,
    reference_position=circuit_assembler.position,
    direction=Direction.UP
)
insert_item(Prototype.Coal, copper_inserter, quantity=10)

print('Circuit assembler connected!')
print('🎉 PRODUCTION DE GREEN CIRCUITS EN COURS!')""",
    },
    {
        "type": "E3_verify_production",
        "category": "E_circuits",
        "order": 15,
        "description": "Vérifier que la production fonctionne",
        "code": """# Vérifier la production
sleep(30)

# Vérifier chaque machine
all_entities = get_entities()
print(f'Total entities placed: {len(all_entities)}')

# Vérifier les assemblers
for entity in all_entities:
    if 'assembling' in str(entity.name).lower():
        print(f'{entity.name} at {entity.position}: {entity.status}')

print('\\n🏭 MINI-BASE STATUS CHECK COMPLETE')""",
    },
]


def inject_minibase_curriculum():
    """Injecte le curriculum mini-base"""
    # Use project root's data/knowledge/ directory
    project_root = Path(__file__).parent.parent
    kb_dir = project_root / "data" / "knowledge"
    kb_dir.mkdir(parents=True, exist_ok=True)
    kb_file = kb_dir / "megabase_knowledge.json"

    if kb_file.exists():
        with open(kb_file) as f:
            kb = json.load(f)
    else:
        kb = {
            "current_phase": 1,
            "building_blocks": {},
            "successful_patterns": [],
            "failed_attempts": [],
            "phase_milestones": {},
            "stats": {"total_experiments": 0, "successful": 0, "failed": 0},
        }

    # Reset to phase 1
    kb["current_phase"] = 1

    # Add minibase curriculum
    kb["building_blocks"]["minibase_curriculum"] = []

    for pattern in MINIBASE_CURRICULUM:
        block = {
            "type": pattern["type"],
            "code": pattern["code"].strip(),
            "category": pattern["category"],
            "description": pattern["description"],
            "order": pattern["order"],
            "phase": 1,
            "created_at": datetime.now().isoformat(),
            "is_bootstrap": True,
        }
        kb["building_blocks"]["minibase_curriculum"].append(block)
        print(f"  ✅ {pattern['order']:2}. {pattern['type']}")

    # Add the goal
    kb["goal"] = GOAL

    with open(kb_file, "w") as f:
        json.dump(kb, f, indent=2)

    print("\n🏭 MINIBASE CURRICULUM INJECTED!")
    print(f"   Total patterns: {len(kb['building_blocks']['minibase_curriculum'])}")
    print(GOAL)


if __name__ == "__main__":
    print("🏭 FACTORIO MINI-BASE BOOTSTRAP")
    print("=" * 60)
    inject_minibase_curriculum()
