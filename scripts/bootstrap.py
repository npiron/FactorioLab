"""
Bootstrap INTRODUCTIF: Apprendre les bases proprement
Objectif: Maîtriser le craft manuel, le placement d'entités uniques, et le stockage.
"""

import json
from datetime import datetime
from pathlib import Path

# Nouvel objectif : Apprentissage progressif
GOAL = """
🎯 OBJECTIF TUTORIEL:
1. Récolter juste assez de pierre (5) pour UN fourneau.
2. Crafter et poser CE fourneau.
3. Faire cuire quelques minerais de fer manuellement.
4. Crafter UN coffre en bois.
5. Stocker le surplus dans le coffre.

NE PAS surconsommer les ressources ! Commence PETIT.
"""

# Curriculum progressif
TUTORIAL_CURRICULUM = [
    # ============================================
    # ETAPE 1: Le premier fourneau
    # ============================================
    {
        "type": "1_craft_one_furnace",
        "category": "basics",
        "order": 1,
        "description": "Récolter 5 pierres et crafter UN seul fourneau.",
        "code": """# Etape 1: Crafter UN fourneau
# Il faut 5 pierres. Si on ne les a pas, on les récolte.

inv = inspect_inventory()
stone_count = inv.get(Prototype.Stone, 0)

if stone_count < 5:
    print(f"Pas assez de pierre ({stone_count}/5). Récolte...")
    stone_pos = nearest(Resource.Stone)
    move_to(stone_pos)
    # Juste assez pour un fourneau !
    harvest_resource(stone_pos, quantity=5) 

# Crafter UN SEUL fourneau
craft_item(Prototype.StoneFurnace, quantity=1)
print("✅ Premier fourneau crafté !")
""",
    },
    # ============================================
    # ETAPE 2: Cuisson manuelle
    # ============================================
    {
        "type": "2_smelt_iron_manual",
        "category": "basics",
        "order": 2,
        "description": "Poser le fourneau et cuire 10 fers.",
        "code": """# Etape 2: Utiliser le fourneau
# On va faire des plaques de fer qui serviront pour la suite.

# Trouver une zone libre près du fer (pour pas marcher trop)
iron_ore_pos = nearest(Resource.IronOre)
target_pos = Position(x=iron_ore_pos.x + 3, y=iron_ore_pos.y)
move_to(target_pos)

# Poser le fourneau
furnace = place_entity(Prototype.StoneFurnace, target_pos)

# Mettre du carburant (Coal ou Wood)
# On récolte un peu de bois ou charbon si besoin
fuel = Prototype.Coal if nearest(Resource.Coal) else Prototype.Wood
fuel_pos = nearest(Resource.Coal if fuel == Prototype.Coal else Resource.Tree)

move_to(fuel_pos)
harvest_resource(fuel_pos, quantity=5)

# Retour au fourneau
move_to(furnace.position)
insert_item(fuel, furnace, quantity=5)

# Mettre du minerai de fer
harvest_resource(iron_ore_pos, quantity=5) # Prendre un peu de minerai
move_to(furnace.position)
insert_item(Prototype.IronOre, furnace, quantity=5)

print(f"✅ Fourneau en marche à {furnace.position}")
""",
    },
    # ============================================
    # ETAPE 3: Stockage (Coffre)
    # ============================================
    {
        "type": "3_craft_and_use_chest",
        "category": "logistics",
        "order": 3,
        "description": "Crafter un coffre en bois et stocker l'excès.",
        "code": """# Etape 3: Le stockage
# Un coffre en bois coûte 2 bois.

inv = inspect_inventory()
wood_count = inv.get(Prototype.Wood, 0)

if wood_count < 2:
    print("Besoin de bois pour le coffre...")
    tree_pos = nearest(Resource.Tree)
    move_to(tree_pos)
    harvest_resource(tree_pos, quantity=2)

# Crafter le coffre
craft_item(Prototype.WoodChest, quantity=1)

# Le poser à côté du fourneau
furnace_pos = nearest(Prototype.StoneFurnace)
chest_pos = Position(x=furnace_pos.x + 1, y=furnace_pos.y)
move_to(chest_pos)

chest = place_entity(Prototype.WoodChest, chest_pos)

# Mettre tout le surplus de pierre ou bois dedans (garder un peu)
# Exemple: on met toute la pierre sauf 5
stone_count = inspect_inventory().get(Prototype.Stone, 0)
if stone_count > 5:
    to_store = stone_count - 5
    insert_item(Prototype.Stone, chest, quantity=to_store)
    print(f"Stocké {to_store} pierres dans le coffre")

print("✅ Coffre posé et utilisé !")
""",
    },
    {
        "type": "4_automated_mining",
        "category": "automation",
        "order": 4,
        "description": "Automatiser le minage avec une Forreuse Thermique (Burner Mining Drill).",
        "code": """# Etape 4: Automatiser le minage
# On ne veut plus miner à la main !
# Il faut une Burner Mining Drill.
# Coût: 3 Iron Gear + 1 Stone Furnace + 3 Iron Plate.

# Vérifier ressources
inv = inspect_inventory()
iron_plate = inv.get(Prototype.IronPlate, 0)
stone = inv.get(Prototype.Stone, 0)

if iron_plate >= 3 and stone >= 5: # Assez pour furnace + un peu de reste
    # Craft
    drill = craft_item(Prototype.BurnerMiningDrill, quantity=1)
    print(f"✅ Crafté: {drill} Burner Mining Drill")
    
    # Placer sur du CHARBON (pour s'auto-alimenter plus tard) ou FER
    # Priorité: Charbon (Energie)
    coal_pos = nearest(Resource.Coal)
    
    # Trouver une case valide sur le charbon
    move_to(coal_pos)
    drill_ent = place_entity(Prototype.BurnerMiningDrill, coal_pos)
    
    if drill_ent:
        # Placer un coffre devant la sortie (Position + Direction)
        # Simplification: on pose juste à côte
        chest_pos = Position(x=coal_pos.x, y=coal_pos.y+1) # Hypothèse sortie Sud
        place_entity(Prototype.WoodChest, chest_pos)
        
        # Mettre du carburant dans la forreuse
        insert_item(Prototype.Coal, drill_ent, quantity=5)
        print("✅ Forreuse posée et alimentée sur le charbon !")
    else:
        print("❌ Impossible de poser la forreuse (collision ?)")

else:
    print(f"❌ Pas assez de ressources pour la forreuse (Fer: {iron_plate}, Pierre: {stone})")
""",
    },
    # ============================================
    # ETAPE 5: Automatisation simple (Burner Inserter)
    # ============================================
    {
        "type": "5_simple_automation",
        "category": "automation",
        "order": 5,
        "description": "Automatiser le fourneau avec un bras robotisé.",
        "code": """# Etape 4: Première automatisation
# On veut que le fourneau se remplisse seul.
# Il faut un Burner Inserter. Coût: 1 Iron Plate + 1 Gear.
# Gear coût: 2 Iron Plates.
# Total: 3 Iron Plates.

# Récupérer les plaques de fer du fourneau
furnace_pos = nearest(Prototype.StoneFurnace)
move_to(furnace_pos)
# extract_item retire le contenu (plaques cuites)
extracted = extract_item(furnace_pos, Prototype.IronPlate) 
print(f"Récupéré {extracted} plaques de fer")

if extracted >= 3:
    # On craft l'inserter
    craft_item(Prototype.BurnerInserter, quantity=1)
    
    # On le place pour mettre du minerai (depuis un coffre ou le sol)
    # Disons qu'on met un coffre d'entrée devant
    chest_pos = Position(x=furnace_pos.x, y=furnace_pos.y + 1)
    place_entity(Prototype.WoodChest, chest_pos)
    
    # Inserter entre le coffre et le fourneau
    # Chest (y+1) -> Inserter (y+0.5?? non grid integer) -> Furnace (y)
    # On place l'inserter à côté
    
    print("✅ Inserter crafté (concept)")
else:
    print("❌ Pas assez de plaques de fer, il faut attendre la cuisson.")
""",
    },
]


def inject_tutorial_curriculum():
    """Injecte le curriculum tutoriel"""
    # Use project root's data/knowledge/ directory
    project_root = Path(__file__).parent.parent
    kb_dir = project_root / "data" / "knowledge"
    kb_dir.mkdir(parents=True, exist_ok=True)
    kb_file = kb_dir / "megabase_knowledge.json"

    # Structure de base propre
    kb = {
        "current_phase": 1,
        "building_blocks": {},
        "successful_patterns": [],
        "failed_attempts": [],
        "phase_milestones": {},
        "stats": {"total_experiments": 0, "successful": 0, "failed": 0},
        "goal": GOAL,
    }

    # Add tutorial curriculum
    kb["building_blocks"]["minibase_curriculum"] = []

    print("🏭 INJECTION DU TUTORIEL DÉBUTANT")
    for pattern in TUTORIAL_CURRICULUM:
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
        print(f"  ✅ {pattern['order']}. {pattern['type']}")

    with open(kb_file, "w") as f:
        json.dump(kb, f, indent=2)

    print("\n✨ Knowledge Base réinitialisée pour le tutoriel !")
    print(GOAL)


if __name__ == "__main__":
    inject_tutorial_curriculum()
