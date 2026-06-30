"""
build_geodata.py — Generate geo-map-fx GeoJSON assets from Kartan source data.

Run once (or after updating source data):
    python scripts/build_geodata.py

Outputs to GEO_MAP_FX_DATA_DIR (default: E:/Kartan/geo-map-fx/geodata/):
    sweden_municipalities.geojson   — 290 municipalities, WGS84
    sweden_regions.geojson          — 21 counties dissolved from municipalities
    sweden_valdistrikt.geojson      — ~6000 electoral districts, WGS84
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import geopandas as gpd
import pandas as pd
from shapely.validation import make_valid

# ── Source paths ──────────────────────────────────────────────────────────────
KARTAN_ROOT = Path(os.environ.get("KARTAN_ROOT", r"C:\Users\tomas\PycharmProjects\Kartan"))
MUNICIPALITIES_SRC = KARTAN_ROOT / "data/geodata/kommuner.geojson"
VALDISTRIKT_SRC_DIR = KARTAN_ROOT / "data/geodata/boundaries"

# ── Output path ───────────────────────────────────────────────────────────────
OUT_DIR = Path(os.environ.get("GEO_MAP_FX_DATA_DIR", r"E:\Kartan\geo-map-fx\geodata"))

SIMPLIFY_TOLERANCE_DEG = 0.0008   # ~89m at Sweden's latitude — good for districts
COORD_PRECISION = 3                # 3 decimal places ≈ 111m


def _round_coords(geojson_str: str, precision: int) -> str:
    """Round all coordinates in a GeoJSON string to `precision` decimal places."""
    import re
    return re.sub(
        r'(-?\d+\.\d+)',
        lambda m: str(round(float(m.group()), precision)),
        geojson_str,
    )


def build_municipalities(out_dir: Path) -> Path:
    print("Building sweden_municipalities.geojson...")
    gdf = gpd.read_file(MUNICIPALITIES_SRC)

    # Ensure WGS84
    if gdf.crs is None:
        gdf = gdf.set_crs("EPSG:4326")
    elif gdf.crs.to_epsg() != 4326:
        gdf = gdf.to_crs("EPSG:4326")

    # Normalize columns — keep only what we need
    keep = [c for c in ["kommun_kod", "namn", "lan_kod", "lan_namn", "geometry"] if c in gdf.columns]
    gdf = gdf[keep].copy()

    # Fix invalid geometries
    gdf["geometry"] = gdf["geometry"].apply(make_valid)

    out = out_dir / "sweden_municipalities.geojson"
    raw = gdf.to_json(show_bbox=False, drop_id=True)
    out.write_text(_round_coords(raw, COORD_PRECISION), encoding="utf-8")
    print(f"  -> {len(gdf)} features -> {out}")
    return out


def build_regions(out_dir: Path) -> Path:
    print("Building sweden_regions.geojson...")
    gdf = gpd.read_file(out_dir / "sweden_municipalities.geojson")

    # Re-validate after coordinate rounding may have introduced degenerate edges
    gdf["geometry"] = gdf["geometry"].apply(make_valid)

    # Dissolve by lan_kod
    regions = gdf.dissolve(by="lan_kod", as_index=False)[["lan_kod", "lan_namn", "geometry"]]
    regions = regions.rename(columns={"lan_namn": "namn"})
    # lan_namn may not dissolve perfectly — keep first value per group
    name_map = gdf.groupby("lan_kod")["lan_namn"].first()
    regions["namn"] = regions["lan_kod"].map(name_map)

    # Fix geometries
    regions["geometry"] = regions["geometry"].apply(make_valid)

    out = out_dir / "sweden_regions.geojson"
    raw = regions.to_json(show_bbox=False, drop_id=True)
    out.write_text(_round_coords(raw, COORD_PRECISION), encoding="utf-8")
    print(f"  -> {len(regions)} features -> {out}")
    return out


def build_valdistrikt(out_dir: Path) -> Path:
    print("Building sweden_valdistrikt.geojson...")

    vd_files = sorted(VALDISTRIKT_SRC_DIR.glob("VD_*.json"))
    if not vd_files:
        raise FileNotFoundError(f"No VD_*.json files found in {VALDISTRIKT_SRC_DIR}")

    frames = []
    for f in vd_files:
        print(f"  Loading {f.name}...")
        with open(f, encoding="utf-8") as fh:
            raw = json.load(fh)

        features = []
        for feat in raw.get("features", []):
            props = feat["properties"]
            lkfv = props.get("Lkfv", "")
            features.append({
                "valdistrikt_kod": lkfv,
                "namn": props.get("Vdnamn", ""),
                "kommun_kod": lkfv[:4] if len(lkfv) >= 4 else "",
                "lan_kod": lkfv[:2] if len(lkfv) >= 2 else "",
                "geometry": feat["geometry"],
            })

        if not features:
            continue

        # Build GeoDataFrame from raw dicts — source CRS is SWEREF99 TM
        from shapely.geometry import shape
        gdf_part = gpd.GeoDataFrame(
            [{k: v for k, v in r.items() if k != "geometry"} for r in features],
            geometry=[shape(r["geometry"]) for r in features],
            crs="EPSG:3006",
        )
        frames.append(gdf_part)

    if not frames:
        raise ValueError("No valdistrikt features loaded")

    gdf = pd.concat(frames, ignore_index=True)
    gdf = gpd.GeoDataFrame(gdf, crs="EPSG:3006")

    # Simplify in metric CRS (50m tolerance)
    gdf["geometry"] = gdf["geometry"].simplify(50, preserve_topology=True)

    # Fix invalid geometries
    gdf["geometry"] = gdf["geometry"].apply(make_valid)

    # Reproject to WGS84
    gdf = gdf.to_crs("EPSG:4326")

    out = out_dir / "sweden_valdistrikt.geojson"
    raw = gdf.to_json(show_bbox=False, drop_id=True)
    out.write_text(_round_coords(raw, COORD_PRECISION), encoding="utf-8")
    print(f"  -> {len(gdf)} features -> {out}")
    return out


def validate(out_dir: Path) -> None:
    print("\nValidating outputs...")
    for name in ["sweden_municipalities.geojson", "sweden_regions.geojson", "sweden_valdistrikt.geojson"]:
        path = out_dir / name
        if not path.exists():
            print(f"  MISSING: {name}")
            continue
        gdf = gpd.read_file(path)
        invalid = gdf[~gdf.is_valid]
        size_mb = path.stat().st_size / 1_048_576
        print(f"  {name}: {len(gdf)} features, {size_mb:.1f} MB, {len(invalid)} invalid geometries")
        print(f"    columns: {list(gdf.columns)}")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Output directory: {OUT_DIR}\n")

    if not MUNICIPALITIES_SRC.exists():
        sys.exit(f"Source not found: {MUNICIPALITIES_SRC}\nSet KARTAN_ROOT env var if needed.")
    if not VALDISTRIKT_SRC_DIR.exists():
        sys.exit(f"Valdistrikt dir not found: {VALDISTRIKT_SRC_DIR}")

    build_municipalities(OUT_DIR)
    build_regions(OUT_DIR)
    build_valdistrikt(OUT_DIR)
    validate(OUT_DIR)
    print("\nDone.")


if __name__ == "__main__":
    main()
