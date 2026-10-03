from django.urls import path

from . import views

app_name = "inventario"

urlpatterns = [
    path("", views.lista_productos, name="lista_productos"),
    path("nuevo/", views.crear_producto, name="crear_producto"),
    path("<int:pk>/editar/", views.editar_producto, name="editar_producto"),
    path("<int:pk>/eliminar/", views.eliminar_producto, name="eliminar_producto"),
    path("ventas/", views.lista_ventas, name="lista_ventas"),
    path("ventas/nueva/", views.crear_venta, name="crear_venta"),
    path("ventas/reporte/", views.reporte_ventas, name="reporte_ventas"),
    path("ventas/<int:pk>/", views.detalle_venta, name="detalle_venta"),
    path("ventas/<int:pk>/editar/", views.editar_venta, name="editar_venta"),
    path("ventas/<int:pk>/eliminar/", views.eliminar_venta, name="eliminar_venta"),
]