from __future__ import annotations

import io
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import Normalize
from matplotlib.cm import ScalarMappable
from shapely.validation import make_valid

matplotlib.use("Agg")

from geo_map_fx.base import MapParams
from geo_map_fx.data_loader import load_for_view
from geo_map_fx.palettes import get_cmap

_LEGEND_LOC = {
    "bottom-right": "lower right",
    "bottom-left": "lower left",
    "top-right": "upper right",
    "top-left": "upper left",
    "none": None,
}


def render_static(params: MapParams, output_path: Path | None = None) -> bytes:
    """
    Render a choropleth map to PNG or SVG bytes.
    If output_path is given, also writes the file.
    """
    gdf, id_col = load_for_view(params.view, params.scope)

    # Re-validate (coordinate rounding may have introduced degenerate edges)
    gdf["geometry"] = gdf["geometry"].apply(make_valid)

    # Attach values
    gdf["_value"] = gdf[id_col].map(params.values)

    # Compute value range from non-null entries
    valid_vals = [v for v in params.values.values() if v is not None]
    vmin = min(valid_vals) if valid_vals else 0.0
    vmax = max(valid_vals) if valid_vals else 1.0
    if vmin == vmax:
        vmax = vmin + 1

    cmap = get_cmap(params.palette, params.reverse_palette)
    norm = Normalize(vmin=vmin, vmax=vmax)

    fig_w = params.width / params.dpi
    fig_h = params.height / params.dpi

    fig, ax = plt.subplots(figsize=(fig_w, fig_h), dpi=params.dpi)
    fig.patch.set_facecolor(params.background_color)
    ax.set_facecolor(params.background_color)
    ax.set_axis_off()

    # Split: has value vs no data
    has_data = gdf[gdf["_value"].notna()]
    no_data = gdf[gdf["_value"].isna()]

    if not no_data.empty:
        no_data.plot(ax=ax, color=params.no_data_color, edgecolor=params.border_color, linewidth=params.border_width)

    if not has_data.empty:
        has_data.plot(
            ax=ax,
            column="_value",
            cmap=cmap,
            vmin=vmin,
            vmax=vmax,
            edgecolor=params.border_color,
            linewidth=params.border_width,
            legend=False,
        )

    # Legend colorbar
    if params.show_legend and params.legend_position != "none" and valid_vals:
        sm = ScalarMappable(cmap=cmap, norm=norm)
        sm.set_array([])
        loc = _LEGEND_LOC.get(params.legend_position, "lower right")
        from mpl_toolkits.axes_grid1.inset_locator import inset_axes
        cbax = inset_axes(
            ax,
            width="3%",
            height="30%",
            loc=loc,
            borderpad=1.5,
        )
        cbar = fig.colorbar(sm, cax=cbax, orientation="vertical")
        cbar.ax.tick_params(labelsize=params.font_size - 1)
        if params.value_label:
            cbar.set_label(params.value_label, size=params.font_size)

    if params.title:
        ax.set_title(params.title, fontsize=params.font_size + 2, pad=8)

    plt.tight_layout(pad=0.5)

    fmt = params.output_format if params.output_format in ("png", "svg") else "png"
    buf = io.BytesIO()
    fig.savefig(buf, format=fmt, dpi=params.dpi, bbox_inches="tight",
                facecolor=params.background_color)
    plt.close(fig)
    buf.seek(0)
    data = buf.read()

    if output_path is not None:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_bytes(data)

    return data
