#!/usr/bin/env python3
"""
Choropleth by ZIP (Allegheny County) using plain matplotlib + pandas.

Inputs (expected to be in the same folder as this script by default):
  - allegheny-county-zip-code-boundaries.geojson
      * GeoJSON FeatureCollection; each feature has properties.ZIP and a Polygon/MultiPolygon geometry
  - fatal_overdoses_allegheny_only.csv
      * Tabular data with a column 'incident_zip' (ZIP per overdose row)

Outputs:
  - allegheny_overdose_choropleth.png       (choropleth image)
  - allegheny_zip_with_case_counts.geojson  (same boundaries with case_count injected per ZIP)

You can tweak the CONFIG section below for colors, figure size, output paths, etc.
"""

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection


# =========================
# ======= CONFIG ==========
# =========================
# Paths (relative or absolute). Change these if your files live elsewhere.
GEOJSON_PATH = Path("./data/allegheny-county-zip-code-boundaries.geojson")
CSV_PATH     = Path("./data/fatal_overdoses_allegheny_only.csv")

OUT_PNG      = Path("./data/allegheny_overdose_choropleth.png")
OUT_GEOJSON  = Path("./data/allegheny_zip_with_case_counts.geojson")

# Plot config
FIGSIZE      = (8, 8)          # inches
EDGE_COLOR   = "black"
EDGE_WIDTH   = 0.35
TITLE        = "Fatal Overdose Cases by ZIP (Allegheny County)"
CBAR_LABEL   = "Case count"
CMAP_NAME    = "viridis"       # any matplotlib colormap name, e.g., "viridis", "plasma", "magma", "Reds"

# Label options (set to True to draw ZIP labels at polygon centroids; rough but quick)
DRAW_LABELS  = False
LABEL_FIELD  = "ZIP"
LABEL_FONTSIZE = 3


# =========================
# ======= HELPERS =========
# =========================
def _exterior_from_rings(rings):
    """Return Nx2 array for the exterior ring (lon, lat). Ignore interior holes for a clean fill."""
    if not rings:
        return None
    # GeoJSON ring is [[lon, lat], ...]
    arr = np.asarray(rings[0], dtype=float)
    if arr.ndim != 2 or arr.shape[1] != 2:
        return None
    return arr

def _polygon_centroid(coords):
    """Simple centroid of a polygon exterior (approx; not geodesic)."""
    if coords is None or len(coords) == 0:
        return None
    x = coords[:, 0]
    y = coords[:, 1]
    # polygon centroid formula (shoelace)
    a = x[:-1] * y[1:] - x[1:] * y[:-1]
    A = a.sum() / 2.0
    if A == 0:
        return (x.mean(), y.mean())
    cx = ((x[:-1] + x[1:]) * a).sum() / (6.0 * A)
    cy = ((y[:-1] + y[1:]) * a).sum() / (6.0 * A)
    return (cx, cy)


