import json
from decimal import Decimal
from pathlib import Path
from tempfile import TemporaryDirectory

from django.contrib.gis.geos import Polygon
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase

from canopy.models import ForestDensityCell


class LoadForestDensityCommandTests(TestCase):
    def setUp(self) -> None:
        self.geometry = {
            "type": "Polygon",
            "coordinates": [
                [
                    [0.0, 0.0],
                    [0.0, 1.0],
                    [1.0, 1.0],
                    [1.0, 0.0],
                    [0.0, 0.0],
                ]
            ],
        }

    def test_loads_feature_collection_into_database(self) -> None:
        with TemporaryDirectory() as tmpdir:
            input_path = Path(tmpdir) / "cells.geojson"
            feature_collection = {
                "type": "FeatureCollection",
                "features": [
                    {
                        "type": "Feature",
                        "geometry": self.geometry,
                        "properties": {"canopy_pct": 42.5, "tile_id": "A1"},
                    },
                    {
                        "type": "Feature",
                        "geometry": self.geometry,
                        "properties": {"canopy_pct": 55.1, "tile_id": "A2"},
                    },
                ],
            }
            input_path.write_text(json.dumps(feature_collection))

            call_command(
                "load_forest_density",
                "--input",
                str(input_path),
                "--source",
                "test_source",
                "--chunk-size",
                "1",
            )

            cells = ForestDensityCell.objects.order_by("tile_id")
            self.assertEqual(cells.count(), 2)
            self.assertEqual(cells[0].source, "test_source")
            self.assertEqual(cells[0].tile_id, "A1")
            self.assertEqual(cells[0].canopy_pct, Decimal("42.5"))
            self.assertEqual(cells[1].canopy_pct, Decimal("55.1"))

    def test_replace_flag_overwrites_existing_source(self) -> None:
        ForestDensityCell.objects.create(
            geom=Polygon(((0, 0), (0, 1), (1, 1), (1, 0), (0, 0))),
            canopy_pct=10,
            source="replace_me",
        )

        with TemporaryDirectory() as tmpdir:
            input_path = Path(tmpdir) / "cells.ndjson"
            features = [
                {
                    "type": "Feature",
                    "geometry": self.geometry,
                    "properties": {"canopy_pct": 75.0, "tile_id": "B1", "source": "replace_me"},
                }
            ]
            input_path.write_text("\n".join(json.dumps(item) for item in features))

            call_command(
                "load_forest_density",
                "--input",
                str(input_path),
                "--source",
                "replace_me",
                "--replace",
                "--chunk-size",
                "2",
            )

            cells = ForestDensityCell.objects.filter(source="replace_me")
            self.assertEqual(cells.count(), 1)
            self.assertEqual(cells[0].tile_id, "B1")
            self.assertEqual(cells[0].canopy_pct, Decimal("75.0"))

    def test_missing_canopy_field_raises_command_error(self) -> None:
        with TemporaryDirectory() as tmpdir:
            input_path = Path(tmpdir) / "invalid.geojson"
            feature_collection = {
                "type": "FeatureCollection",
                "features": [
                    {"type": "Feature", "geometry": self.geometry, "properties": {}},
                ],
            }
            input_path.write_text(json.dumps(feature_collection))

            with self.assertRaises(CommandError):
                call_command(
                    "load_forest_density",
                    "--input",
                    str(input_path),
                    "--source",
                    "error_source",
                )
