from __future__ import annotations

from pathlib import Path

from geo_map_fx.base import MapParams, ViewMode, OutputFormat, LegendPosition
from geo_map_fx.palettes import PALETTES


class MapRenderer:
    """
    High-level API for geo-map-fx choropleth rendering.

    Usage::

        r = MapRenderer()
        png_bytes = r.render(
            values={"0180": 42.5, "0381": 18.2, ...},
            view="municipalities",
            scope="01",
            palette="YlOrRd",
            output_format="png",
        )
    """

    def render(
        self,
        values: dict[str, float | None],
        view: ViewMode = "municipalities",
        scope: str = "sweden",
        palette: str = "YlOrRd",
        reverse_palette: bool = False,
        no_data_color: str = "#cccccc",
        border_color: str = "#ffffff",
        border_width: float = 0.5,
        title: str | None = None,
        legend_position: LegendPosition = "bottom-right",
        width: int = 1200,
        height: int = 900,
        dpi: int = 150,
        output_format: OutputFormat = "png",
        background_color: str = "#f8f8f8",
        font_size: int = 10,
        show_legend: bool = True,
        value_format: str = "{:.1f}",
        value_label: str = "",
        output_path: str | Path | None = None,
    ) -> bytes | str:
        """
        Render a choropleth map.

        Returns:
            PNG/SVG bytes for static formats, HTML string for "html".
        """
        params = MapParams(
            view=view,
            scope=scope,
            values=values,
            palette=palette,
            reverse_palette=reverse_palette,
            no_data_color=no_data_color,
            border_color=border_color,
            border_width=border_width,
            title=title,
            legend_position=legend_position,
            width=width,
            height=height,
            dpi=dpi,
            output_format=output_format,
            background_color=background_color,
            font_size=font_size,
            show_legend=show_legend,
            value_format=value_format,
            value_label=value_label,
        )
        out_path = Path(output_path) if output_path else None

        if output_format == "html":
            from geo_map_fx.renderers.interactive import render_interactive
            return render_interactive(params, out_path)

        from geo_map_fx.renderers.static import render_static
        return render_static(params, out_path)

    def render_regions(
        self,
        values: dict[str, float | None],
        scope: str = "sweden",
        **kwargs,
    ) -> bytes | str:
        return self.render(values=values, view="regions", scope=scope, **kwargs)

    def render_municipalities(
        self,
        values: dict[str, float | None],
        scope: str = "sweden",
        **kwargs,
    ) -> bytes | str:
        return self.render(values=values, view="municipalities", scope=scope, **kwargs)

    def render_region_municipalities(
        self,
        values: dict[str, float | None],
        lan_kod: str,
        **kwargs,
    ) -> bytes | str:
        return self.render(values=values, view="region_municipalities", scope=lan_kod, **kwargs)

    def render_region_valdistrikt(
        self,
        values: dict[str, float | None],
        lan_kod: str,
        **kwargs,
    ) -> bytes | str:
        return self.render(values=values, view="region_valdistrikt", scope=lan_kod, **kwargs)

    def render_municipality_valdistrikt(
        self,
        values: dict[str, float | None],
        kommun_kod: str,
        **kwargs,
    ) -> bytes | str:
        return self.render(values=values, view="municipality_valdistrikt", scope=kommun_kod, **kwargs)


def list_palettes() -> list[str]:
    return list(PALETTES.keys())
