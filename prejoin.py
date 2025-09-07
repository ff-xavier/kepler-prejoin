#!/usr/bin/env python3
import re
import argparse
from pathlib import Path
import pandas as pd
import geopandas as gpd

# ----------------- helpers -----------------
def find_key(cols, candidates):
    """Return the first column in cols that case-insensitively matches any candidate."""
    low = {c.lower(): c for c in cols}
    for cand in candidates:
        if cand.lower() in low:
            return low[cand.lower()]
    return None

def normalize_key(series):
    return (
        series.astype(str)
        .str.strip()
        .str.replace(r"\s+", " ", regex=True)
        .str.upper()
    )

def clean_numeric(x):
    if pd.isna(x):
        return pd.NA
    s = str(x).strip()
    if not s:
        return pd.NA
    # remove currency / percent / thousands separators / spaces
    s = s.replace("$", "").replace("%", "").replace(",", "").replace(" ", "")
    s = re.sub(r"[^\d\.\-\+eE]", "", s)
    try:
        return float(s)
    except Exception:
        return pd.NA

# ---- flexible, case/space/punct-insensitive column renamer ----
def _norm(s: str) -> str:
    """lowercase and strip all non-alphanumerics so 'Average Price' == 'average_price' == 'AveragePrice'"""
    return re.sub(r"[^a-z0-9]", "", s.lower())

RENAME_RULES = [
    (["Sales"], "TRREB Sales"),
    (["Average Price", "Avg Price", "AveragePrice"], "TRREB Average Price"),
    (["Dollar Volume", "Total Dollar Volume", "$ Volume", "DollarVolume"], "TRREB Dollar Volume"),
]

def apply_fuzzy_renames(df: pd.DataFrame) -> dict:
    """
    Return the mapping applied and rename df columns in-place using RENAME_RULES.
    Matches are case/space/punctuation-insensitive; first candidate that exists wins.
    """
    by_norm = {_norm(c): c for c in df.columns}
    to_rename = {}
    for candidates, new_name in RENAME_RULES:
        for cand in candidates:
            src = by_norm.get(_norm(cand))
            if src:
                to_rename[src] = new_name
                break
    if to_rename:
        df.rename(columns=to_rename, inplace=True)
    return to_rename

# ----------------- main -----------------
def main():
    p = argparse.ArgumentParser(description="Join CSV columns into a GeoJSON by district/area name.")
    p.add_argument("--geojson", "-g", default="torontoHugo.geojson", help="Input GeoJSON path")
    p.add_argument("--csv", "-c", default="TRREBxLENDSTRAIT-202507.csv",
                   help="Input CSV path (all columns will be merged)")
    p.add_argument("--out", "-o", default="merged.geojson", help="Output GeoJSON path")
    p.add_argument("--left-key", help="Explicit join key in GeoJSON (overrides auto-detect)")
    p.add_argument("--right-key", help="Explicit join key in CSV (overrides auto-detect)")
    p.add_argument("--no-clean", action="store_true", help="Do NOT attempt numeric cleaning")
    args = p.parse_args()

    geo_path = Path(args.geojson)
    csv_path = Path(args.csv)
    out_path = Path(args.out)

    # Load
    gdf = gpd.read_file(geo_path)
    df  = pd.read_csv(csv_path, dtype=str)

    # Fix blank first CSV header -> District
    first_col = df.columns[0]
    if not first_col.strip() or first_col.startswith("Unnamed"):
        df = df.rename(columns={first_col: "District"})

    # Rename selected CSV columns to desired output names (before cleaning/merge)
    applied = apply_fuzzy_renames(df)
    if applied:
        print("Renamed CSV columns ->", applied)

    # Auto-detect join keys if not provided
    candidates = ["District", "TRREB Area", "Name", "Region", "F1", "Area"]
    left_key  = args.left_key  or find_key(gdf.columns, candidates)
    right_key = args.right_key or find_key(df.columns,  candidates)

    if left_key is None or right_key is None:
        raise SystemExit(
            "Could not find join keys.\n"
            f"GeoJSON columns: {list(gdf.columns)}\n"
            f"CSV columns:     {list(df.columns)}\n"
            "Tip: pass --left-key and/or --right-key explicitly."
        )

    print(f"Joining on -> GeoJSON: '{left_key}'  CSV: '{right_key}'")

    # Normalize keys
    gdf["_JOIN_KEY_"] = normalize_key(gdf[left_key])
    df ["_JOIN_KEY_"] = normalize_key(df [right_key])

    # Optional numeric cleaning on every CSV column except the key
    if not args.no_clean:
        for c in df.columns:
            if c == "_JOIN_KEY_":
                continue
            df[c] = df[c].apply(clean_numeric)

    # Merge (left join: keep all polygons)
    merged = gdf.merge(df, on="_JOIN_KEY_", how="left", suffixes=("","_csv"))

    # Diagnostics: who didn't match?
    csv_only = df [~df["_JOIN_KEY_"].isin(gdf["_JOIN_KEY_"])]
    geo_only = gdf[~gdf["_JOIN_KEY_"].isin(df ["_JOIN_KEY_"])][[left_key]]

    if not csv_only.empty:
        csv_only.to_csv("unmatched_in_csv.csv", index=False)
        print(f"⚠️  {len(csv_only)} CSV names didn’t match a polygon. See unmatched_in_csv.csv")

    if not geo_only.empty:
        geo_only.to_csv("unmatched_in_geojson.csv", index=False)
        print(f"⚠️  {len(geo_only)} polygons didn’t find CSV data. See unmatched_in_geojson.csv")

    # Drop helper key
    merged = merged.drop(columns=["_JOIN_KEY_"], errors="ignore")

    # Replace <NA> / NaN with empty string (Kepler-friendly)
    merged = merged.fillna("")

    # Save
    merged.to_file(out_path, driver="GeoJSON")
    print(f"✅ Wrote {out_path.resolve()}")

if __name__ == "__main__":
    main()
