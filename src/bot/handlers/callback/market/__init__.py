from .deps import market_router as callback_market_router

# Import modules so handlers register on the router.
from . import menu  # noqa: F401
from . import catalog  # noqa: F401
from . import my_listings  # noqa: F401
from . import inputs  # noqa: F401

__all__ = ("callback_market_router",)

