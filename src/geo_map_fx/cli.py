from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Optional

import typer

app = typer.Typer(name="geo-map-fx", add_completion=False)


@app.command()
def render(
    values_json: str = typer.Argument(..., help='JSON string or @file.json with {region_id: value} dict'),
    view: str = typer.Option("municipalities", "--view", "-v", help="View mode"),
    scope: str = typer.Option("sweden", "--scope", "-s", help="Scope: 'sweden', lan_kod, or kommun_kod"),
    palette: str = typer.Option("YlOrRd", "--palette", "-p"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output file path"),
    output_format: str = typer.Option("png", "--format", "-f", help="png | svg | html"),
    title: Optional[str] = typer.Option(None, "--title"),
    width: int = typer.Option(1200, "--width"),
    height: int = typer.Option(900, "--height"),
    dpi: int = typer.Option(150, "--dpi"),
    no_legend: bool = typer.Option(False, "--no-legend"),
    value_label: str = typer.Option("", "--value-label"),
) -> None:
    """Render a choropleth map from a JSON values dict."""
    # Load values
    if values_json.startswith("@"):
        values = json.loads(Path(values_json[1:]).read_text(encoding="utf-8"))
    else:
        values = json.loads(values_json)

    from geo_map_fx.api import MapRenderer
    r = MapRenderer()
    result = r.render(
        values=values,
        view=view,
        scope=scope,
        palette=palette,
        title=title,
        output_format=output_format,
        width=width,
        height=height,
        dpi=dpi,
        show_legend=not no_legend,
        value_label=value_label,
        output_path=output,
    )

    if output is None:
        if isinstance(result, str):
            sys.stdout.write(result)
        else:
            sys.stdout.buffer.write(result)
    else:
        typer.echo(f"Wrote {output}")


@app.command()
def palettes() -> None:
    """List available color palettes."""
    from geo_map_fx.api import list_palettes
    for name in list_palettes():
        typer.echo(name)


if __name__ == "__main__":
    app()
