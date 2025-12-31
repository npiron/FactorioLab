## Check FLE

Pour vérifier si FLE est installé et fonctionnel :

```bash
./scripts/check_fle.sh
```

Sur Windows:

```bash
python scripts/check_fle.py
```

## Installation FLE

FLE nécessite:
- Python 3.10+ ✅ (tu as 3.11.3)
- Docker (pour le serveur Factorio headless)
- Factorio version 1.1.110 (licence requise pour le rendering optionnel)

### Installation du package Python

```bash
# Activer venv
source .venv/bin/activate

# Installation de base
pip install factorio-learning-environment

# Ou avec fonctionnalités complètes (recommandé pour les expérimentations)
pip install factorio-learning-environment[eval,mcp,psql]
```

### Vérification post-installation

Après installation, relance le script de vérification :

```bash
./scripts/check_fle.sh
```

Le script devrait afficher `PASS` si FLE est correctement installé.
