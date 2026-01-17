# Factorio AI Lab 🏭

An AI agent framework for playing Factorio using the [Factorio Learning Environment (FLE)](https://github.com/JackHopkins/FactorioLearningEnvironment).

## 📁 Project Structure

```
factorio-ai-lab/
├── src/factorio_ai_lab/          # Main Python package
│   ├── agents/                   # AI agents
│   │   └── megabase_learning_agent.py  # Main self-learning agent
│   ├── prompts/                  # LLM prompts
│   ├── cli.py                    # CLI entry point
│   ├── env_adapter.py            # FLE environment adapter
│   └── runner.py                 # Episode runner
├── configs/                      # YAML configurations
├── scripts/                      # Utility scripts
│   ├── bootstrap.py              # Initialize knowledge base
│   ├── check_fle.py              # Verify FLE connection
│   ├── view_knowledge.py         # Inspect knowledge base
│   └── ...
├── docs/                         # Documentation
│   ├── FLE_docs.md               # FLE API reference (92KB)
│   ├── SETUP_LLM.md              # LLM setup guide
│   └── reference/                # Research papers (PDFs)
├── data/                         # Generated data (gitignored)
│   ├── knowledge/                # Knowledge base files
│   ├── logs/                     # Run logs
│   └── screenshots/              # Game screenshots
├── tests/                        # Test suite
└── runs/                         # Episode run logs
```

## 🚀 Quick Start

### 1. Setup Environment

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

### 2. Configure API Keys

```bash
cp .env.example .env
# Edit .env with your OpenAI/Anthropic API keys
```

### 3. Start FLE Server

```bash
fle cluster start
```

### 4. Run the Agent

```bash
# Using CLI
falab run --config configs/default.yaml

# Or run the main agent directly
python -m factorio_ai_lab.agents.megabase_learning_agent
```

## 🤖 Agent Types

### Megabase Learning Agent (Recommended)
Self-learning agent with persistent knowledge base and curriculum learning:
- Automatically saves successful patterns
- Progress through 5 curriculum phases
- Uses OpenAI GPT-4 or GPT-4o-mini

```bash
python -m factorio_ai_lab.agents.megabase_learning_agent
```

## 📊 Curriculum Phases

1. **Phase 1**: Early Game (mining → smelting → green circuits)
2. **Phase 2**: Mid Game (oil/plastics/red circuits)
3. **Phase 3**: Open Play (roboports + rails + modules)
4. **Phase 4**: Modular Bases (stampable blueprints)
5. **Phase 5**: UPS Optimization (entity reduction)

## 🛠️ Useful Scripts

```bash
# Check FLE connection
python scripts/check_fle.py

# Bootstrap initial knowledge
python scripts/bootstrap.py

# View knowledge base
python scripts/view_knowledge.py

# Take screenshots (observer mode)
python scripts/observer_mode.py
```

## 📚 Documentation

- [FLE API Reference](docs/FLE_docs.md) - Complete API documentation
- [LLM Setup Guide](docs/SETUP_LLM.md) - Configure OpenAI/Anthropic
- [FLE Installation](docs/FLE_INSTALLATION.md) - Install Factorio Learning Environment

## 🔬 Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Lint code
ruff check .
mypy src/

# Pre-commit hooks
pre-commit install
```

## 📖 References

- [FLE (Factorio Learning Environment)](https://github.com/JackHopkins/FactorioLearningEnvironment)
- [Automatic Design of Factorio Blueprints](https://arxiv.org/abs/2403.16663)
- [AI Agents for System Engineering in Factorio](https://arxiv.org/abs/2503.00123)

## 📄 License

MIT
