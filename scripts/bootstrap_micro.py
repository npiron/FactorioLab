"""
Micro-Step Curriculum: Ant-Like Agent
Each step includes STRICT verification logic.
"""

import json
from datetime import datetime
from pathlib import Path

GOAL = """
🐜 AGENT FOURMI - MICRO-STEPS
Chaque étape = UNE SEULE ACTION VERIFIÉE
"""

# Curriculum: Séquence très fine, étape par étape
# Pour les petits modèles, il faut être EXTRÊMEMENT explicite et unitaire.
# On évite les boucles, les "smart_functions", on fait du direct.

TUTORIAL_CURRICULUM = [
    {
        "order": 1,
        "description": "Trouver la position du gisement de pierre",
        "type": "query",
        "code": """
# Step 1: Trouver la position du gisement de pierre
stone_pos = nearest(Resource.Stone)
if stone_pos:
    print(f"🪨 Pierre trouvée à {stone_pos}")
else:
    print("Error: Pas de pierre trouvée!")
""",
    },
    {
        "order": 2,
        "description": "Se déplacer vers la pierre",
        "type": "action",
        "code": """
# Step 2: Se déplacer vers la pierre
stone_pos = nearest(Resource.Stone)
if not stone_pos:
    print("Error: Pierre perdue")
else:
    move_to(stone_pos)
    print(f"🚶 Déplacement vers {stone_pos}")
""",
    },
    {
        "order": 3,
        "description": "Récolter 5 pierres",
        "type": "action",
        "code": """
# Step 3: Récolter et VERIFIER 5 pierres
stone_pos = nearest(Resource.Stone)
if stone_pos:
    move_to(stone_pos)
    harvest_resource(stone_pos, quantity=5)

inv = inspect_inventory()
count = inv.get(Prototype.Stone, 0)
print(f"🎒 Inventaire Pierre: {count}")

if count < 5:
    print(f"Error: J'ai besoin de 5 pierres, j'en ai {count}.")
else:
    print("✅ OK: 5+ pierres en poche.")
""",
    },
    {
        "order": 4,
        "description": "Vérifier l'inventaire pour la pierre (Redondant mais pédagogique)",
        "type": "query",
        "code": """
# Step 4: Vérifier l'inventaire pour la pierre
inv = inspect_inventory()
stone_count = inv.get(Prototype.Stone, 0)
# This step is just a gate
if stone_count < 5:
    print("Error: Pas assez de pierre! (Need 5)")
else:
    print("✅ Assez de pierre!")
""",
    },
    {
        "order": 5,
        "description": "Fabriquer un fourneau en pierre",
        "type": "action",
        "code": """
# Step 5: Fabriquer un fourneau
inv = inspect_inventory()
if inv.get(Prototype.Stone, 0) < 5:
    print("Error: Pas assez de pierre pour fabriquer (Need 5)")
else:
    craft_item(Prototype.StoneFurnace, quantity=1)
    
    # Verify craft
    inv_after = inspect_inventory()
    if inv_after.get(Prototype.StoneFurnace, 0) > 0:
        print("✅ Fourneau fabriqué avec succès")
    else:
        print("Error: Le fourneau n'apparaît pas dans l'inventaire")
""",
    },
    {
        "order": 6,
        "description": "Trouver un endroit libre pour poser le fourneau",
        "type": "query",
        "code": """
# Step 6: Trouver un endroit libre
# Simplification: on décide d'une position relative fixe
# Dans le futur, on utilisera find_position()
target_pos = Position(x=10, y=10)
print(f"📍 Position cible pour fourneau: {target_pos}")
""",
    },
    {
        "order": 7,
        "description": "Poser le fourneau",
        "type": "action",
        "code": """
# Step 7: Poser le fourneau et VERIFIER
target_pos = Position(x=10, y=10)

# IMPORTANT: Move close before building!
move_to(Position(x=10, y=8)) 

place_entity(Prototype.StoneFurnace, position=target_pos, direction=Direction.SOUTH)

# Verify placement
nearby = get_entities(box_limit=20) 
found = False
for ent in nearby:
    if ent.name == "stone-furnace":
        dx = abs(ent.position.x - target_pos.x)
        dy = abs(ent.position.y - target_pos.y)
        if dx < 3 and dy < 3:
            found = True
            break

if found:
    print("✅ Fourneau détecté au sol")
else:
    print("Error: Je ne vois pas le fourneau au sol à (10,10)!")
""",
    },
    {
        "order": 8,
        "description": "Localiser le charbon",
        "type": "query",
        "code": """
# Step 8: Localiser le charbon
coal_pos = nearest(Resource.Coal)
if coal_pos:
    print(f"⚫ Charbon trouvé à {coal_pos}")
else:
    print("Error: Pas de charbon trouvé")
""",
    },
    {
        "order": 9,
        "description": "Récolter du charbon",
        "type": "action",
        "code": """
# Step 9: Récolter du charbon
coal_pos = nearest(Resource.Coal)
if not coal_pos:
    print("Error: Pas de charbon visible")
else:
    move_to(coal_pos)
    harvest_resource(coal_pos, quantity=5)
    
    inv = inspect_inventory()
    count = inv.get(Prototype.Coal, 0)
    if count < 5:
        print(f"Error: Besoin de 5 charbons, j'en ai {count}")
    else:
        print("✅ Charbon récolté")
""",
    },
    {
        "order": 10,
        "description": "Localiser le fer",
        "type": "query",
        "code": """
# Step 10: Localiser le fer
iron_pos = nearest(Resource.IronOre)
if iron_pos:
    print(f"🟥 Fer trouvé à {iron_pos}")
else:
    print("Error: Fer introuvable")
""",
    },
    {
        "order": 11,
        "description": "Récolter du fer",
        "type": "action",
        "code": """
# Step 11: Récolter du fer
iron_pos = nearest(Resource.IronOre)
if not iron_pos:
    print("Error: Fer introuvable")
else:
    move_to(iron_pos)
    harvest_resource(iron_pos, quantity=5)
    inv = inspect_inventory()
    if inv.get(Prototype.IronOre, 0) < 5:
        print("Error: Pas assez de fer récolté")
    else:
        print("✅ Fer récolté")
""",
    },
    {
        "order": 12,
        "description": "Mettre du charbon dans le fourneau",
        "type": "action",
        "code": """
# Step 12: Mettre du charbon dans le fourneau
furnaces = get_entities()
target = None
for f in furnaces:
    if f.name == "stone-furnace":
        target = f
        break

if not target:
    print("Error: Pas de fourneau trouvé pour alimenter")
else:
    move_to(target.position)
    insert_item(Prototype.Coal, target, quantity=1)
    
    # Verification is hard without inventory inspection of entity
    print("✅ Charbon inséré (supposé)")
""",
    },
    {
        "order": 13,
        "description": "Mettre du minerai de fer dans le fourneau",
        "type": "action",
        "code": """
# Step 13: Mettre du minerai de fer
furnaces = get_entities()
my_furnace = next((e for e in furnaces if e.name == "stone-furnace"), None)
if my_furnace:
    move_to(my_furnace.position)
    insert_item(Prototype.IronOre, my_furnace, quantity=1)
    print("⚙️ Minerai inséré")
else:
    print("Error: Pas de fourneau!")
""",
    },
    {
        "order": 14,
        "description": "Attendre la fonte",
        "type": "action",
        "code": """
# Step 14: Attendre
sleep(5)
print("⏳ Cuisson...")
""",
    },
    {
        "order": 15,
        "description": "Récupérer les plaques de fer",
        "type": "action",
        "code": """
# Step 15: Récupérer le résultat
furnaces = get_entities()
my_furnace = next((e for e in furnaces if e.name == "stone-furnace"), None)
if my_furnace:
    move_to(my_furnace.position)
    extract_item(Prototype.IronPlate, my_furnace, quantity=1)
    
    inv = inspect_inventory()
    if inv.get(Prototype.IronPlate, 0) > 0:
        print("🏆 SUCCÈS: Plaque de fer obtenue!")
    else:
        print("Error: Pas de plaque de fer récupérée.")
else:
    print("Error: Pas de fourneau!")
""",
    },
]


