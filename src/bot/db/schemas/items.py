from logging import critical
from pydantic import BaseModel, Field
from typing import Optional


class BaseAttributes(BaseModel):
    item_level: int = Field(..., ge=1)

class WeaponAttributes(BaseAttributes):
    min_damage: int = Field(..., ge=1)
    max_damage: int = Field(..., ge=1)

    attack_speed: float = Field(..., ge=1.0)

    critical_chance: float = Field(default=0.0, ge=0.0, le=1.0)
    critical_multiplier: float = Field(default=1.0, ge=1.0, le=10.0)


class ArmorAttributes(BaseAttributes):
    defense: int = Field(..., ge=1)
    
    health_bonus: int = Field(ge=0, default=0)