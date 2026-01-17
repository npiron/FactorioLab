# 🚀 Fine-Tuning Mistral 7B sur Mac M1 Pro

Guide complet pour entraîner ton propre modèle Factorio sur Apple Silicon

---

## 📋 Table des Matières

1. [Prérequis](#prérequis)
2. [Installation MLX](#installation-mlx)
3. [Téléchargement Mistral 7B](#téléchargement-mistral-7b)
4. [Préparation du Dataset](#préparation-du-dataset)
5. [Fine-Tuning](#fine-tuning)
6. [Utilisation](#utilisation)
7. [Troubleshooting](#troubleshooting)

---

## Prérequis

### Matériel
- ✅ Mac M1 Pro avec **32GB RAM** (EXCELLENT!)
- ✅ ~20GB espace disque libre (30GB recommandé)
- ✅ macOS 13+ (Ventura ou plus récent)

**Avec 32GB, tu peux** :
- ✅ Utiliser Mistral 7B version COMPLÈTE (non-quantized) → Meilleure qualité
- ✅ Batch size 4-8 → Training 2-3x plus rapide
- ✅ Fine-tuner plus de layers → Meilleurs résultats
- 🚀 Même entraîner Mixtral 8x7B si tu veux (70B params total!)

### Logiciels
- Python 3.11+ ✅ (tu l'as déjà)
- `pip` mis à jour

### Coût
- **$0** (100% gratuit, juste électricité)
- Temps: **3-6h** de training (avec batch_size=8, 2x plus rapide que 16GB)

---

## Installation MLX

### Étape 1 : Créer environnement dédié

```bash
cd /Users/nicolaspiron/NextTread/factorio-ai-lab

# Créer nouvel environnement pour MLX
python3.11 -m venv .venv-mlx
source .venv-mlx/bin/activate

# Mise à jour pip
pip install --upgrade pip
```

### Étape 2 : Installer MLX

```bash
# MLX: Framework Apple Silicon optimisé
pip install mlx mlx-lm

# Dépendances training
pip install numpy tqdm datasets transformers

# Validation
python -c "import mlx.core as mx; print(mx.__version__)"
# Devrait afficher : 0.x.x
```

> **Note**: MLX utilise le GPU du M1 Pro automatiquement via Metal - aucune config CUDA nécessaire !

---

## Téléchargement Mistral 7B

### Option A : Version 4-bit Quantized (Rapide)

**Avantages** :
- Taille: 4GB au lieu de 14GB
- Vitesse: 2x plus rapide
- RAM: 8GB au lieu de 16GB
- Qualité: ~95% de l'original

```bash
# Installation
pip install huggingface_hub

# Téléchargement (15-30 min)
python3 << EOF
from huggingface_hub import snapshot_download

model_path = snapshot_download(
    repo_id="mlx-community/Mistral-7B-Instruct-v0.3-4bit",
    local_dir="./models/mistral-7b-4bit"
)
print(f"✅ Modèle téléchargé: {model_path}")
EOF
```

### Option B : Version Complète (RECOMMANDÉ pour 32GB!) 🚀

**Avantages avec 32GB RAM** :
- Qualité: 100% (meilleure que 4-bit)
- Fine-tuning plus précis
- Meilleurs résultats finaux
- Training à peine plus lent

```bash
python3 << EOF
from huggingface_hub import snapshot_download

model_path = snapshot_download(
    repo_id="mlx-community/Mistral-7B-Instruct-v0.3",
    local_dir="./models/mistral-7b-full"
)
print(f"✅ Modèle téléchargé: {model_path}")
EOF
```

### Option C : Mixtral 8x7B (Si tu veux le TOP!) 🔥

**Pour les aventuriers avec 32GB** :
- 8 "experts" de 7B chacun
- Qualité proche GPT-4
- Plus lent mais meilleur

```bash
python3 << EOF
from huggingface_hub import snapshot_download

model_path = snapshot_download(
    repo_id="mlx-community/Mixtral-8x7B-Instruct-v0.1-4bit",
    local_dir="./models/mixtral-8x7b-4bit"
)
print(f"✅ Modèle téléchargé: {model_path}")
EOF
```

> **Recommandation pour 32GB** : Option B (Mistral 7B full) = meilleur compromis qualité/vitesse

**Test du modèle** :

```bash
python3 << EOF
from mlx_lm import load, generate

model, tokenizer = load("./models/mistral-7b-4bit")
response = generate(
    model, 
    tokenizer, 
    prompt="How do I craft a stone furnace in Factorio?",
    max_tokens=100
)
print(response)
EOF
```

---

## Préparation du Dataset

### Étape 1 : Extraire les runs existants

On va convertir tes runs GPT-4o en dataset d'entraînement !

```bash
# Créer dossier dataset
mkdir -p training_data
```

Créer `scripts/prepare_dataset.py` :

```python
"""
Convertit les runs Factorio en dataset pour fine-tuning
"""
import json
import glob
from pathlib import Path

def extract_successful_actions(run_file):
    """Extrait actions réussies d'un run"""
    with open(run_file) as f:
        steps = [json.loads(line) for line in f]
    
    examples = []
    for step in steps:
        # Garder seulement les steps réussis
        if step.get('stderr', ''):
            continue  # Skip erreurs
            
        code = step.get('code', '')
        stdout = step.get('stdout', '')
        
        if code and stdout:
            examples.append({
                "instruction": "Generate Factorio code for the next action.",
                "input": f"Previous output: {stdout}",
                "output": code
            })
    
    return examples

# Extraire de tous les runs
all_examples = []
for run_file in glob.glob("runs/*.jsonl"):
    print(f"Processing {run_file}...")
    examples = extract_successful_actions(run_file)
    all_examples.extend(examples)
    print(f"  → {len(examples)} examples")

print(f"\n✅ Total: {len(all_examples)} training examples")

# Sauvegarder dataset
with open("training_data/factorio_dataset.jsonl", "w") as f:
    for ex in all_examples:
        f.write(json.dumps(ex) + "\n")

print(f"✅ Dataset saved: training_data/factorio_dataset.jsonl")
```

**Exécuter** :

```bash
python scripts/prepare_dataset.py
```

### Étape 2 : Augmenter le dataset

Ajouter des exemples manuels basés sur `starter_agent.py` qui marche :

```bash
cat > training_data/manual_examples.jsonl << 'EOF'
{"instruction": "Harvest stone in Factorio", "input": "Need 5 stone", "output": "stone_pos = nearest(Resource.Stone)\nmove_to(stone_pos)\nharvest_resource(stone_pos, quantity=5)\nprint('Harvested stone')"}
{"instruction": "Craft stone furnace", "input": "Have 5 stone in inventory", "output": "crafted = craft_item(Prototype.StoneFurnace, quantity=1)\nprint(f'Crafted {crafted} furnace')"}
{"instruction": "Place stone furnace", "input": "Have furnace in inventory", "output": "furnace = place_entity(\n    entity=Prototype.StoneFurnace,\n    position=Position(x=0, y=2),\n    direction=Direction.UP\n)\nprint(f'Placed furnace at {furnace.position}')"}
{"instruction": "Insert coal into furnace", "input": "Have furnace and coal", "output": "insert_item(Prototype.Coal, furnace, quantity=10)\nprint('Inserted coal')"}
EOF

# Combiner datasets
cat training_data/factorio_dataset.jsonl training_data/manual_examples.jsonl > training_data/combined.jsonl
```

---

## Fine-Tuning

### Étape 1 : Configurer le training

Créer `train_config.yaml` :

```yaml
# Configuration MLX Fine-tuning - OPTIMISÉ 32GB RAM
model: ./models/mistral-7b-full  # Full precision!
data: ./training_data/combined.jsonl
train: true
seed: 42

# Hyperparamètres optimisés M1 Pro 32GB
lora_layers: 32          # Plus de layers (32GB permet ça!)
batch_size: 8            # Gros batch = training plus rapide
iters: 1000              # Nombre d'itérations
steps_per_eval: 100      # Évaluation tous les 100 steps
learning_rate: 1e-4
val_batches: 10

# LoRA config (efficient fine-tuning)
lora_parameters:
  rank: 16               # Plus haut pour 32GB
  alpha: 32
  dropout: 0.05
  
# Sortie
adapter_file: ./adapters/factorio-mistral-lora
```

### Étape 2 : Lancer le training

```bash
# Activer env
source .venv-mlx/bin/activate

# Créer dossier adapters
mkdir -p adapters

# Lancer fine-tuning (6-12h)
python -m mlx_lm.lora \
    --model ./models/mistral-7b-4bit \
    --data ./training_data/combined.jsonl \
    --train \
    --iters 1000 \
    --steps-per-eval 100 \
    --adapter-file ./adapters/factorio-mistral-lora \
    --batch-size 2 \
    --lora-layers 16

# OU avec config file:
# python -m mlx_lm.lora --config train_config.yaml
```

**Monitoring** :

```bash
# Dans un autre terminal
watch -n 10 'tail -20 mlx_lm.log'
```

**Temps estimés sur M1 Pro 32GB** :
- 500 examples: **2-3h** (batch_size=8)
- 1000 examples: **4-6h** (2x plus rapide que 16GB!)
- 2000 examples: **8-12h**

> **Astuce**: Lance overnight, ça consomme peu (<30W)

---

## Utilisation

### Test rapide

```python
from mlx_lm import load, generate

# Charger modèle + adapter fine-tuné
model, tokenizer = load(
    "./models/mistral-7b-4bit",
    adapter_file="./adapters/factorio-mistral-lora"
)

# Test
prompt = """Generate Factorio code to:
1. Harvest 50 iron ore
2. Smelt it into plates

Code:"""

response = generate(
    model, 
    tokenizer, 
    prompt=prompt,
    max_tokens=200,
    temp=0.3
)

print(response)
```

### Intégration avec FLE

Créer `local_mistral_agent.py` :

```python
"""
Agent Factorio qui utilise Mistral 7B fine-tuné localement
"""
from mlx_lm import load, generate
from factorio_ai_lab.env_adapter import FleEnv

print("🤖 Loading Mistral 7B (local, fine-tuned)")
model, tokenizer = load(
    "./models/mistral-7b-4bit",
    adapter_file="./adapters/factorio-mistral-lora"
)
print("✅ Model ready\n")

env = FleEnv()
obs = env.reset()

for step in range(50):
    print(f"\n{'='*60}")
    print(f"STEP {step}")
    print(f"{'='*60}")
    
    prompt = f"""Generate Python code for next Factorio action.

Previous output: {obs.stdout[-200:] if obs.stdout else 'Starting'}
Previous error: {obs.stderr[-100:] if obs.stderr else 'None'}

Next action (Python code only):
"""
    
    # Générer avec ton modèle local (GRATUIT!)
    code = generate(
        model,
        tokenizer, 
        prompt=prompt,
        max_tokens=150,
        temp=0.2
    )
    
    # Nettoyer
    if "```python" in code:
        code = code.split("```python")[1].split("```")[0]
    
    print(f"\n💻 {code[:100]}...\n")
    
    # Exécuter
    obs = env.step(code)
    print(f"📊 {obs.stdout[:150] if obs.stdout else obs.stderr[:150]}")

env.close()
print("\n✅ Done! (And it was FREE! 🎉)")
```

**Lancer** :

```bash
python local_mistral_agent.py
```

---

## Troubleshooting

### Erreur : "Out of memory"

**Solution 1** : Réduire batch size

```yaml
batch_size: 1  # Au lieu de 2
```

**Solution 2** : Utiliser moins de layers

```yaml
lora_layers: 8  # Au lieu de 16
```

### Erreur : "Model not found"

```bash
# Vérifier le chemin
ls -la models/mistral-7b-4bit/

# Re-télécharger si nécessaire
rm -rf models/mistral-7b-4bit
python -m huggingface_hub download mlx-community/Mistral-7B-Instruct-v0.3-4bit
```

### Training trop lent

**Vérifier GPU usage** :

```bash
# Installer powermetrics
sudo powermetrics --samplers gpu_power -i 1000

# Devrait montrer GPU actif pendant training
```

**Augmenter batch size** (si RAM ok) :

```yaml
batch_size: 4  # Plus rapide
```

### Qualité insuffisante après training

**Plus d'itérations** :

```yaml
iters: 2000  # Au lieu de 1000
```

**Learning rate plus faible** :

```yaml
learning_rate: 5e-5  # Au lieu de 1e-4
```

---

## 📊 Résultats Attendus

### Après 1000 iterations

**Capacités** :
- ✅ Harvest resources correctement
- ✅ Craft items simples
- ✅ Place entities avec bons params
- ⚠️ Planning complexe limité

**Performance** :
- Production Score: 35-45 (vs 30 pour GPT-4o-mini vanilla)
- Success rate: 60-70%

### Après 2000 iterations

**Capacités** :
- ✅ Workflows complets (harvest → craft → place)
- ✅ Gestion d'erreurs basique
- ✅ Multi-step planning
- ⚠️ Optimisation UPS limitée

**Performance** :
- Production Score: 45-55
- Success rate: 70-80%

### Comparaison

| Modèle | PS | Coût/run | Notes |
|--------|-------|----------|-------|
| Mistral 7B fine-tuné | 45-55 | **$0** | Local, gratuit après training |
| GPT-4o-mini | 30-40 | $0.50 | Cloud, toujours payant |
| GPT-4o | 70-80 | $15 | Cloud, cher |
| Claude 3.5 | 86 | $50 | Cloud, très cher |

---

## 🎯 Next Steps

### Améliorer le modèle

1. **Collecter plus de runs** :
   ```bash
   # Faire tourner GPT-4o plusieurs fois
   python gpt4o_fullpower.py
   # Extraire succès → Dataset
   ```

2. **Ajouter exemples négatifs** :
   ```jsonl
   {"instruction": "Avoid this", "input": "Error: too far", "output": "# FIX: move_to() first"}
   ```

3. **Re-train avec plus de data** :
   ```bash
   python -m mlx_lm.lora --iters 3000
   ```

### Setup Hybride (Recommandé)

```python
# Utiliser Mistral local (gratuit) + GPT-4o fallback

if task_complexity < 5:
    code = local_mistral.generate()  # 90% des cas, $0
else:
    code = gpt4o.generate()  # 10% des cas, payant
```

---

## 📚 Ressources

- [MLX Documentation](https://ml-explore.github.io/mlx/)
- [Mistral AI](https://mistral.ai/)
- [LoRA Paper](https://arxiv.org/abs/2106.09685)
- [Factorio Wiki](https://wiki.factorio.com/)

---

**Créé le** : 2026-01-01  
**Pour** : M1 Pro (16GB RAM)  
**Budget** : $0 (gratuit!)  
**Temps** : 6-12h training initial

**Bon training ! 🚀**
