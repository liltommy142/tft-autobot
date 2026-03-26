"""
ARCHITECTURE.md - Kiến trúc & Design của TFT Auto-bot
"""

# Architecture Overview

## 🎯 Design Philosophy

**Separation of Concerns**: Tách biệt logic từ data, CLI từ business logic

```
┌─────────────────────────────────────────────────────┐
│              CLI Layer (cli_main.py)                │
│         Input validation, user interaction          │
└──────────────────┬──────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────┐
│           Business Logic (core_engine.py)           │
│  - recommend_comps()                                │
│  - econ_advice()                                    │
│  - recommend_items()                                │
└──────────────────┬──────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────┐
│   Data Models & Persistence Layer                   │
│  - core_models.py (Models with validation)          │
│  - logger.py (JSONL logging)                        │
│  - Data files (data/meta/*.json)                    │
└─────────────────────────────────────────────────────┘
```

## 📦 Module Breakdown

### `config.py` (Configuration Hub)
- Tập trung tất cả constants
- Magic numbers → named constants
- Environment-specific settings

**Why**: Avoid scattered magic numbers, easy tuning

### `core_models.py` (Data Models)
```python
@dataclass
class UnitInstance:
    name: str
    star: int = 1

@dataclass  
class GameState:
    level: int
    gold: int
    hp: int
    round: str
    units: List[UnitInstance]
```

**Design**:
- Simple dataclasses with validation
- `__post_init__` for validation logic
- Immutable design encourages functional style

### `core_engine.py` (Business Logic)

**Comp Scoring Algorithm**:
```
score = (core_units_owned * MULTIPLIER) 
      + (optional_units_owned) 
      - (level_penalty)
      + (meta_score) 
      + (personal_score)
```

**Personal Score**: Calculated from game logs
- Average placement of past games with this comp
- Encourages picking comps player excels at

**Econ Rules** (Priority order):
1. HP ≤ 40 → ROLL
2. Gold ≥ 50 & Level < 8 → LEVEL
3. Otherwise → SAVE

**Item Matching**: 
- Find items where comp's core units are "best_users"
- Pick first core unit that matches

### `cli_main.py` (User Interface)

**Input Processing**:
- Parse CLI input strings
- Validate ranges (level 1-10, placement 1-8, etc.)
- Provide sensible defaults

**Menu System**:
1. Assistant mode - get recommendations
2. Log game mode - record game outcome
3. View logs mode - show game history

### `logger.py` (Persistence)

**Format**: JSONL (JSON Lines)
- One JSON object per line
- Easy to stream/parse
- No database dependency

**Fields**:
- timestamp (auto-added if missing)
- placement (1-8)
- comp_name (optional, for personal score calculation)
- final_board, items (for post-game analysis)

### `fetch_from_riot.py` (External Data Fetch)

**API Integration**:
1. Get summoner via name
2. Get recent match IDs
3. Fetch each match detail
4. Extract player's data
5. Append to logs

**Rate Limiting**:
- 0.13s delay between requests
- 429 (rate limit) handling with exponential backoff

**Error Handling**:
- Graceful degradation (skip bad matches)
- Clear error messages

## 🔄 Data Flow

### Recommendation Flow
```
user_input -> parse_units() -> GameState 
           -> recommend_comps() 
           -> scored & sorted
           -> top 3 returned
```

### Econ Decision Flow
```
GameState -> econ_advice() 
         -> check HP first
         -> check Gold + Level
         -> return ROLL/LEVEL/SAVE
```

### Logging Flow
```
user_input -> parse_game_data() 
          -> validate
          -> log_game() 
          -> append to JSONL
```

## 🧪 Testing Strategy

### Unit Tests
- Test individual functions in isolation
- Mock external data (fixtures)
- Edge cases & error handling

### Types of Tests
```
test_core_models.py
  - GameState validation
  - UnitInstance creation
  - Invalid inputs

test_core_engine.py
  - Econ logic
  - Edge cases
  - Scoring algorithm

test_cli_main.py
  - Input parsing
  - Validation functions
```

### Test Coverage Goal
- Core logic: >85%
- Models: 100%
- CLI: >75%

## 📊 Extensibility Points

### 1. Add New Econ Rules
```python
# In core_engine.py econ_advice()
if your_condition:
    return {"action": "YOUR_ACTION", "reason": "..."}
```

### 2. Add Item Filters
```python
# In core_engine.py recommend_items()
# Add additional filtering logic before returning
```

### 3. Add Meta Sources
```python
# In update_meta.py
def fetch_from_your_source():
    # Fetch data
    # Save as JSON
```

### 4. Add New UI
```python
# Create cli_web.py or cli_discord.py
# Use core_engine functions directly
```

## 🔧 Configuration Tuning

All parameters in `config.py`:

```python
# For more aggressive rolling:
LOW_HP_THRESHOLD = 35  # Roll sooner

# For early leveling:
MIN_LEVEL_TO_LEVEL_UP = 7  # Level sooner

# For stronger preference of meta comps:
PERSONAL_SCORE_MAX = 3.0  # Reduce personal score weight
```

Then run `core_engine` - it uses these automatically.

## 📈 Performance Considerations

**Current**: Fast (sub-100ms for recommendations)

**Optimization opportunities**:
1. Cache comp scores while game continues
2. Pre-compute item mappings
3. Use numpy for batch operations (if scale grows)

## 🔒 Data Validation Strategy

```python
User Input 
    ↓ 
Validate format (parse_units, validate_placement)
    ↓
Create Model (GameState validates ranges)
    ↓
Use in Logic (assumes valid model)
```

Failures at each stage have clear error messages.

## 🚀 Future Architecture Plans

- **v0.3**: Add SQLite for historical analysis
- **v0.4**: Web dashboard with real-time updates
- **v0.5**: ML-based recommendations
- **v1.0**: Mobile app + Discord integration
