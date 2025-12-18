# StarkGrid Backend

Map-first climate intelligence backend for StarkGrid. Provides APIs for renewable energy planning with ecological context (forest density, forest loss, etc.).

## Stack
- Django 6 + Django REST Framework
- PostGIS (Supabase) via `django.contrib.gis.db.backends.postgis`
- GIS libs: GDAL, GEOS, `djangorestframework-gis`, `rasterio`, `rio-cogeo`
- Python 3.14 (Pipfile)

## Project layout
- `starkgrid_backend/` – Django project root
  - `manage.py` – management commands entry
  - `starkgrid_backend/settings.py` – base settings (GDAL/GEOS paths default to Homebrew)
  - `starkgrid_backend/local_settings.py` – DB config from env (`DB_PASSWORD`, etc.)
  - `canopy/` – forest/eco modules (`ForestDensityCell` model, admin)
 - `PRD.md` – product requirements

## Prerequisites
- Python 3.14
- PostGIS-enabled PostgreSQL (Supabase): run `create extension postgis;`
- macOS system libs (Homebrew paths assumed):
  - `brew install gdal geos`
  - Export if needed:
    ```bash
    export GDAL_LIBRARY_PATH=/opt/homebrew/opt/gdal/lib/libgdal.dylib
    export GEOS_LIBRARY_PATH=/opt/homebrew/opt/geos/lib/libgeos_c.dylib
    export GDAL_DATA=/opt/homebrew/share/gdal
    export PROJ_LIB=/opt/homebrew/share/proj
    ```

## Environment variables
Defined via `python-decouple`:
- `DJANGO_SECRET_KEY`
- `DB_PASSWORD` (used in `local_settings.py`)
- Optional overrides: `GDAL_LIBRARY_PATH`, `GEOS_LIBRARY_PATH`

## Setup
```bash
# from repo root
python -m venv venv
source venv/bin/activate
pip install pipenv  # if you prefer pipenv workflows
pipenv install      # or: pip install -r <(pipenv requirements --dev)

# apply DB schema
cd starkgrid_backend
python manage.py migrate
```

## Run
```bash
cd starkgrid_backend
python manage.py runserver
```

## Forest Density module (MVP)
- Model: `canopy.models.ForestDensityCell` (PolygonField SRID 4326, `canopy_pct`, `source`, `tile_id`, GIST + btree indexes).
- Admin: registered with GIS admin for inspection.
- Next steps: ingestion command to load canopy data into the grid; stats API to compute mean canopy, bins, and threshold coverage for user-supplied polygons.

## Testing
```bash
cd starkgrid_backend
python manage.py test
```
