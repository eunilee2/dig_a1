#!/usr/bin/env python3
"""
Single-row faceted choropleth by ZIP for selected years (no GeoPandas).

Inputs in the same folder:
  - allegheny-county-zip-code-boundaries.geojson
  - fatal_overdoses_allegheny_only.csv  (needs: incident_zip, case_year)

Output:
  - faceted_choropleth_zip_years_row.png
"""

from pathlib import Path
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from matplotlib.colors import Normalize
from matplotlib.cm import ScalarMappable, get_cmap

# ----------------------------
# CONFIG
# ----------------------------
GEOJSON_PATH = Path("./data/allegheny-county-zip-code-boundaries.geojson")
CSV_PATH     = Path("./data/fatal_overdoses_allegheny_only.csv")

YEARS        = [2007, 2016, 2017, 2023]   # facets (all will be in one row)
FIG_PER_PLOT_WIDTH = 3.2                  # width per small multiple (inches)
FIG_HEIGHT         = 4.0                  # total figure height (inches)
CMAP_NAME    = "Reds"
EDGE_COLOR   = "black"
EDGE_WIDTH   = 0.35
TITLE        = "Fatal Overdose Cases by ZIP (Selected Years)"
CBAR_LABEL   = "Case count"
CBAR_PAD     = 0.12                       # distance between subplots and colorbar
CBAR_HEIGHT  = 0.04                       # relative height of colorbar (as fraction of figure height)

# Optional: label the top-K ZIPs in each facet (set 0 to disable)
DRAW_TOP_K_LABELS = 0
LABEL_FONTSIZE    = 6

# ----------------------------
# helpers
# ----------------------------
def _exterior_from_rings(rings):
    if not rings: return None
    arr = np.asarray(rings[0], dtype=float)
    if arr.ndim != 2 or arr.shape[1] != 2: return None
    return arr

def _polygon_centroid(coords):
    if coords is None or len(coords) == 0: return None
    x = coords[:, 0]; y = coords[:, 1]
    a = x[:-1]*y[1:] - x[1:]*y[:-1]
    A = a.sum()/2.0
    if A == 0: return (x.mean(), y.mean())
    cx = ((x[:-1] + x[1:]) * a).sum() / (6.0*A)
    cy = ((y[:-1] + y[1:]) * a).sum() / (6.0*A)
    return (cx, cy)

# ----------------------------
# load data
# ----------------------------
if not GEOJSON_PATH.exists(): raise SystemExit(f"GeoJSON not found: {GEOJSON_PATH}")
if not CSV_PATH.exists():     raise SystemExit(f"CSV not found: {CSV_PATH}")

with GEOJSON_PATH.open("r") as f:
    gj = json.load(f)
features = gj.get("features", [])
if not features: raise SystemExit("No features in GeoJSON.")

df = pd.read_csv(CSV_PATH)
required = {"incident_zip", "case_year"}
missing = required - set(df.columns)
if missing: raise SystemExit(f"CSV missing required columns: {missing}")
df["incident_zip"] = df["incident_zip"].astype(str).str.zfill(5)
df["case_year"]    = pd.to_numeric(df["case_year"], errors="coerce")

# ----------------------------
# geometry cache
# ----------------------------
poly_zip, poly_geom, poly_centroid = [], [], []
for feat in features:
    props = feat.get("properties", {}) or {}
    z = str(props.get("ZIP", "")).zfill(5)
    geom = feat.get("geometry", {}) or {}
    gtype = geom.get("type"); coords = geom.get("coordinates")

    if not gtype or coords is None: continue
    if gtype == "Polygon":
        ext = _exterior_from_rings(coords)
        if ext is not None:
            poly_zip.append(z); poly_geom.append(ext); poly_centroid.append(_polygon_centroid(ext))
    elif gtype == "MultiPolygon":
        for poly in coords:
            ext = _exterior_from_rings(poly)
            if ext is not None:
                poly_zip.append(z); poly_geom.append(ext); poly_centroid.append(_polygon_centroid(ext))

if not poly_geom: raise SystemExit("No polygon exteriors extracted.")

# ----------------------------
# aggregate counts per ZIP × year
# ----------------------------
counts = (
    df.groupby(["case_year", "incident_zip"])
      .size()
      .reset_index(name="case_count")
)
counts_sel = counts[counts["case_year"].isin(YEARS)]
global_min = counts_sel["case_count"].min() if not counts_sel.empty else 0
global_max = counts_sel["case_count"].max() if not counts_sel.empty else 1
norm = Normalize(vmin=global_min, vmax=global_max)
cmap = get_cmap(CMAP_NAME)

# ----------------------------
# figure & axes (single row)
# ----------------------------
n = len(YEARS)
fig_w = max(8.0, FIG_PER_PLOT_WIDTH * n)         # total width scales with number of facets
fig_h = FIG_HEIGHT
fig, axes = plt.subplots(nrows=1, ncols=n, figsize=(fig_w, fig_h), squeeze=False)
axes = axes[0]  # flatten to 1D


# render each year panel
for i, year in enumerate(YEARS):
    ax = axes[i]
    df_y = counts[counts["case_year"] == year]
    zip_to_val = dict(zip(df_y["incident_zip"], df_y["case_count"]))
    vals = np.array([zip_to_val.get(z, 0) for z in poly_zip], dtype=float)

    facecolors = cmap(norm(vals))
    pc = PolyCollection(poly_geom, facecolors=facecolors,
                        edgecolors=EDGE_COLOR, linewidths=EDGE_WIDTH)
    ax.add_collection(pc)

    all_x = np.concatenate([p[:, 0] for p in poly_geom])
    all_y = np.concatenate([p[:, 1] for p in poly_geom])
    ax.set_xlim(all_x.min(), all_x.max())
    ax.set_ylim(all_y.min(), all_y.max())
    ax.set_aspect("equal", adjustable="box")
    ax.set_title(str(year), pad=6)
    ax.set_xticks([]); ax.set_yticks([])

    # List top 3 ZIPs with highest case counts for this year
    top3 = df_y.sort_values("case_count", ascending=False).head(3)
    top3_str = "\n".join([f"{row['incident_zip']}: {int(row['case_count'])}" for _, row in top3.iterrows()])
    # Place the text below the plot
    ax.text(0.5, -0.08, top3_str, ha="center", va="top", fontsize=9, transform=ax.transAxes, linespacing=1.2)

# shared title
fig.suptitle(TITLE, fontsize=14, y=0.97)


# ----------------------------
# shared horizontal colorbar at top, left-aligned
# ----------------------------
sm = ScalarMappable(norm=norm, cmap=cmap); sm.set_array([])
# [left, bottom, width, height] in figure fraction
cbar_ax = fig.add_axes([0.01, 0.85, 0.35, 0.025])  # move colorbar lower
cbar = fig.colorbar(sm, cax=cbar_ax, orientation="horizontal")
cbar.set_label(CBAR_LABEL, labelpad=2, loc='left')
cbar.ax.xaxis.set_label_position('top')

# layout
fig.tight_layout(rect=[0, 0, 1, 0.91])  # leave room for colorbar & title at top

OUT = Path("faceted_choropleth_zip_years_row.png")
fig.savefig(OUT, dpi=300, bbox_inches="tight")
print(f"Saved → {OUT.resolve()}")
