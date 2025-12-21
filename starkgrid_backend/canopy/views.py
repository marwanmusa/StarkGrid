from rest_framework.response import Response
from rest_framework.views import APIView

from canopy.serializers import DEFAULT_BINS, ForestDensityStatsRequestSerializer
from canopy.services.forest_density import compute_stats


class ForestDensityStatsView(APIView):
    """
    Accepts a GeoJSON polygon and returns canopy statistics for the intersection.
    """

    def post(self, request, *args, **kwargs):
        serializer = ForestDensityStatsRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        geometry = serializer.validated_data["geometry"]
        threshold = float(serializer.validated_data.get("threshold", 60))
        bins = serializer.validated_data.get("bins") or DEFAULT_BINS

        stats = compute_stats(geometry=geometry, threshold=threshold, bins=bins)
        return Response(stats)


class ForestDensityLegendView(APIView):
    """
    Returns the default legend configuration for the forest density layer.
    """

    def get(self, request, *args, **kwargs):
        # Simple, readable ramp; frontend can override if needed.
        colors = ["#f7fcf5", "#c7e9c0", "#74c476", "#31a354", "#006d2c"]
        return Response(
            {
                "bin_edges": DEFAULT_BINS,
                "colors": colors,
                "title": "Forest canopy cover (%)",
                "description": "Canopy cover percentage per grid cell.",
            }
        )
