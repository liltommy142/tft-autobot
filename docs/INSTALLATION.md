# Installation Guide

## Prerequisites

- Python 3.11 or higher
- pip (Python package manager)
- Riot API key (get from https://developer.riotgames.com/)

## Setup Steps

### 1. Clone Repository

```bash
git clone https://github.com/yourusername/tft-autobot.git
cd tft-autobot
```

### 2. Create Virtual Environment

**Windows (PowerShell):**
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

**Linux/macOS:**
```bash
python -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
# Basic installation
pip install -r requirements.txt

# With development tools (linting, testing)
pip install -r requirements.txt -r dev-requirements.txt

# Or as package (optional)
pip install -e .
```

### 4. Configure Environment

```bash
# Copy example config
cp .env.example .env

# Edit .env and add your Riot API key
# Windows:
notepad .env

# Linux/macOS:
nano .env
```

Your `.env` file should look like:
```
RIOT_API_KEY=RGAPI-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

### 5. Initialize Meta Data

```bash
# Create initial metadata
python src/update_meta.py

# Or fetch from online sources
python src/fetch_meta.py
```

## Verify Installation

```bash
# Test imports
python -c "from src.core_models import GameState; print('✓ Installation successful')"

# Run tests
pytest -v tests/
```

## Quick Start

### Option 1: CLI Assistant

```bash
python main.py
```

### Option 2: Meta Learner

```bash
# Run once
python learn.py

# Run as daemon (every 6 hours)
python schedule.py daemon 6 60
```

## Troubleshooting

### Issue: `ModuleNotFoundError: No module named 'src'`

**Solution:** Make sure you're running from repository root:
```bash
cd /path/to/tft-autobot
python main.py  # ✓ Correct
python src/cli_main.py  # ✗ Wrong
```

### Issue: `RIOT_API_KEY not set`

**Solution:** Create `.env` file with your API key:
```bash
cp .env.example .env
# Edit .env with your actual API key
```

### Issue: `No module named 'requests'`

**Solution:** Install dependencies:
```bash
pip install -r requirements.txt
```

### Issue: Pytest can't find modules

**Solution:** Pytest is configured in `pytest.ini`. Run from repository root:
```bash
pytest -v tests/
```

## Getting Riot API Key

1. Go to https://developer.riotgames.com/
2. Sign in or create account
3. Create an API key
4. Add to `.env` file

**Note:** Free API keys have rate limits. See [docs/CONTINUOUS_LEARNING.md](CONTINUOUS_LEARNING.md) for rate limit handling.

## Uninstall

```bash
# Deactivate virtual environment
deactivate

# Remove virtual environment
# Windows: rmdir /s .venv
# Linux/macOS: rm -rf .venv

# Or remove installed package
pip uninstall tft-autobot
```

## Next Steps

- Read [README.md](../README.md) for usage
- See [docs/ARCHITECTURE.md](ARCHITECTURE.md) for system design
- Check [docs/CONTINUOUS_LEARNING.md](CONTINUOUS_LEARNING.md) for meta learning setup
- Review [docs/CONTRIBUTING.md](CONTRIBUTING.md) to contribute
