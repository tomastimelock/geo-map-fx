from __future__ import annotations

__version__ = "0.1.0"

from geo_map_fx.api import MapRenderer, list_palettes
from geo_map_fx.base import MapParams
from geo_map_fx.renderers.static import render_static
from geo_map_fx.renderers.interactive import render_interactive

__all__ = [
    "__version__",
    "MapRenderer",
    "MapParams",
    "render_static",
    "render_interactive",
    "list_palettes",
]
