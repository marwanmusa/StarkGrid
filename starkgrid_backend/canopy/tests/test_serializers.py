from django.contrib.gis.geos import Polygon
from django.test import SimpleTestCase

from canopy.serializers import ForestDensityStatsRequestSerializer


class ForestDensityStatsSerializerTests(SimpleTestCase):
    def setUp(self):
        self.poly_geojson = Polygon(
            ((0, 0), (1, 0), (1, 1), (0, 1), (0, 0))
        ).geojson

    def test_valid_payload_normalizes_geometry(self):
        serializer = ForestDensityStatsRequestSerializer(
            data={"geometry": self.poly_geojson, "threshold": 50}
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
        geom = serializer.validated_data["geometry"]
        self.assertEqual(geom.srid, 4326)
        self.assertEqual(serializer.validated_data["threshold"], 50)

    def test_invalid_bins_order(self):
        serializer = ForestDensityStatsRequestSerializer(
            data={"geometry": self.poly_geojson, "bins": [0, 40, 20, 100]}
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn("Bins must be in ascending order.", str(serializer.errors))

    def test_bins_must_start_and_end_correctly(self):
        serializer = ForestDensityStatsRequestSerializer(
            data={"geometry": self.poly_geojson, "bins": [10, 20, 100]}
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn("Bins must start at 0 and end at 100.", str(serializer.errors))
