from django.contrib.postgres.indexes import GistIndex
from django.contrib.gis.db import models
from django.core.validators import MaxValueValidator, MinValueValidator


class ForestDensityCell(models.Model):
    """
    Stores aggregated canopy cover percentage for a grid cell.
    Geometry uses WGS84 (EPSG:4326) polygons.
    """

    geom = models.PolygonField(srid=4326)
    canopy_pct = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Canopy cover percentage for the cell (0-100).",
    )
    source = models.CharField(
        max_length=64,
        default="hansen_v1",
        help_text="Dataset/version identifier used to derive canopy cover.",
    )
    tile_id = models.CharField(
        max_length=64,
        blank=True,
        help_text="Optional tile or scene id to group cells by input product.",
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            GistIndex(fields=["geom"], name="forest_density_geom_gist"),
            models.Index(fields=["canopy_pct"], name="forest_density_canopy_pct_idx"),
        ]
        verbose_name = "Forest density cell"
        verbose_name_plural = "Forest density cells"
        ordering = ["-updated_at"]

    def __str__(self) -> str:
        return f"ForestDensityCell {self.id} ({self.canopy_pct}% canopy)"
