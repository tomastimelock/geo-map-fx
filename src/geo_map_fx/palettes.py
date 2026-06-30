from __future__ import annotations

import matplotlib.cm as cm
import matplotlib.colors as mcolors
import numpy as np

# Available palette names → matplotlib colormap names
PALETTES: dict[str, str] = {
    "YlOrRd": "YlOrRd",
    "YlGn": "YlGn",
    "Blues": "Blues",
    "viridis": "viridis",
    "plasma": "plasma",
    "RdYlGn": "RdYlGn",
    "Reds": "Reds",
    "BuPu": "BuPu",
    "OrRd": "OrRd",
    "PuBuGn": "PuBuGn",
    "GnBu": "GnBu",
    "YlOrBr": "YlOrBr",
}


def get_cmap(name: str, reverse: bool = False):
    """Return a matplotlib colormap by palette name."""
    cmap_name = PALETTES.get(name, name)
    if reverse:
        cmap_name = cmap_name + "_r"
    return cm.get_cmap(cmap_name)


def build_color_stops(
    values: list[float],
    palette: str,
    reverse: bool = False,
    n_stops: int = 9,
) -> list[tuple[float, str]]:
    """Return [(value, hex_color), ...] stops for use in MapLibre interpolation."""
    if not values:
        return []
    vmin, vmax = min(values), max(values)
    if vmin == vmax:
        vmax = vmin + 1
    cmap = get_cmap(palette, reverse)
    stops = []
    for i in range(n_stops):
        t = i / (n_stops - 1)
        v = vmin + t * (vmax - vmin)
        rgba = cmap(t)
        stops.append((v, mcolors.to_hex(rgba)))
    return stops
