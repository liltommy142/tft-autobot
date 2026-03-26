"""
CONTINUOUS_LEARNING.md - Auto Meta Learning System Documentation
"""

# Continuous Meta Learning System

## 🎯 Overview

TFT Auto-bot now has a **continuous learning system** that automatically:

1. **Monitors patch updates** - Detects when new patches roll out
2. **Crawls high-level matches** - Fetches data from Challenger/Grandmaster players
3. **Analyzes meta shifts** - Calculates comp winrates from real match data
4. **Auto-updates database** - Updates `comps_meta.json` with learned meta
5. **Tracks historical meta** - Maintains meta version history

**Result**: Meta database stays fresh and accurate without manual updates!

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────┐
│        Learner Scheduler (learner_scheduler.py)      │
│  - Continuous daemon or cron-scheduled task         │
│  - Monitors interval and patch updates              │
└───────────────────┬─────────────────────────────────┘
                    │
┌───────────────────▼─────────────────────────────────┐
│        Meta Learner (meta_learner.py)                │
│  - Checks for patch updates (TFT-STATUS-V1)        │
│  - Crawls Grandmaster matches (TFT-LEAGUE-V1)      │
│  - Fetches match details (TFT-MATCH-V1)            │
│  - Analyzes comp winrates                           │
│  - Updates comps_meta.json                          │
└───────────────────┬─────────────────────────────────┘
                    │
┌───────────────────▼─────────────────────────────────┐
│     Riot Game APIs (developer.riotgames.com)        │
│  - TFT-STATUS-V1: Check patch version              │
│  - TFT-LEAGUE-V1: Get top players                  │
│  - TFT-MATCH-V1: Fetch match data                  │
└─────────────────────────────────────────────────────┘
```

---

## 🔧 Components

### 1. **meta_learner.py** - Core Learning Engine

**Classes:**

- **MetaPatcher**: Track and detect patch updates
  ```python
  MetaPatcher.get_current_patch()      # Get current patch from API
  MetaPatcher.is_patch_updated()       # Check if patch changed
  MetaPatcher.save_patch_info()        # Save patch + meta version
  ```

- **HighEloMatcher**: Fetch matches from top players
  ```python
  matcher.get_grandmaster_players()    # Get top GM players
  matcher.get_challenger_players()     # Get top Challenger players
  matcher.get_recent_matches(puuid)    # Get player's recent matches
  matcher.get_match_details(match_id)  # Get match data
  ```

- **MetaAnalyzer**: Analyze comp performance
  ```python
  analyzer.extract_comp_from_match()   # Extract comp from match data
  analyzer.get_comp_core_units()       # Get top 3 units
  ```

- **MetaLearner**: Main orchestrator
  ```python
  learner.learn_from_matches()         # Analyze matches from top players
  learner.calculate_meta_scores()      # Compute meta scores (0-10)
  learner.update_meta_database()       # Save to comps_meta.json
  ```

**Usage:**
```bash
python meta_learner.py
```

### 2. **learner_scheduler.py** - Scheduling & Automation

**Modes:**

1. **Once mode** - Run learning once and exit
   ```bash
   python learner_scheduler.py once
   ```
   - Useful for: CI/CD, cron jobs, one-time analysis

2. **Test mode** - Dry run without updating meta
   ```bash
   python learner_scheduler.py test
   ```
   - Useful for: Testing, debugging

3. **Daemon mode** - Run continuously in background
   ```bash
   python learner_scheduler.py daemon [interval_hours] [check_seconds]
   
   # Examples:
   python learner_scheduler.py daemon           # Check every 6 hours
   python learner_scheduler.py daemon 4 30      # Check every 4 hours, verify every 30 sec
   ```
   - Useful for: Production servers, always-on systems

---

## 📊 How Learning Works

### Step 1: Patch Detection
```
Check TFT-STATUS-V1/platform-data
  ↓
Compare current patch vs saved patch
  ↓
If different → trigger full analysis
```

### Step 2: High-Elo Match Crawling
```
Get top 20 Grandmaster players (TFT-LEAGUE-V1)
  ↓
For each player:
  - Fetch 5 recent matches (TFT-MATCH-V1)
  - Extract comp info (units, placement)
  - Record performance
```

### Step 3: Meta Analysis
```
For each unique comp core:
  - Collect all placements (1-8)
  - Calculate winrate (top 4 = win)
  - Calculate frequency bonus
  ↓
Meta Score = (winrate × 8) + (frequency_bonus)
```

### Step 4: Database Update
```
Merge learned comps with existing comps
  ↓
Prioritize learned comps (fresh data)
  ↓
Save to comps_meta.json
  ↓
Update patch_info.json
```

---

## ⚙️ Configuration

All settings in `config.py`:

```python
# Learning frequency
LEARNING_INTERVAL_HOURS = 6

