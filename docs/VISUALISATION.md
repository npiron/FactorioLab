# Visualiser Factorio FLE

Le serveur FLE tourne en mode **headless** (sans interface graphique) pour des raisons de performance. Voici tes options pour visualiser ce qui se passe :

## Option 1: Logs Docker en temps réel

Voir ce que fait le serveur via les logs :

```bash
# Logs en direct
docker logs -f fle-factorio_0-1

# Dernières 50 lignes
docker logs fle-factorio_0-1 --tail 50
```

## Option 2: Connecter un client Factorio (Recommandé)

Si tu as Factorio installé sur ta machine :

1. **Lancer Factorio**
2. **Menu principal → Multijoueur**
3. **Se connecter à l'adresse:**
   - Adresse: `localhost`
   - Port: `34197` (du conteneur Docker)

Le serveur FLE accepte les connexions multijoueur !

## Option 3: FLE avec rendu (non-headless)

Pour avoir le rendu graphique via FLE :

```bash
# Arrêter cluster headless actuel
fle cluster stop

# Redémarrer avec rendu (nécessite Factorio installé)
# Note: plus lent mais visuel
fle cluster start -n 1 --render
```

**Attention:** Le mode rendu nécessite :
- Factorio v1.1.110 installé localement
- Beaucoup plus de ressources
- Moins performant pour l'entraînement

## Option 4: Screenshots via FLE API

Programmer des screenshots depuis ton agent :

```python
# Dans ton code agent
screenshot = instance.screenshot()
# Sauvegarder l'image
```

## Recommandation

Pour **vérifier que tout marche** :
1. Utilise `docker logs -f fle-factorio_0-1` pour voir l'activité
2. Si tu veux vraiment voir le jeu, installe Factorio et connecte-toi en multijoueur

Pour **développer ton agent** :
- Reste en headless (plus rapide)
- Utilise les logs JSONL pour debug
- Screenshots ponctuels si besoin

## Vérification rapide

Vérifions que le serveur répond :

```bash
# Status du serveur
docker ps | grep factorio

# Dernière activité
docker logs fle-factorio_0-1 --tail 20
```
