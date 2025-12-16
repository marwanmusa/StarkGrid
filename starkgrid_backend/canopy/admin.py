from django.contrib import admin
from django.contrib.gis.admin import GISModelAdmin

from .models import ForestDensityCell


@admin.register(ForestDensityCell)
class ForestDensityCellAdmin(GISModelAdmin):
    list_display = ("id", "canopy_pct", "source", "tile_id", "updated_at")
    list_filter = ("source",)
    search_fields = ("tile_id",)
    readonly_fields = ("updated_at",)
