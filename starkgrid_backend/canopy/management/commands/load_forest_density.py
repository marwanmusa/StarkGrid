import gzip
import json
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional

from django.contrib.gis.geos import GEOSGeometry
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from canopy.models import ForestDensityCell


class Command(BaseCommand):
    help = "Load pre-aggregated forest density polygons into the database."

    def add_arguments(self, parser):
        parser.add_argument(
            "--file",
            "-f",
            required=True,
            help="Path to GeoJSON/NDJSON of polygons with canopy_pct property (optionally gzip compressed).",
        )
        parser.add_argument(
            "--source",
            default=None,
            help="Dataset/source label to store. Defaults to feature property 'source' or 'unknown'.",
        )
        parser.add_argument(
            "--tile-id-field",
            default="tile_id",
            help="Feature property containing tile/scene id. Defaults to 'tile_id'.",
        )
        parser.add_argument(
            "--canopy-field",
            default="canopy_pct",
            help="Feature property containing canopy percentage value. Defaults to 'canopy_pct'.",
        )
        parser.add_argument(
            "--batch-size",
            type=int,
            default=500,
            help="Bulk insert batch size. Defaults to 500.",
        )
        parser.add_argument(
            "--srid",
            type=int,
            default=4326,
            help="SRID of incoming geometries. Defaults to 4326 (WGS84).",
        )

    def handle(self, *args, **options):
        path = Path(options["file"])
        if not path.exists():
            raise CommandError(f"Input file not found: {path}")

        source_override = options["source"]
        tile_field = options["tile_id_field"]
        canopy_field = options["canopy_field"]
        batch_size = options["batch_size"]
        srid = options["srid"]

        created = 0
        batch: List[ForestDensityCell] = []

        self.stdout.write(f"Loading features from {path} ...")

        for feature in self._iter_features(path):
            geom = feature.get("geometry")
            if not geom:
                self.stderr.write("Skipping feature with no geometry.")
                continue

            props: Dict[str, Any] = feature.get("properties") or {}
            canopy_pct = props.get(canopy_field)
            if canopy_pct is None:
                self.stderr.write("Skipping feature with no canopy percentage value.")
                continue

            tile_id = props.get(tile_field, "")
            row_source = source_override or props.get("source") or "unknown"

            try:
                geom_obj = GEOSGeometry(json.dumps(geom), srid=srid)
            except Exception as exc:  # pragma: no cover - safety net
                self.stderr.write(f"Skipping invalid geometry: {exc}")
                continue

            batch.append(
                ForestDensityCell(
                    geom=geom_obj,
                    canopy_pct=canopy_pct,
                    source=row_source,
                    tile_id=tile_id,
                )
            )

            if len(batch) >= batch_size:
                self._bulk_insert(batch)
                created += len(batch)
                self.stdout.write(f"Inserted {created} rows...")
                batch = []

        if batch:
            self._bulk_insert(batch)
            created += len(batch)

        self.stdout.write(self.style.SUCCESS(f"Done. Inserted {created} rows."))

    def _bulk_insert(self, batch: List[ForestDensityCell]) -> None:
        # Bulk create inside a transaction to keep batches atomic.
        with transaction.atomic():
            ForestDensityCell.objects.bulk_create(batch, ignore_conflicts=True)

    def _iter_features(self, path: Path) -> Iterator[Dict[str, Any]]:
        """
        Yields GeoJSON features from a GeoJSON FeatureCollection file
        or newline-delimited GeoJSON (NDJSON). Supports gzip-compressed
        inputs when the filename ends with '.gz'.
        """
        is_gz = path.suffix == ".gz"
        opener = gzip.open if is_gz else open
        inner_path = path.with_suffix("") if is_gz else path

        with opener(path, "rt", encoding="utf-8") as handle:
            if inner_path.suffix.lower() in {".ndjson", ".jsonl"}:
                for line in handle:
                    line = line.strip()
                    if not line:
                        continue
                    feature = json.loads(line)
                    yield feature
                return

            # Otherwise treat as standard GeoJSON FeatureCollection.
            data = json.load(handle)
            if data.get("type") == "FeatureCollection":
                for feature in data.get("features", []):
                    yield feature
            elif data.get("type") == "Feature":
                yield data
            else:
                raise CommandError("Unrecognized GeoJSON structure; expected Feature or FeatureCollection.")
