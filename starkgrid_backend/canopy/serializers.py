from rest_framework import serializers
from rest_framework_gis.fields import GeometryField


DEFAULT_BINS = [0, 20, 40, 60, 80, 100]


class ForestDensityStatsRequestSerializer(serializers.Serializer):
    geometry = GeometryField()
    threshold = serializers.DecimalField(
        max_digits=5, decimal_places=2, min_value=0, max_value=100, required=False, default=60
    )
    bins = serializers.ListField(
        child=serializers.DecimalField(max_digits=5, decimal_places=2, min_value=0, max_value=100),
        allow_empty=False,
        required=False,
    )

    def validate_bins(self, value):
        # Ensure bins are ascending and cover at least two edges.
        floats = [float(v) for v in value]
        if len(floats) < 2:
            raise serializers.ValidationError("Provide at least two bin edges.")
        if sorted(floats) != floats:
            raise serializers.ValidationError("Bins must be in ascending order.")
        if floats[0] != 0 or floats[-1] != 100:
            raise serializers.ValidationError("Bins must start at 0 and end at 100.")
        return floats

    def validate_geometry(self, value):
        # Normalize SRID to WGS84 for downstream queries.
        if value.srid is None:
            value.srid = 4326
        elif value.srid != 4326:
            value.transform(4326)
        return value
