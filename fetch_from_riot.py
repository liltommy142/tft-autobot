#!/usr/bin/env python
"""
fetch_from_riot.py - Entry point for Riot API data fetching.
"""
import sys
import os
from pathlib import Path

# Thêm thư mục 'src' vào Python path để tìm thấy file logic_riot.py
# Add 'src' to Python path to enable internal module imports
src_path = str(Path(__file__).parent / "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

# Bây giờ có thể import từ file trong thư mục src
from fetch_from_riot import main 

if __name__ == "__main__":
    main()
