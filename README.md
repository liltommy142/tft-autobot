# TFT Auto-bot / Rank Assistant

Tool hỗ trợ quyết định đội hình (comp), econ (kinh tế), và item trong TFT (Teamfight Tactics).

Được thiết kế với kiến trúc modular: tách logic ra khỏi data meta, giúp dễ dàng cập nhật meta độc lập.

## 🎯 Tính năng

- **Gợi ý comp**: Dựa trên game state (level, gold, units hiện có) và meta score
- **Lời khuyên econ**: ROLL / LEVEL / SAVE dựa trên HP và vàng
- **Gợi ý item**: Gợi ý trang bị cho core unit của comp chọn
- **Lưu log game**: Ghi lại mỗi game vào JSONL format để phân tích
- **Fetch từ Riot API**: Tự động lấy match data từ Riot API (với PowerShell scheduler)

## 🏗️ Cấu trúc Project

```
tft-autobot/
├── src/                          # Core modules
│   ├── __init__.py
│   ├── config.py                 # Constants tập trung
│   ├── logger.py                 # Logger cho JSONL output
│   ├── core_models.py            # Data models: GameState, UnitInstance
│   ├── core_engine.py            # Logic: recommend_comps, econ_advice
│   ├── cli_main.py               # CLI interface
│   ├── tft_assistant.py          # Alternative interface
│   ├── update_meta.py            # Create/update metadata
│   ├── fetch_meta.py             # Fetch meta từ online sources
│   ├── fetch_from_riot.py        # Fetch từ Riot API
│   ├── meta_learner.py           # Continuous learning engine
│   └── learner_scheduler.py      # Task scheduler
│
├── tests/                        # Test suite
│   ├── __init__.py
│   ├── test_core_models.py
│   └── test_core_engine.py
│
├── docs/                         # Documentation
│   ├── ARCHITECTURE.md           # System design
│   ├── CONTRIBUTING.md           # Contribution guide
│   ├── CONTINUOUS_LEARNING.md    # Meta learning setup
│   └── CHANGES.md                # Changelog
│
├── scripts/                      # Utility scripts
│   └── create_task.ps1           # Windows Task Scheduler helper
│
├── data/                         # Data files
│   ├── meta/
│   │   ├── comps_meta.json       # Composition database
│   │   ├── items.json            # Item recommendations
│   │   └── patch_info.json       # Patch metadata
│   └── ...other data
│
├── logs/                         # Game logs (generated)
│   └── games.jsonl               # JSONL game history
│
├── main.py                       # Entry point: CLI assistant
├── learn.py                      # Entry point: Meta learner
├── schedule.py                   # Entry point: Scheduler
├── .env                          # Environment variables
├── pytest.ini                    # Pytest configuration
├── mypy.ini                      # Type checking config
├── requirements.txt              # Dependencies
├── dev-requirements.txt          # Dev dependencies
└── README.md                     # This file
```

## 🚀 Cách Sử Dụng

### 1. Setup & Cài Đặt

```bash
# Clone repo
cd d:/GitHub/tft-autobot

# Tạo virtual environment
python -m venv .venv
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r dev-requirements.txt  # Nếu muốn linting + testing
```

### 2. Khởi Tạo Metadata

```bash
# Tạo data/meta/ với sample data
python update_meta.py

# Hoặc fetch từ online sources
python fetch_meta.py
```

### 3. Chạy CLI Assistant

```bash
python main.py

# Menu:
# (1) run assistant - Gợi ý cho game hiện tại
# (2) log game      - Ghi log kết quả game
# (3) show logs     - Xem 50 game gần nhất
```

**Ví dụ:**
```
Level hiện tại: 7
Vàng hiện tại: 45
Máu hiện tại: 65
Round: 4-1
Tướng đang có: Ahri2,Annie1,Lulu1

=> Gợi ý: AP Carry Ahri, LEVEL (có vàng), items cho Ahri
```

### 4. Fetch Match History từ Riot (Optional)

Cần Riot API key: https://developer.riotgames.com/

```bash
# Setup .env
echo "RIOT_API_KEY=your-api-key-here" > .env

# Fetch 15 games gần nhất
python fetch_from_riot.py "YourSummonerName" vn1

# Hoặc auto-detect platform
python fetch_from_riot.py "YourSummonerName"
```

