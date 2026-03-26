# Quick Start Guide

## ⚡ Installation

```bash
# 1. Clone repository
cd tft-autobot

# 2. Create virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
# or: source .venv/bin/activate  # Linux/Mac

# 3. Install dependencies
pip install -r requirements.txt
```

## 🚀 Entry Points

All scripts can be run from the **repository root**.

### CLI Assistant
```bash
python main.py
```
Interactive recommendations: comp selection, econ advice, item suggestions.

### Initialize / Update Metadata
```bash
python update_meta.py
```
Creates `data/meta/` with sample composition and item data.

### Fetch Metadata from Online Sources
```bash
python fetch_meta.py
```
Fetches meta from Riot Data Dragon and tactics.tools.

### Fetch Player Match History (requires Riot API key)
```bash
# Set up .env first:
# RIOT_API_KEY=your-key-here

python fetch_from_riot.py "SummonerName" vn1    # Specific platform
python fetch_from_riot.py "SummonerName"        # Auto-detect platform
```
Fetches recent matches and appends to `logs/games.jsonl`.

### Meta Learner - Learn from High-Elo Players
```bash
python learn.py
```
Analyzes Grandmaster/Challenger matches to update meta database.

### Meta Scheduler - Automate Learning
```bash
# Run meta learning once
python schedule.py once

# Dry-run without updating
python schedule.py test

# Continuous daemon (checks every 60s, learns every 6 hours)
python schedule.py daemon 6 60
```

## 📁 Project Structure

```
src/           # Core modules
tests/         # Unit tests (pytest)
docs/          # Documentation
scripts/       # Utility scripts
data/meta/     # Metadata (auto-created)
logs/          # Game logs (auto-created)
```

## ✅ Verify Installation

```bash
# Test imports
python -c "from src.core_models import GameState; print('✓ Installation OK')"

# Run tests (requires pytest)
pytest tests/ -v
```

## 🔧 Common Issues

### Issue: `ModuleNotFoundError: requests`

**Solution:**
```bash
pip install -r requirements.txt
```

### Issue: `RIOT_API_KEY not set`

**Solution:**
```bash
cp .env.example .env
# Edit .env with your API key from https://developer.riotgames.com/
```

### Issue: Files not found when running scripts

**Solution:** Always run from repository root:
```bash
cd d:/GitHub/tft-autobot
python main.py  # ✓ Correct
```

## 📚 Documentation

- **Getting Started**: See [docs/INSTALLATION.md](docs/INSTALLATION.md)
- **How to Use**: See [README.md](README.md)
- **System Design**: See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- **Meta Learning Setup**: See [docs/CONTINUOUS_LEARNING.md](docs/CONTINUOUS_LEARNING.md)
- **Contributing**: See [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md)

## 🎯 Next Steps

1. **Run the assistant**
   ```bash
   python main.py
   ```

2. **Initialize metadata** (if not done)
   ```bash
   python update_meta.py
   ```

3. **Start meta learning** (requires Riot API key)
   ```bash
   python learn.py
   ```

4. **Schedule continuous updates**
   ```bash
   python schedule.py daemon 6 60
   ```

## 📊 Project Status

- ✅ CLI Assistant fully functional
- ✅ Meta learning engine functional
- ✅ Riot API integration ready
- ✅ Scheduling system ready
- ✅ Type hints (85%)
- ✅ Unit tests (25+)
- ✅ Documentation complete
- ✅ Professional structure

**Status: Production Ready** 🎯
