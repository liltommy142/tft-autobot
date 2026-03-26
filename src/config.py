"""
config.py - Tập trung tất cả constants & configuration
"""
import os

# ============ Directories ============
ROOT_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(ROOT_DIR, "data")
META_DIR = os.path.join(DATA_DIR, "meta")
LOGS_DIR = os.path.join(ROOT_DIR, "logs")

# ============ Log files ============
LOG_FILE = os.path.join(LOGS_DIR, "games.jsonl")

# ============ Econ Strategy Constants ============
LOW_HP_THRESHOLD = 40
HIGH_GOLD_THRESHOLD = 50
MIN_LEVEL_TO_LEVEL_UP = 8
ROLL_ACTION = "ROLL"
LEVEL_ACTION = "LEVEL"
SAVE_ACTION = "SAVE"

# ============ Comp Scoring Constants ============
CORE_UNIT_MULTIPLIER = 3
OPTIONAL_UNIT_MULTIPLIER = 1
IDEAL_LEVEL_DEFAULT = 8
PERSONAL_SCORE_MAX = 5.0
PERSONAL_LOG_LIMIT = 500
COMP_SCORE_THRESHOLD = 0
TOP_N_COMPS = 3

# ============ API Constants ============
RATE_LIMIT_DELAY = 0.13  # seconds between Riot API calls
API_TIMEOUT = 10
MAX_RETRIES = 3
MAX_RECENT_MATCHES = 15

# ============ Validation ============
VALID_PLACEMENTS = range(1, 9)  # 1-8
MIN_STAR_LEVEL = 1
MAX_STAR_LEVEL = 3
DEFAULT_STAR_LEVEL = 1

# ============ Display ============
DEFAULT_LEVEL = 6
DEFAULT_GOLD = 30
DEFAULT_HP = 70
DEFAULT_ROUND = "3-2"
TOP_N_LOGS_TO_SHOW = 50

# ============ Meta Learning ============
# Continuous learning from Riot API
LEARNING_INTERVAL_HOURS = 6          # How often to analyze grandmaster meta
MATCHES_PER_PLAYER = 5               # Recent matches to analyze per player
NUM_HIGH_ELO_PLAYERS = 20            # Number of grandmaster players to analyze
MIN_COMP_SAMPLES = 3                 # Min matches for comp to be considered
LEARNING_PLATFORM = "na1"            # Which platform to learn from

# Meta score calculation
WINRATE_WEIGHT = 8.0                 # Contribution of winrate to meta score
FREQUENCY_WEIGHT = 2.0               # Bonus for frequently played comps
META_SCORE_MAX = 10.0                # Max possible meta score

# Patch tracking
PATCH_CHECK_INTERVAL_HOURS = 1       # How often to check for patch updates
AUTO_UPDATE_ON_PATCH = True          # Auto-analyze when patch updates

# Learning scheduler
SCHEDULER_CHECK_INTERVAL = 60        # Seconds between scheduler checks
SCHEDULER_ENABLED = True             # Enable background meta learning
