# 🤖 Setup Agent LLM pour Factorio

## 📋 Checklist Rapide

### 1. Obtenir une Clé API

**Option A : OpenAI (Recommandé pour commencer)**
- Aller sur https://platform.openai.com/api-keys
- Créer une nouvelle clé API
- Coût estimé : ~$0.10-$0.50 pour un test (GPT-4o-mini)

**Option B : Anthropic (Claude)**
- Aller sur https://console.anthropic.com/
- Créer une clé API
- Coût estimé : ~$1-2 pour un test (Claude 3.5 Sonnet)

### 2. Configurer le Projet

```bash
# Copier le template
cp .env.example .env

# Éditer .env et ajouter ta clé
# OPENAI_API_KEY=sk-proj-...
```

### 3. Installer les Dépendances d'Évaluation

```bash
source .venv/bin/activate
pip install 'factorio-learning-environment[eval]'
```

### 4. Lancer le Premier Test

```bash
# Démarrer le serveur Factorio
fle cluster start

# Lancer l'évaluation LLM
fle eval --config configs/llm_test.json
```

## 🎮 Que Va-t-il Se Passer ?

L'agent LLM va :
1. Se connecter au serveur Factorio
2. Lire l'objectif : "Produire du minerai de fer"
3. **Générer du code Python** à chaque step
4. Exécuter ce code dans Factorio
5. Observer les résultats
6. Décider de la prochaine action
7. Répéter pendant 50 steps

## 📊 Configs Disponibles

### `llm_test.json` - Test Simple
- Modèle : GPT-4o-mini ($)
- Tâche : iron_ore_throughput
- Steps : 50
- **Coût estimé : $0.10-0.30**

### Pour Plus Tard

Créer `configs/llm_advanced.json` :
```json
{
  "model": "gpt-4o",
  "task": "automation_science_pack_throughput",
  "max_steps": 128,
  "num_runs": 1
}
```

## 🐛 Troubleshooting

**Erreur : "No API key found"**
→ Vérifier que `.env` contient `OPENAI_API_KEY=sk-...`

**Erreur : "Cluster not running"**
→ Lancer `fle cluster start` d'abord

**Erreur : "Module eval not found"**
→ Installer : `pip install 'factorio-learning-environment[eval]'`

## 📈 Analyser les Résultats

Les logs seront dans :
- Console : logs en temps réel
- Fichiers : trajectoires sauvegardées (si configuré)

Chercher dans les logs :
- `Step X:` - Code généré par le LLM
- `Output:` - Résultat dans Factorio
- `Error:` - Erreurs de l'agent

## 🎯 Prochaines Étapes

Une fois le test réussi :
1. Essayer une tâche plus complexe
2. Tester avec Claude (plus performant)
3. Analyser comment l'IA raisonne
4. Construire ton propre agent custom !
