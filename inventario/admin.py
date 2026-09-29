import csv

from django.contrib import admin
from django.http import HttpResponse

from .models import Producto


class StockRangeFilter(admin.SimpleListFilter):
    title = "rango de stock"
    parameter_name = "stock_range"

    def lookups(self, request, model_admin):
        return (
            ("out", "Sin stock"),
            ("low", "Stock bajo: 1 - 10"),
            ("medium", "Stock medio: 11 - 50"),
            ("high", "Stock alto: 51 - 100"),
            ("very_high", "Stock muy alto: más de 100"),
        )

    def queryset(self, request, queryset):
        value = self.value()

        if value == "out":
            return queryset.filter(stock=0)
        if value == "low":
            return queryset.filter(stock__gte=1, stock__lte=10)
        if value == "medium":
            return queryset.filter(stock__gte=11, stock__lte=50)
        if value == "high":
            return queryset.filter(stock__gte=51, stock__lte=100)
        if value == "very_high":
            return queryset.filter(stock__gt=100)

        return queryset


@admin.action(description="Exportar productos seleccionados a CSV")
def exportar_productos_csv(modeladmin, request, queryset):
    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = 'attachment; filename="inventario.csv"'

    response.write("\ufeff")  # BOM para Excel
    writer = csv.writer(response)

    writer.writerow(["ID", "Producto", "Stock", "Precio"])

    for producto in queryset:
        writer.writerow([
            producto.id,
            producto.nombre,
            producto.stock,
            producto.precio,
        ])

    return response


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ("id", "nombre", "stock", "precio")
    list_filter = (StockRangeFilter,)
    actions = (exportar_productos_csv,)