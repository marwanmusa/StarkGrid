from decimal import Decimal
from typing import Dict, Iterable, List, Tuple

from django.db import connection

from canopy.serializers import DEFAULT_BINS


def _pairwise_bins(edges: Iterable[float]) -> List[Tuple[float, float]]:
    floats = [float(v) for v in edges]
    return list(zip(floats[:-1], floats[1:]))


def compute_stats(geometry, threshold: float = 60, bins: List[float] = None) -> Dict:
    """
    Compute canopy statistics for a given polygon geometry.
    Returns mean canopy, total area, area above threshold, and area by bins.
    """
    bin_edges = bins or DEFAULT_BINS
    bin_pairs = _pairwise_bins(bin_edges)

    geom_wkb = geometry.ewkb

    with connection.cursor() as cursor:
        cursor.execute(
            """
            WITH clip AS (
                SELECT
                    canopy_pct,
                    ST_Area(
                        ST_Intersection(
                            geom::geography,
                            ST_GeomFromEWKB(%s)::geography
                        )
                    ) AS area_m2
                FROM canopy_forestdensitycell
                WHERE geom && ST_GeomFromEWKB(%s)
                  AND ST_Intersects(geom, ST_GeomFromEWKB(%s))
            )
            SELECT canopy_pct, SUM(area_m2) AS area_m2, COUNT(*) AS cell_count
            FROM clip
            WHERE area_m2 > 0
            GROUP BY canopy_pct
            """,
            [geom_wkb, geom_wkb, geom_wkb],
        )
        rows = cursor.fetchall()

    total_area = 0.0
    weighted_sum = 0.0
    area_above_threshold = 0.0
    pixel_count = 0

    # Collect area grouped by canopy_pct to aggregate into bins.
    pct_area_pairs: List[Tuple[float, float]] = []

    for canopy_pct, area_m2, count in rows:
        canopy_val = float(canopy_pct)
        area_val = float(area_m2 or 0)
        total_area += area_val
        weighted_sum += area_val * canopy_val
        if canopy_val >= float(threshold):
            area_above_threshold += area_val
        pixel_count += int(count or 0)
        pct_area_pairs.append((canopy_val, area_val))

    area_by_class: List[Dict[str, float]] = []
    for low, high in bin_pairs:
        area_bin = sum(area for pct, area in pct_area_pairs if low <= pct < high)
        area_by_class.append({"min": low, "max": high, "area_m2": area_bin})

    mean_canopy = weighted_sum / total_area if total_area > 0 else 0.0

    return {
        "mean_canopy": mean_canopy,
        "total_area_m2": total_area,
        "area_above_threshold_m2": area_above_threshold,
        "area_by_class": area_by_class,
        "pixel_count": pixel_count,
        "bin_edges": bin_edges,
        "threshold": float(threshold),
    }
