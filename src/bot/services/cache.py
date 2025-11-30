import asyncio
import time
import json
from typing import Optional, Dict, Any, Callable, Tuple
from functools import wraps
from redis.asyncio import Redis
from tortoise import Tortoise
import logging
from dataclasses import dataclass
from enum import Enum

logging = logging.getLogger(__name__)

class CacheMode(Enum):
    LAZY = 'lazy'
    ACTIVE = 'active'
    OFF = 'off'

@dataclass
class CacheStats:
    hits: int = 0
    misses: int = 0
    invalidations: int = 0
    stale_updates: int = 0

class CacheService:
    def __init__(self):
        self.redis_client: Optional[Redis] = None
        self.cache_ttls = {
            'user': 300,
            'items': 600,
            'market_prices': 60, 
        }