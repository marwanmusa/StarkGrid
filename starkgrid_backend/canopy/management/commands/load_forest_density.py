import json
from decimal import Decimal
from pathlib import Path
from typing import Dict, Iterable, Iterator

from django.contrib.gis.geos import GEOSGeometry
from django.core.management.base import BaseCommand, CommandError

from canopy.models import ForestDensityCell


class Command(BaseCommand):
    help = (
        "Load forest density polygons from GeoJSON or newline-delimited GeoJSON into "
        "the ForestDensityCell table."
    )

    def add_arguments(self, parser) -> None:
        parser.add_argument(
            "--input",
            required=True,
            help="Path to a GeoJSON FeatureCollection or newline-delimited GeoJSON file.",
        )
        parser.add_argument(
            "--source",
            default=None,
            help="Source identifier to apply to all records; overrides any per-feature value.",
        )
        parser.add_argument(
            "--canopy-field",
            default="canopy_pct",
            help="Name of the property that stores canopy percentage (default: canopy_pct).",
        )
        parser.add_argument(
            "--tile-id-field",
            default="tile_id",
            help="Name of the property that stores a tile/scene identifier (default: tile_id).",
        )
        parser.add_argument(
            "--srid",
            type=int,
            default=4326,
            help="SRID to apply when reading geometries (default: 4326).",
        )
        parser.add_argument(
            "--chunk-size",
            type=int,
            default=500,
            help="Number of features to buffer before bulk inserting.",
        )
        parser.add_argument(
            "--replace",
            action="store_true",
            help="Delete existing ForestDensityCell rows for the provided --source before loading.",
        )

    def handle(self, *args, **options) -> None:
        input_path = Path(options["input"])
        source_override = options["source"]
        canopy_field = options["canopy_field"]
        tile_id_field = options["tile_id_field"]
        srid = options["srid"]
        chunk_size = options["chunk_size"]
        replace = options["replace"]

        if not input_path.exists():
            raise CommandError(f"Input file not found: {input_path}")

        if chunk_size < 1:
            raise CommandError("--chunk-size must be a positive integer.")

        if replace and not source_override:
            raise CommandError("--replace requires --source to be provided.")

        if replace:
            deleted, _ = ForestDensityCell.objects.filter(source=source_override).delete()
            self.stdout.write(
                self.style.WARNING(
                    f"Deleted {deleted} existing ForestDensityCell rows for source '{source_override}'."
                )
            )

        created_total = 0
        buffer: list[ForestDensityCell] = []

        for index, feature in enumerate(self._iter_features(input_path), start=1):
            buffer.append(
                self._feature_to_instance(
                    feature=feature,
                    feature_index=index,
                    srid=srid,
                    canopy_field=canopy_field,
                    tile_id_field=tile_id_field,
                    source_override=source_override,
                )
            )

            if len(buffer) >= chunk_size:
                created_total += self._bulk_insert(buffer, chunk_size)
                buffer.clear()

        if buffer:
            created_total += self._bulk_insert(buffer, chunk_size)

        self.stdout.write(
            self.style.SUCCESS(
                f"Inserted {created_total} forest density cells from {input_path}."
            )
        )

    def _iter_features(self, input_path: Path) -> Iterator[Dict]:
        """
        Yield GeoJSON features from a FeatureCollection file or newline-delimited
        GeoJSON file. Raises CommandError if the payload is not valid JSON.
        """
        with input_path.open() as file_handle:
            try:
                data = json.load(file_handle)
            except json.JSONDecodeError:
                file_handle.seek(0)
                for line_number, line in enumerate(file_handle, start=1):
                    stripped = line.strip()
                    if not stripped:
                        continue
                    try:
                        yield json.loads(stripped)
                    except json.JSONDecodeError as exc:
                        raise CommandError(
                            f"Invalid JSON on line {line_number}: {exc}"
                        ) from exc
            else:
                if isinstance(data, dict) and data.get("type") == "FeatureCollection":
                    for feature in data.get("features", []):
                        yield feature
                elif isinstance(data, dict) and data.get("type") == "Feature":
                    yield data
                else:
                    raise CommandError(
                        "Input JSON must be a FeatureCollection, single Feature, "
                        "or newline-delimited GeoJSON Features."
                    )

    def _feature_to_instance(
        self,
        *,
        feature: Dict,
        feature_index: int,
        srid: int,
        canopy_field: str,
        tile_id_field: str,
        source_override: str | None,
    ) -> ForestDensityCell:
        geometry = feature.get("geometry")
        if not geometry:
            raise CommandError(f"Feature {feature_index} is missing geometry.")

        try:
            geom = GEOSGeometry(json.dumps(geometry), srid=srid)
        except (TypeError, ValueError) as exc:
            raise CommandError(f"Feature {feature_index} has invalid geometry: {exc}") from exc

        properties = feature.get("properties") or {}

        canopy_value = properties.get(canopy_field)
        if canopy_value is None:
            raise CommandError(
                f"Feature {feature_index} is missing canopy field '{canopy_field}'."
            )

        try:
            canopy_pct = Decimal(str(canopy_value))
        except (TypeError, ValueError) as exc:
            raise CommandError(
                f"Feature {feature_index} has invalid canopy value '{canopy_value}': {exc}"
            ) from exc

        source_value = (
            source_override
            or properties.get("source")
            or properties.get("dataset")
            or "unknown"
        )

        tile_id_value = properties.get(tile_id_field, "") or ""

        return ForestDensityCell(
            geom=geom,
            canopy_pct=canopy_pct,
            source=source_value,
            tile_id=tile_id_value,
        )

    @staticmethod
    def _bulk_insert(instances: Iterable[ForestDensityCell], batch_size: int) -> int:
        instances_list = instances if isinstance(instances, list) else list(instances)
        ForestDensityCell.objects.bulk_create(instances_list, batch_size=batch_size)
        return len(instances_list)
