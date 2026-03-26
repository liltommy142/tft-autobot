# Project Overview

## Mission

**TFT AutoBot** is an intelligent assistant for Teamfight Tactics (Riot's autobattler). It provides:

1. **Real-time game recommendations** - Comp selection, economic advice, item suggestions
2. **Continuous meta learning** - Automatically learns meta from Grandmaster/Challenger players
3. **Game logging & analysis** - Track your games and analyze performance trends
4. **Modular architecture** - Easy to extend and customize for different playstyles

## Key Features

| Feature | Description | Status |
|---------|-------------|--------|
| **CLI Assistant** | Interactive recommendations during games | ✅ Complete |
| **Meta Learning** | Auto-fetch and analyze high-elo matches | ✅ Complete |
| **Game Logging** | JSONL format for personal game history | ✅ Complete |
| **Riot API Integration** | Direct Riot API for latest meta data | ✅ Complete |
| **Scheduling** | Daemon mode for continuous updates | ✅ Complete |
| **Type Safety** | Full type hints (mypy compatible) | ✅ 85% |
| **Testing** | Unit tests for core modules | ✅ 25+ tests |

## System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    User Interface Layer                  │
├──────────────────┬──────────────────┬──────────────────┤
│  CLI Assistant   │  API Server      │  Web Dashboard   │
│  (main.py)       │  (optional)      │  (future)        │
└──────────────────┴──────────────────┴──────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│                  Business Logic Layer                    │
├──────────────────┬──────────────────┬──────────────────┤
│ Recommendations  │  Meta Learner    │  Data Logger     │
│ (core_engine)    │  (meta_learner)  │  (logger)        │
└──────────────────┴──────────────────┴──────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│                    Data Layer                            │
├──────────────────┬──────────────────┬──────────────────┤
│ Game Models      │  Config          │  JSON Storage    │
│ (core_models)    │  (config.py)     │  (data/meta/)    │
└──────────────────┴──────────────────┴──────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│                Integration Layer                         │
├──────────────────┬──────────────────┬──────────────────┤
│ Riot API         │  Online Sources  │ File System      │
│ (fetch_*.py)     │ (tactics.tools)  │ (data persistence)|
└──────────────────┴──────────────────┴──────────────────┘
```

## Module Dependencies

```
main.py
  └─ src/cli_main.py
     ├─ config.py
     ├─ core_engine.py
     │  ├─ core_models.py
     │  ├─ logger.py
     │  └─ config.py
     └─ core_models.py

learn.py
  └─ src/meta_learner.py
     ├─ config.py
     ├─ core_models.py
     ├─ fetch_from_riot.py
     │  ├─ config.py
     │  └─ logger.py
     └─ logger.py

schedule.py
  └─ src/learner_scheduler.py
     ├─ config.py
     └─ meta_learner.py
```

## How It Works

### Recommendation Flow

```
User Input (Level, Gold, Units)
        ↓
GameState Validation
        ↓
Load Meta Database (comps_meta.json)
        ↓
Score Comps using:
  - Core Unit Matching
  - Meta Score
  - Personal Winrate History
  - Econ Thresholds
        ↓
Recommend Top 3 Comps
        ↓
Suggest Items for Core Units
```

### Meta Learning Flow

```
┌─ MetaPatcher (Check for Patch Updates)
│  └─ TFT-STATUS-V1 API
│
├─ HighEloMatcher (Get Grandmaster Matches)
│  ├─ TFT-LEAGUE-V1 API (Get 20 GM players)
│  ├─ TFT-MATCH-V1 API (Get 5 recent matches each)
│  └─ Raw Match Data
│
├─ MetaAnalyzer (Extract Comp Information)
│  ├─ Parse unit placements
│  ├─ Calculate winrates (top 4)
│  ├─ Extract comp cores
│  └─ Compute meta scores
│
└─ MetaLearner (Update Meta Database)
   ├─ Merge learned comps
   ├─ Update comps_meta.json
   └─ Track patch history
```

## Technology Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| Language | Python | 3.11+ |
| Web Framework | - | - |
| API Client | requests | Latest |
| Data Format | JSON/JSONL | - |
| Type Checking | mypy | 0.950+ |
| Testing | pytest | 7.0+ |
| Code Quality | black, flake8, isort | Latest |
| Database | JSON files | - |

**Future upgrades**: SQLite for scalability, FastAPI for web API

## File Organization

```
src/
├── config.py              # All constants (one source of truth)
├── core_models.py         # GameState, UnitInstance (validated)
├── core_engine.py         # Recommendation logic
├── logger.py              # JSONL output
├── cli_main.py            # Interactive CLI
├── tft_assistant.py       # Alternative interface
├── meta_learner.py        # Core learning engine
├── learner_scheduler.py   # Task scheduling
├── fetch_from_riot.py     # Riot API integration
├── fetch_meta.py          # Online meta sources
└── update_meta.py         # Data initialization

tests/
├── test_core_models.py    # Models validation
└── test_core_engine.py    # Engine logic

docs/
├── INSTALLATION.md        # Setup guide
├── ARCHITECTURE.md        # System design
├── CONTINUOUS_LEARNING.md # Meta learning guide
├── CONTRIBUTING.md        # Contribution guide
└── CHANGES.md             # Changelog
```

## Configuration

All tunable parameters in `src/config.py`:

```python
# Thresholds
LOW_HP_THRESHOLD = 40
HIGH_GOLD_THRESHOLD = 50

# Multipliers
CORE_UNIT_MULTIPLIER = 3
COMP_WIN_RATE_WEIGHT = 1.5

# Learning
LEARNING_INTERVAL_HOURS = 6
NUM_HIGH_ELO_PLAYERS = 20
WINRATE_WEIGHT = 8.0
```

## Performance

- **Recommendation latency**: ~50ms (in-memory lookup)
- **Meta learning cycle**: ~16 seconds (122 API calls)
- **Rate limits**: 0.13s between requests (Riot compliant)
- **Memory usage**: ~20MB typical

## Future Roadmap

### Phase 2 (Next)
- [ ] Web API using FastAPI
- [ ] Multi-region support (NA, EUW, KR)
- [ ] Item meta learning
- [ ] Real-time spectator analysis

### Phase 3 (Later)
- [ ] Machine learning-based scoring
- [ ] Temporal meta analysis (patch trends)
- [ ] Mobile app companion
- [ ] Community meta sharing

## Contributing

See [docs/CONTRIBUTING.md](CONTRIBUTING.md) for:
- Development setup
- Code style guidelines
- Testing requirements
- Pull request process

## Support

- 📖 Documentation: See `docs/` folder
- 🐛 Issues: GitHub Issues
- 💬 Discussions: GitHub Discussions

## License

MIT License - See LICENSE file

## Acknowledgments

- Riot Games for TFT and the public API
- tft-data.json community projects
- Tactics.tools for meta references