# =========================
# ========= MAIN ==========
# =========================
def main():
    if not GEOJSON_PATH.exists():
        sys.exit(f"GeoJSON not found: {GEOJSON_PATH}")
    if not CSV_PATH.exists():
        sys.exit(f"CSV not found: {CSV_PATH}")

    # ---- Load GeoJSON ----
    with GEOJSON_PATH.open("r") as f:
        gj = json.load(f)
    features = gj.get("features", [])
    if not isinstance(features, list) or not features:
        sys.exit("No features found in GeoJSON (expect a FeatureCollection with 'features').")

    # ---- Load CSV & aggregate counts by ZIP ----
    df = pd.read_csv(CSV_PATH)
    if "incident_zip" not in df.columns:
        sys.exit("CSV must contain a column named 'incident_zip'.")

    df["incident_zip"] = df["incident_zip"].astype(str).str.zfill(5)
    counts = (
        df["incident_zip"]
        .value_counts(dropna=False)
        .rename_axis("incident_zip")
        .reset_index(name="case_count")
    )
    zip_to_count = dict(zip(counts["incident_zip"], counts["case_count"]))

    # ---- Build polygon list + values ----
    polys   = []    # list of Nx2 arrays
    values  = []    # parallel list of counts per polygon
    labels  = []    # centroid positions if labeling
    label_z = []    # label text (ZIP)

    for feat in features:
        props = feat.get("properties", {}) or {}
        z = str(props.get("ZIP", "")).zfill(5)
        geom = feat.get("geometry", {}) or {}
        gtype = geom.get("type")
        coords = geom.get("coordinates", None)

        if coords is None or gtype is None:
            continue

        if gtype == "Polygon":
            exterior = _exterior_from_rings(coords)
            if exterior is not None:
                polys.append(exterior)
                values.append(zip_to_count.get(z, 0))
                if DRAW_LABELS:
                    cen = _polygon_centroid(exterior)
                    if cen:
                        labels.append(cen)
                        label_z.append(z)
        elif gtype == "MultiPolygon":
            # plot each polygon separately with same ZIP value
            for poly in coords:
                exterior = _exterior_from_rings(poly)
                if exterior is not None:
                    polys.append(exterior)
                    values.append(zip_to_count.get(z, 0))
                    if DRAW_LABELS:
                        cen = _polygon_centroid(exterior)
                        if cen:
                            labels.append(cen)
                            label_z.append(z)
        # Ignore non-polygons

    if not polys:
        sys.exit("No polygons extracted from GeoJSON. Check geometry types.")

    values = np.array(values, dtype=float)

    # ---- Plot ----
    fig, ax = plt.subplots(figsize=FIGSIZE)

    pc = PolyCollection(polys, edgecolors=EDGE_COLOR, linewidths=EDGE_WIDTH)
    pc.set_array(values)
    pc.set_cmap(plt.get_cmap(CMAP_NAME))
    pc.set_clim(vmin=np.nanmin(values), vmax=np.nanmax(values))
    ax.add_collection(pc)

    # Fit view bounds
    all_x = np.concatenate([p[:, 0] for p in polys])
    all_y = np.concatenate([p[:, 1] for p in polys])
    ax.set_xlim(all_x.min(), all_x.max())
    ax.set_ylim(all_y.min(), all_y.max())
    ax.set_aspect("equal", adjustable="box")

    # Title & colorbar (scaled down legend)
    ax.set_title(TITLE, fontsize=16, pad=12)
    cbar = plt.colorbar(pc, ax=ax, shrink=0.6)   # shrink makes it smaller
    cbar.set_label(CBAR_LABEL)

    # --- Label top 5 ZIPs by count ---
    # Build a DataFrame to identify top 5
    df_counts = pd.DataFrame({
        "zip": [str((f.get("properties", {}) or {}).get("ZIP", "")).zfill(5) for f in features],
        "value": [zip_to_count.get(str((f.get("properties", {}) or {}).get("ZIP", "")).zfill(5), 0) for f in features],
        "geometry": [f.get("geometry") for f in features]
    })

    top5 = df_counts.sort_values("value", ascending=False).head(5)

    for _, row in top5.iterrows():
        z = row["zip"]
        v = row["value"]
        geom = row["geometry"]
        if geom and geom["type"] == "Polygon":
            exterior = _exterior_from_rings(geom["coordinates"])
        elif geom and geom["type"] == "MultiPolygon":
            exterior = _exterior_from_rings(geom["coordinates"][0])
        else:
            exterior = None

        if exterior is not None:
            cx, cy = _polygon_centroid(exterior)
            ax.text(
                cx, cy,
                f"{z}",                       # keep just the ZIP code (or f"{z}\n({v})" if you want counts too)
                ha="center", va="center",
                fontsize=6,                   # smaller text size (try 5–7)
                fontweight="normal",          # lighter than bold
                color="black",
                bbox=dict(
                    facecolor="white",
                    alpha=0.5,                # more transparent background
                    edgecolor="none",
                    boxstyle="round,pad=0.1"  # tighter box around the text
                )
            )

    # Clean axes
    ax.set_xticks([])
    ax.set_yticks([])

    # Save
    fig.savefig(OUT_PNG, dpi=300, bbox_inches="tight")
    print(f"Saved map → {OUT_PNG}")

    # ---- Write merged GeoJSON with case_count in properties ----
    merged = gj  # mutate in place is fine since we don't reuse gj
    for feat in merged.get("features", []):
        z = str((feat.get("properties", {}) or {}).get("ZIP", "")).zfill(5)
        feat.setdefault("properties", {})
        feat["properties"]["case_count"] = int(zip_to_count.get(z, 0))

    with OUT_GEOJSON.open("w") as f:
        json.dump(merged, f)
    print(f"Saved merged GeoJSON → {OUT_GEOJSON}")

if __name__ == "__main__":
    main()
