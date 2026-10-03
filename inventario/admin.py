import csv

from django.contrib import admin
from django.http import HttpResponse

from .models import DetalleVenta, Producto, Venta


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
    list_display = ("id", "nombre", "stock", "precio", "activo")
    list_filter = (StockRangeFilter,)
    actions = (exportar_productos_csv,)
    search_fields = ("nombre", "descripcion")


class DetalleVentaInline(admin.TabularInline):
    model = DetalleVenta
    extra = 1
    autocomplete_fields = ("producto",)
    readonly_fields = ("subtotal_admin",)

    @admin.display(description="Subtotal")
    def subtotal_admin(self, obj):
        return obj.subtotal if obj.pk else "-"


@admin.action(description="Marcar ventas seleccionadas como pagadas")
def marcar_pagadas(modeladmin, request, queryset):
    queryset.update(estado="pagada")


@admin.register(Venta)
class VentaAdmin(admin.ModelAdmin):
    list_display = ("id", "fecha", "cliente", "estado", "total_admin")
    list_filter = ("estado", "fecha")
    search_fields = ("=id", "cliente", "detalles__producto__nombre")
    date_hierarchy = "fecha"
    readonly_fields = ("fecha", "total_admin")
    inlines = (DetalleVentaInline,)
    actions = (marcar_pagadas,)

    @admin.display(description="Total", ordering="detalles__precio_unitario")
    def total_admin(self, obj):
        return obj.total


@admin.register(DetalleVenta)
class DetalleVentaAdmin(admin.ModelAdmin):
    list_display = ("venta", "producto", "cantidad", "precio_unitario", "subtotal_admin")
    list_filter = ("producto",)
    search_fields = ("venta__cliente", "producto__nombre")
    autocomplete_fields = ("venta", "producto")

    @admin.display(description="Subtotal")
    def subtotal_admin(self, obj):
        return obj.subtotal

admin.site.site_header = "Control de Ventas"
admin.site.site_title = "Panel Tienda"
admin.site.index_title = "Administración de Ventas e Inventario"