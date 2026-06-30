from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

import geopandas as gpd

_DATA_DIR: Path | None = None


def get_data_dir() -> Path:
    global _DATA_DIR
    if _DATA_DIR is None:
        env = os.environ.get("GEO_MAP_FX_DATA_DIR")
        if env:
            _DATA_DIR = Path(env)
        else:
            _DATA_DIR = Path(r"E:\Kartan\geo-map-fx\geodata")
    if not _DATA_DIR.exists():
        raise RuntimeError(
            f"GeoJSON data directory not found: {_DATA_DIR}\n"
            "Set GEO_MAP_FX_DATA_DIR env var or run scripts/build_geodata.py first."
        )
    return _DATA_DIR


@lru_cache(maxsize=3)
def _load_raw(name: str) -> gpd.GeoDataFrame:
    path = get_data_dir() / name
    if not path.exists():
        raise FileNotFoundError(
            f"GeoJSON not found: {path}\nRun scripts/build_geodata.py to generate it."
        )
    return gpd.read_file(path)


def load_regions() -> gpd.GeoDataFrame:
    return _load_raw("sweden_regions.geojson").copy()


def load_municipalities() -> gpd.GeoDataFrame:
    return _load_raw("sweden_municipalities.geojson").copy()


def load_valdistrikt() -> gpd.GeoDataFrame:
    return _load_raw("sweden_valdistrikt.geojson").copy()


def load_for_view(view: str, scope: str) -> tuple[gpd.GeoDataFrame, str]:
    """
    Return (gdf, id_column) for the given view/scope.
    gdf is already filtered to scope; id_column is the property used to join values.
    """
    if view == "regions":
        gdf = load_regions()
        return gdf, "lan_kod"

    if view == "municipalities":
        gdf = load_municipalities()
        if scope != "sweden" and len(scope) == 2:
            gdf = gdf[gdf["lan_kod"] == scope].copy()
        return gdf, "kommun_kod"

    if view == "region_municipalities":
        gdf = load_municipalities()
        if len(scope) == 2:
            gdf = gdf[gdf["lan_kod"] == scope].copy()
        return gdf, "kommun_kod"

    if view == "region_valdistrikt":
        gdf = load_valdistrikt()
        if len(scope) == 2:
            gdf = gdf[gdf["lan_kod"] == scope].copy()
        return gdf, "valdistrikt_kod"

    if view == "municipality_valdistrikt":
        gdf = load_valdistrikt()
        if len(scope) == 4:
            gdf = gdf[gdf["kommun_kod"] == scope].copy()
        return gdf, "valdistrikt_kod"

    raise ValueError(f"Unknown view: {view!r}")
