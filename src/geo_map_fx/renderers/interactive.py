from __future__ import annotations

import json
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from geo_map_fx.base import MapParams
from geo_map_fx.data_loader import load_for_view
from geo_map_fx.palettes import build_color_stops, get_cmap

_TEMPLATES_DIR = Path(__file__).parent.parent / "templates"

_LEGEND_CSS = {
    "bottom-right": "bottom: 20px; right: 20px;",
    "bottom-left":  "bottom: 20px; left: 20px;",
    "top-right":    "top: 60px; right: 20px;",
    "top-left":     "top: 60px; left: 20px;",
    "none":         "display: none;",
}


def render_interactive(params: MapParams, output_path: Path | None = None) -> str:
    """
    Render a MapLibre GL JS choropleth widget as a self-contained HTML string.
    If output_path is given, also writes the file.
    """
    gdf, id_col = load_for_view(params.view, params.scope)

    # Attach values as _value property in GeoJSON
    gdf["_value"] = gdf[id_col].map(params.values)

    # Compute bounds [minx, miny, maxx, maxy]
    bounds = list(gdf.total_bounds)  # [minx, miny, maxx, maxy]

    # Build color stops from non-null values
    valid_vals = [v for v in params.values.values() if v is not None]
    color_stops = build_color_stops(valid_vals, params.palette, params.reverse_palette, n_stops=9)
    # Flatten to [v1, color1, v2, color2, ...] for JS spread
    color_stops_json = json.dumps(color_stops)

    # Gradient CSS for legend bar
    gradient_colors = ", ".join(c for _, c in color_stops) if color_stops else "#ccc"

    vmin = color_stops[0][0] if color_stops else 0
    vmax = color_stops[-1][0] if color_stops else 1
    fmt = params.value_format
    vmin_label = fmt.format(vmin) + (f" {params.value_label}" if params.value_label else "")
    vmax_label = fmt.format(vmax) + (f" {params.value_label}" if params.value_label else "")

    # Serialize filtered GeoJSON; replace NaN with null
    geojson_dict = json.loads(gdf.to_json(drop_id=True, show_bbox=False))
    for feat in geojson_dict["features"]:
        v = feat["properties"].get("_value")
        if v != v:  # NaN check
            feat["properties"]["_value"] = None
    geojson_str = json.dumps(geojson_dict)

    env = Environment(
        loader=FileSystemLoader(str(_TEMPLATES_DIR)),
        autoescape=select_autoescape(["html"]),
    )
    # tojson filter for safe JS embedding
    env.filters["tojson"] = lambda x: json.dumps(x)

    tmpl = env.get_template("maplibre_widget.html.j2")
    html = tmpl.render(
        title=params.title or "",
        geojson_str=geojson_str,
        color_stops_json=color_stops_json,
        bounds_json=json.dumps(bounds),
        no_data_color=params.no_data_color,
        border_color=params.border_color,
        border_width=params.border_width,
        gradient_colors=gradient_colors,
        vmin_label=vmin_label,
        vmax_label=vmax_label,
        show_legend=params.show_legend and params.legend_position != "none",
        has_no_data=gdf["_value"].isna().any(),
        legend_css_position=_LEGEND_CSS.get(params.legend_position, _LEGEND_CSS["bottom-right"]),
        background_color=params.background_color,
        value_format=params.value_format,
        value_label=params.value_label,
    )

    if output_path is not None:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(html, encoding="utf-8")

    return html
