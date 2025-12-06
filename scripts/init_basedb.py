# scripts/init_basedb.py
import asyncio
import sys
from pathlib import Path

# Add scripts directory to path so we can import basedb package
scripts_dir = Path(__file__).resolve().parent
if str(scripts_dir) not in sys.path:
    sys.path.insert(0, str(scripts_dir))

from basedb.generator import create_base_items


if __name__ == "__main__":
    asyncio.run(create_base_items())

