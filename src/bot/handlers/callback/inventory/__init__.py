from .deps import inventory_router as callback_inventory_router

from . import menu  # noqa: F401
from . import listing  # noqa: F401
from . import view  # noqa: F401
from . import sell  # noqa: F401

__all__ = ("callback_inventory_router",)

