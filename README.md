# 1) (once) create & activate venv				
python3 -m venv .venv				
source .venv/bin/activate				
				
# 2) install deps				
pip install geopandas pandas				
				
# 3) run with defaults (expects TRREBxLENDSTRAIT-202507.csv in the folder)				
python prejoin.py \				
--geojson "/Users/xavier.robitaille/cashr/client/data/torontoHugo - 2025-08-31 - Final.geojson" \				
--csv "/Users/xavier.robitaille/cashr/client/data/TRREBxLENDSTRAIT-202507.csv" \				
--out "/Users/xavier.robitaille/cashr/client/data/kepler_prejoined_hardcoded.geojson"				
Joining on -> GeoJSON: 'TRREB Area'  CSV: 'TRREB Area'				
⚠️  51 CSV names didn’t match a polygon. See unmatched_in_csv.csv				
⚠️  35 polygons didn’t find CSV data. See unmatched_in_geojson.csv				
✅ Wrote /Users/xavier.robitaille/cashr/client/data/kepler_prejoined_hardcoded.geojson				