Để schedule tự động (Windows):
```powershell
# Chạy PowerShell elevated
.\scripts\create_task.ps1 -Summoner "YourName" -Platform vn1 -Time "02:30"

# Sẽ chạy auto mỗi ngày lúc 02:30 AM
```

### 5. Continuous Meta Learning (Optional, Advanced) 🤖

Tự động học meta từ Grandmaster/Challenger players - **meta luôn cập nhật**!

```bash
# Run once to analyze latest meta
python learn.py

# Or run as daemon (learns automatically every 6 hours)
python schedule.py daemon 6 60
  # Checks every 60 seconds, learns every 6 hours

# Dry-run without updating meta
python schedule.py test
```

**Tính năng**:
- ✅ Auto-detects patch updates (TFT-STATUS-V1)
- ✅ Crawls high-elo matches (TFT-LEAGUE-V1)  
- ✅ Calculates real-time comp winrates (TFT-MATCH-V1)
- ✅ Updates meta automatically every 6 hours
- ✅ Tracks meta version history

**Kết quả**: `comps_meta.json` tự động được cập nhật với meta mới nhất! 📊

Chi tiết → **[docs/CONTINUOUS_LEARNING.md](docs/CONTINUOUS_LEARNING.md)** (deployment, cron, Docker, v.v.)

## 🧪 Testing

```bash
# Run tests
pytest -v

# With coverage
pytest --cov=core_models --cov=core_engine
```

## 📊 Data Formats

### games.jsonl (Game Log)
```json
{
  "patch": "fetched-auto",
  "placement": 5,
  "comp_name": "AP Carry Ahri",
  "final_board": ["Ahri3", "Annie2", "Lulu2"],
  "items": {"Ahri": ["Rabadon", "Jeweled"], "Annie": ["Zhonyas"]},
  "timestamp": "2024-01-15T10:30:45.123Z"
}
```

### comps_meta.json
```json
[
  {
    "name": "AP Carry Ahri",
    "core_units": ["Ahri", "Annie", "Lulu"],
    "optional_units": ["Janna", "Sona"],
    "ideal_level": 8,
    "meta_score": 5
  }
]
```

### items.json
```json
[
  {
    "name": "Rabadon's Deathcap",
    "best_users": ["Ahri", "Syndra"],
    "note": "Tăng sát thương phép cho carry AP"
  }
]
```

## 🔧 Configuration

Tất cả magic numbers được tập trung trong `config.py`:

```python
LOW_HP_THRESHOLD = 40          # HP < này -> ROLL
HIGH_GOLD_THRESHOLD = 50       # Gold >= này + level < 8 -> LEVEL
CORE_UNIT_MULTIPLIER = 3       # Weight cho core unit khi scoring comp
PERSONAL_LOG_LIMIT = 500       # Lấy bao nhiêu games gần nhất để tính personal score
```

Để tuning lại logic, chỉnh config.py rồi core_engine.py sẽ tự động áp dụng.

## 📈 Cách Mở Rộng

### Thêm Logic Econ Mới

Edit `core_engine.py` → `econ_advice()`:
- Thêm thêm rule mới (ví dụ: nếu có item spike, ROLL hôm nay)
- Hoặc dùng ML model để predict

### Cập Nhật Meta

Sửa `update_meta.py`:
- Từ local examples → Fetch từ Riot API
- Từ tactics.tools → Fetch từ lolchess, blitz.gg, etc.

### Thêm Tracking

Sửa `cli_main.py` hoặc tạo UI mới:
- Web interface (Flask/Django)
- Discord bot
- vs...

## ⚠️ Lưu Ý

- **Rate limits**: Riot API có strict rate limits. Script tự động handle nhưng nếu fetch quá nhiều sẽ bị throttle
- **Meta data**: Sample data là placeholder. Nên cập nhật meta 1-2 lần/mùa để stay relevant
- **Validation**: Input từ CLI được validate nhưng logic vẫn có thể fail nếu data format sai
- **Logs**: Game log JSONL không có hard delete; archive theo tuần/tháng

## 🐛 Troubleshooting

**"Meta file not found: data/meta/comps_meta.json"**
→ Chạy `python update_meta.py` để tạo metadata

**"RIOT_API_KEY not set"**
→ Tạo .env file hoặc export env var RIOT_API_KEY

**"Auto-detect failed"**
→ Summoner name không found trên platform được provide. Specify platform explicit

## 📝 License

MIT

## 👤 Author

Created for TFT players muốn optimize decision-making in game.

