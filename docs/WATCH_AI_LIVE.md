# Tester l'IA en Direct avec Visualisation

Tu es connecté au serveur FLE via Factorio Steam ! 🎮

## Lancer un run et voir l'IA jouer

Dans un terminal (garde Factorio ouvert) :

```bash
cd /Users/nicolaspiron/NextTread/factorio-ai-lab
source .venv/bin/activate

# Run de 20 steps pour voir l'activité
falab run --mode fle --config configs/fle_test.yaml
```

**Dans Factorio**, tu verras en temps réel :
- Les commandes Python exécutées
- Les actions de l'IA
- L'état du jeu qui change

## Modifier le nombre de steps

Pour voir plus d'actions, édite `configs/fle_test.yaml` :

```yaml
run:
  name: "fle-demo"
  max_steps: 50    # Change ici pour plus de steps
  seed: 42
```

## Debug en direct

Pendant que l'IA tourne, tu peux :
- Observer dans Factorio ce qui se passe
- Voir les logs dans le terminal
- Vérifier les JSONL dans `runs/` après

## Commandes utiles

```bash
# Run simple
falab run --mode fle

# Run plus long
# (édite configs/fle_test.yaml pour max_steps: 100)
falab run --mode fle --config configs/fle_test.yaml

# Voir les logs du serveur
docker logs -f fle-factorio_0-1
```

## Note importante

Pour l'instant, l'agent fait un simple `print("Step X")` - tu ne verras pas beaucoup d'action car c'est juste un agent de test.

Pour voir de vraies actions Factorio, il faudra implémenter un agent qui utilise l'API FLE pour construire/placer des entités !
