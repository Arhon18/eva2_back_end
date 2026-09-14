from django.contrib import admin
from .models import Producto

class ProductoAdmin(admin.ModelAdmin):
    list_display  = ("nombre", "precio","stock", "activo")
    search_fields = ("nombre",)
    list_filter   = ("activo",)
    ordering      = ("nombre",)

admin.site.register(model_or_iterable=Producto, admin_class=ProductoAdmin)