# factorio-ai-lab

Harness pour expérimenter un agent Factorio (FLE), avec:
- CLI `falab`
- configs YAML
- logs run en JSONL
- CI (ruff/mypy/pytest)

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pre-commit install
```

## Smoke test (sans Factorio)

```bash
falab run --config configs/default.yaml
pytest -q
```

## Next

Intégrer FLE:
- connecter env.step(...)
- log reward/PS/milestones
- brancher prompt + mémoire

## Architecture

### Curriculum de tâches

Le projet suit une progression en 5 phases inspirée du guide megabase:

1. **Phase 1**: lab-play "early" (mining → smelting → green circuits)
2. **Phase 2**: lab-play "mid" (oil/plastics/red circuits)
3. **Phase 3**: open-play avec objectifs internes (bootstrap roboports + rails + modules)
4. **Phase 4**: bases modulaires "stampables"
5. **Phase 5**: optimisation UPS-aware (refactor + réduction entités)

### Métriques Megabase

Le score composite `MegabaseScore` combine:
- `log(PS)` - croissance de Production Score
- `milestones_weighted` - progression tech-tree
- `SPM_estimate` - Science Packs par Minute
- Pénalités: `EntityCost`, `InserterActivityCost`, `BalancerPenalty`, `PowerWastePenalty`

### Heuristiques UPS-friendly

- Minimiser entités/inserters/machines
- Éviter balancers inutiles
- Préférer "sleep" des machines via back-pressure
- Mining direct into wagon
- Clock des inserters pour swings pleins (12 items)

## Références

- [FLE (Factorio Learning Environment)](https://github.com/JackHopkins/FactorioLearningEnvironment)
- [Automatic Design of Factorio Blueprints](https://arxiv.org/abs/2403.16663)
- [AI Agents for System Engineering in Factorio](https://arxiv.org/abs/2503.00123)
- [Guide megabase Reddit](https://www.reddit.com/r/factorio/comments/kef2tn/guide_building_a_megabase_in_phases/)
- [Thread UPS Factorio forum](https://forums.factorio.com/viewtopic.php?t=82134)