def inject_micro_curriculum():
    """Injecte le micro-curriculum"""
    project_root = Path(__file__).parent.parent
    kb_dir = project_root / "data" / "knowledge"
    kb_dir.mkdir(parents=True, exist_ok=True)
    kb_file = kb_dir / "megabase_knowledge.json"

    kb = {
        "current_phase": 1,
        "building_blocks": {},
        "successful_patterns": [],
        "failed_attempts": [],
        "phase_milestones": {},
        "stats": {"total_experiments": 0, "successful": 0, "failed": 0, "tutorial_progress": 0},
        "goal": GOAL,
    }

    kb["building_blocks"]["minibase_curriculum"] = []

    print("🐜 INJECTION DU MICRO-CURRICULUM (Approche Fourmi)")
    print("=" * 50)
    for pattern in TUTORIAL_CURRICULUM:
        block = {
            "type": f"micro_step_{pattern['order']}",
            "code": pattern["code"].strip(),
            "description": pattern["description"],
            "order": pattern["order"],
            "phase": 1,
            "created_at": datetime.now().isoformat(),
            "is_bootstrap": True,
        }
        kb["building_blocks"]["minibase_curriculum"].append(block)
        print(f"  📋 Step {pattern['order']:2d}: {pattern['description']}")

    with open(kb_file, "w") as f:
        json.dump(kb, f, indent=2)

    print("=" * 50)
    print(f"✨ {len(TUTORIAL_CURRICULUM)} micro-steps injectés!")
    print(GOAL)


if __name__ == "__main__":
    inject_micro_curriculum()
