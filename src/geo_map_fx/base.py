from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

ViewMode = Literal[
    "regions",
    "municipalities",
    "region_municipalities",
    "region_valdistrikt",
    "municipality_valdistrikt",
]
OutputFormat = Literal["png", "svg", "html"]
LegendPosition = Literal["bottom-right", "bottom-left", "top-right", "top-left", "none"]


@dataclass
class MapParams:
    """Parameters controlling a single choropleth map render."""

    view: ViewMode = "municipalities"
    scope: str = "sweden"  # "sweden" | 2-char lan_kod | 4-char kommun_kod
    values: dict[str, float | None] = field(default_factory=dict)
    palette: str = "YlOrRd"
    reverse_palette: bool = False
    no_data_color: str = "#cccccc"
    border_color: str = "#ffffff"
    border_width: float = 0.5
    title: str | None = None
    legend_position: LegendPosition = "bottom-right"
    width: int = 1200
    height: int = 900
    dpi: int = 150
    output_format: OutputFormat = "png"
    background_color: str = "#f8f8f8"
    font_size: int = 10
    show_legend: bool = True
    value_format: str = "{:.1f}"
    value_label: str = ""  # label shown next to legend (e.g. "%" or "kr")
