# scripts/basedb.py
import asyncio

from basedb.generator import create_base_items


if __name__ == "__main__":
    asyncio.run(create_base_items())