# How much data to analyze
MATCHES_PER_PLAYER = 5
NUM_HIGH_ELO_PLAYERS = 20

# Quality thresholds
MIN_COMP_SAMPLES = 3          # Need ≥3 samples
WINRATE_WEIGHT = 8.0          # How much winrate matters
FREQUENCY_WEIGHT = 2.0        # Bonus for popular comps

# Auto-updates
AUTO_UPDATE_ON_PATCH = True   # Learn when patch drops
PATCH_CHECK_INTERVAL_HOURS = 1
```

### Tuning Guide

**For more aggressive updates:**
```python
LEARNING_INTERVAL_HOURS = 3           # Learn every 3 hours instead of 6
NUM_HIGH_ELO_PLAYERS = 50             # Analyze more players
MATCHES_PER_PLAYER = 10               # More matches per player
```

**For lighter load:**
```python
LEARNING_INTERVAL_HOURS = 24          # Once per day
NUM_HIGH_ELO_PLAYERS = 10             # Fewer players
MATCHES_PER_PLAYER = 3                # Fewer matches
```

---

## 🚀 Deployment Options

### Option 1: Cron Job (Linux/Mac)
```bash
# Edit crontab
crontab -e

# Run every 6 hours
0 */6 * * * cd /path/to/tft-autobot && python learner_scheduler.py once

# Run every day at 2 AM
0 2 * * * cd /path/to/tft-autobot && python learner_scheduler.py once
```

### Option 2: Windows Task Scheduler
```powershell
# Create scheduled task to run learner_scheduler.py daemon
$trigger = New-ScheduledTaskTrigger -AtStartup
$action = New-ScheduledTaskAction -Execute "python.exe" -Argument "C:\path\to\learner_scheduler.py daemon"
Register-ScheduledTask -TaskName "TFT-MetaLearner" -Trigger $trigger -Action $action
```

### Option 3: Docker + Kubernetes
```dockerfile
# Dockerfile
FROM python:3.11
WORKDIR /app
COPY . /app
RUN pip install -r requirements.txt
CMD ["python", "learner_scheduler.py", "daemon", "6", "60"]
```

```bash
# Run in Docker
docker run -d \
  -e RIOT_API_KEY=your-key \
  -v /path/to/data:/app/data \
  tft-autobot:latest
```

### Option 4: Always-On Process
```bash
# Terminal 1: Run daemon
python learner_scheduler.py daemon

# Or with supervisor (supervisord.conf)
[program:tft-meta-learner]
command=python /path/to/learner_scheduler.py daemon
autostart=true
autorestart=true
stderr_logfile=/path/to/logs/learning.err.log
stdout_logfile=/path/to/logs/learning.out.log
```

---

## 📈 Data Flow & Output

### Input
```
Riot API
├── TFT-STATUS-V1: Current patch version
├── TFT-LEAGUE-V1: Grandmaster/Challenger players
└── TFT-MATCH-V1: Match details (units, placement, items)
```

### Processing
```
1. Extract comp core from each match
   Example: [Ahri, Annie, Lulu, Janna, Sona]
   → Core: [Ahri, Annie, Lulu]

2. Record placement (1-8)
   Top 4 = win, 5-8 = loss

3. Calculate statistics
   - Winrate = (wins / total_games)
   - Frequency = (play_count)
   - Meta Score = (winrate × 8) + (frequency_bonus)
```

### Output
```
comps_meta.json (Updated)
{
  "name": "Ahri + Annie + Lulu",
  "core_units": ["Ahri", "Annie", "Lulu"],
  "meta_score": 8.5,           ← Calculated from real data
  "winrate": 62.5,             ← From Grandmaster matches
  "sample_size": 24,           ← How many matches
  "tags": ["learned-from-api"]
}

patch_info.json
{
  "patch": "14.2",
  "meta_version": 45,
  "last_updated": "2024-01-20T..." 
  "source": "riot-api"
}
```

---

## 📊 Example Analysis

**Input**: 20 Grandmaster players, 5 matches each = 100 matches

**Data Processing**:
```
100 matches
  ↓
Extract comps from each match
  ↓
Group by core units
  ↓
100 unique comps found
  ↓
Filter (min 3 samples)
  ↓
45 viable comps remaining
  ↓
Calculate meta scores
  ↓
