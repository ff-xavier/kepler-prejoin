# 1) (once) create & activate venv				
	# (optional) if a venv is currently active
	deactivate 2>/dev/null || true

	# clean any partial venv
	rm -rf .venv

	# 1) create the env
	python3 -m venv .venv

	# 2) activate it
	source .venv/bin/activate

	# verify
	which python
	python -V

	/Users/xavier.robitaille/dev/kepler-prejoin/.venv/bin/python
	Python 3.13.7

				
# 2) install deps				
	pip install geopandas pandas				
				
# 3) run with defaults (expects TRREBxLENDSTRAIT-202507.csv in the folder)				
	python3 prejoin.py --geojson "/Users/xavier.robitaille/cashr/client/data/TRREB Areas.geojson" --csv /Users/xavier.robitaille/cashr/client/data/TRREBxLENDSTRAIT-202507.csv --out "/Users/xavier.robitaille/cashr/client/data/Lendstrait x TRREB.geojson"
 
	// Joining on -> GeoJSON: 'TRREB Area'  CSV: 'TRREB Area'				
	// ⚠️  51 CSV names didn’t match a polygon. See unmatched_in_csv.csv				
	// ⚠️  35 polygons didn’t find CSV data. See unmatched_in_geojson.csv				
	// ✅ Wrote /Users/xavier.robitaille/cashr/client/data/kepler_prejoined_hardcoded.geojson				
