# Pourquoi tu ne vois peut-être rien

## Raisons possibles

### 1. Les actions sont trop rapides
L'agent exécute les 15 actions en quelques secondes. Si tu ne regardais pas au bon moment, tu as manqué.

### 2. Le joueur se déplace
L'IA contrôle un personnage dans le jeu. Si tu ne regardes pas où il est, tu ne verras pas les actions.

### 3. Erreurs silencieuses
Les commandes FLE peuvent échouer sans message d'erreur visible.

## Solutions pour mieux voir

### Option 1: Ralentir l'agent
Ajoute des pauses entre les actions :

```python
# Dans demo_agent.py, ajoute "sleep(120)" entre chaque action
```

### Option 2: Actions plus visibles
Utilise des actions qui créent des choses massives :

```python
# Placer plein de choses
for i in range(10):
    place_entity('stone-wall', position=Position(i, 0))
```

### Option 3: Suivre le personnage
Dans Factorio:
1. Active le mode **spectateur libre** (touche Tab)
2. Cherche le personnage "player"  
3. Garde la caméra sur lui

### Option 4: Vérifier après coup
Regarde dans Factorio si des choses ont changé:
- Y a-t-il une foreuse quelque part?
- Un four?
- Des items dans l'inventaire?

## Test Simple

Essayons une action ultra-visible :

```bash
# Je vais créer un agent qui place 100 murs
# Tu ne pourras pas le rater!
```