comps_meta.json updated with 45 comps
```

**Example Results**:
| Comp | Winrate | Samples | Meta Score |
|------|---------|---------|-----------|
| Ahri+Annie+Lulu | 67% | 24 | 8.7 |
| Yasuo+Vi+Illaoi | 58% | 18 | 7.2 |
| Syndra+Lux+Annie | 62% | 15 | 7.8 |

---

## 🔍 Monitoring & Logging

### Log Files
```
logs/
├── meta_learner.log     # Learning run logs
├── games.jsonl          # Game history (existing)
└── [other logs]
```

### Example Log Output
```
2024-01-20 02:30:00 - INFO - Starting meta learning cycle
2024-01-20 02:30:01 - INFO - Current patch: 14.2
2024-01-20 02:30: - INFO - New patch detected - starting analysis
2024-01-20 02:30:05 - INFO - Fetching top 20 Grandmaster players...
2024-01-20 02:30:10 - INFO - Found 20 players
2024-01-20 02:30:15 - INFO - Player 1/20: Challenger_V1_PBE
2024-01-20 02:30:20 - INFO - Analyzing 5 matches...
...(more analysis)...
2024-01-20 02:45:00 - INFO - Analysis Complete
2024-01-20 02:45:01 - INFO - - Matches analyzed: 100
2024-01-20 02:45:01 - INFO - - Comps found: 100
2024-01-20 02:45:01 - INFO - - Unique comps: 45
2024-01-20 02:45:02 - INFO - Updating meta database...
2024-01-20 02:45:03 - INFO - ✓ Meta learning successful
```

### Monitoring Commands
```bash
# Check if daemon is running
ps aux | grep learner_scheduler

# View live logs
tail -f logs/meta_learner.log

# Check meta database age
stat data/meta/comps_meta.json

# Verify patch tracking
cat data/meta/patch_info.json
```

---

## ⚠️ Rate Limiting & Quotas

**Riot API Limits** (per key):
- 20 requests / 1 sec
- 100 requests / 2 min

**Our Strategy**:
- 0.13s delay between requests (8 req/sec)
- Stay well under limits
- Safe for production use

**Estimated API calls per run** (20 players, 5 matches):
```
1. Patch check: 1 call
2. Get GM players: 1 call
3. Get recent matches: 20 calls (per player)
4. Get match details: 100 calls (per match)
─────────────────────
Total: ~122 API calls per run
Time: ~16 seconds
```

---

## 🧪 Testing

### Test Mode (Dry Run)
```bash
python learner_scheduler.py test
# Runs analysis without updating meta
# Safe for testing setup
```

### Manual Testing
```python
# In Python
from meta_learner import MetaLearner, MetaPatcher

# Check patch
patch = MetaPatcher.get_current_patch()
print(f"Current patch: {patch}")

# Run learner
learner = MetaLearner()
learner.learn_from_matches(matches_per_player=3, num_players=5)
comps = learner.calculate_meta_scores()
for comp in comps[:5]:
    print(comp)
```

---

## 🔗 Integration with CLI

Once meta is updated automatically, CLI gets fresh data:

```bash
python cli_main.py

# CLI automatically uses latest comps_meta.json
# No manual updates needed!

=> Recommendations now based on current meta
=> Personal score calculated from game logs
=> Always up-to-date with patch changes
```

---

## 🎯 Future Enhancements

- [ ] Multi-region learning (learn from all regions)
- [ ] Temporal analysis (track meta evolution)
- [ ] Item meta learning (best items per comp)
- [ ] Trait synergy analysis
- [ ] Champion itemization patterns
- [ ] Win condition detection
- [ ] ML-based meta scoring
- [ ] Real-time spectator analysis

---

## 📞 Troubleshooting

### API Key Issues
```
Error: RIOT_API_KEY not found

Solution:
1. Add to .env: echo "RIOT_API_KEY=your-key" > .env
2. Or set environment: export RIOT_API_KEY=your-key
3. Or modify load_api_key() in meta_learner.py
```

### Rate Limited (429)
```
Error: Status 429 - Too Many Requests

Not our fault! Riot rate limited us.
Script auto-retries with exponential backoff.
Reduce NUM_HIGH_ELO_PLAYERS or MATCHES_PER_PLAYER.
```

### No API Key Errors
```
Error: Failed to get grandmaster players

Check:
1. API key validity: developer.riotgames.com
2. Account tier (need at least level 1)
3. API endpoints are correct
```

---

## 📚 References

- [Riot Developer Portal](https://developer.riotgames.com)
- [TFT API Documentation](https://developer.riotgames.com/apis#tft-league-v1)
- [Rate Limiting Guide](https://developer.riotgames.com/rate-limiting)

---

## 📝 Summary

The **Continuous Learning System** enables:

✅ **Automatic patch detection** - No manual intervention needed
✅ **Real data analysis** - Based on Grandmaster/Challenger play
✅ **Fresh meta** - Database updates every 6 hours (configurable)
✅ **Historical tracking** - Know when/how meta changes
✅ **Zero maintenance** - Set and forget daemon

**Result**: TFT Auto-bot always knows the latest meta! 🚀
