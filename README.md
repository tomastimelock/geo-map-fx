# geo-map-fx

Geographic choropleth map renderer for Sweden — static PNG/SVG and interactive HTML widgets from `{region_id: value}` dicts.

## Install

```bash
pip install geo-map-fx
```

## Usage

```python
from geo_map_fx import MapRenderer

r = MapRenderer()
png = r.render_municipalities(
    values={"0180": 42.5, "0381": 18.2},
    scope="01",
    palette="YlOrRd",
    title="My Map",
)
```
