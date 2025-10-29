from logging import critical
from pydantic import BaseModel, Field
from typing import Optional


class BaseAttributes(BaseModel):
    pass

class WeaponAttributes(BaseAttributes):
    damage: int = Field(..., ge=1)
    critical_chance: float = Field(default= 0.0, ge=0.0, le=1.0)

class ArmorAttributes(BaseAttributes):
    pass
