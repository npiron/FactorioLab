"""
Simple Starter Agent - Les Bases de Factorio

Objectif: Récolter ressources de base et crafter premiers objets simples
- Récolter du bois (wood)
- Récolter du charbon (coal)
- Crafter un coffre en bois (wooden chest)
- Le placer pour commencer à stocker

Tout simple, tout visible !
"""

STARTER_ACTIONS = [
    # Step 0: Récolter du bois d'arbres
    """
# Trouver et aller vers un arbre
tree_pos = nearest(Resource.Wood)
print(f'Arbre trouvé à {tree_pos}')
move_to(tree_pos)
harvested_wood = harvest_resource(tree_pos, quantity=20)
print(f'Récolté {harvested_wood} bois')
""",
    # Step 1: Récolter du charbon
    """
coal_pos = nearest(Resource.Coal)
print(f'Charbon trouvé à {coal_pos}')
move_to(coal_pos)
harvested_coal = harvest_resource(coal_pos, quantity=20)
print(f'Récolté {harvested_coal} charbon')
""",
    # Step 2: Vérifier inventaire
    """
inv = inspect_inventory()
print(f'Inventaire: {inv}')
""",
    # Step 3: Crafter un coffre en bois (simple!)
    """
# Wooden chest = 2 wood seulement!
chest_count = craft_item(Prototype.WoodenChest, quantity=1)
print(f'Crafté {chest_count} coffre(s) en bois')
""",
    # Step 4: Retourner au spawn et placer le coffre
    """
# Retourner au point de départ (spawn)
spawn_pos = Position(x=0, y=0)
move_to(spawn_pos)
print('Retour au spawn')

# Placer le coffre juste à côté (2 unités devant)
chest_pos = Position(x=0, y=2)
chest = place_entity(
    entity=Prototype.WoodenChest,
    position=chest_pos,
    direction=Direction.UP
)
print(f'Coffre placé à {chest.position}')
""",
    # Step 5: Vérifier le résultat
    """
print('=== MISSION ACCOMPLIE ===')
print('Tu as:')
print('- Récolté du bois et du charbon')
print('- Crafté ton premier coffre')
print('- Placé le coffre dans le monde')
print('Regarde dans Factorio - tu verras le coffre!')
score()
""",
]


def get_starter_code(step: int) -> str:
    """Get code for starter agent."""
    if step < len(STARTER_ACTIONS):
        return STARTER_ACTIONS[step]
    else:
        return "score()"
