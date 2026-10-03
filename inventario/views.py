from datetime import datetime

from django.contrib import messages
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Q, Sum
from django.forms.utils import ErrorList
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import DetalleVentaFormSet, ProductoForm, VentaForm
from .models import DetalleVenta, Producto, Venta


def lista_productos(request):
    productos = Paginator(Producto.objects.all().order_by("nombre"), 8).get_page(request.GET.get("page"))
    return render(request, "inventario/lista_productos.html", {"productos": productos})


def crear_producto(request):
    form = ProductoForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        producto = form.save()
        messages.success(request, f'El producto "{producto.nombre}" fue creado correctamente.')
        return redirect("inventario:lista_productos")

    return render(
        request,
        "inventario/formulario_producto.html",
        {"form": form, "titulo": "Nuevo producto", "boton": "Guardar producto"},
    )


def editar_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    form = ProductoForm(request.POST or None, instance=producto)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, f'El producto "{producto.nombre}" fue actualizado correctamente.')
        return redirect("inventario:lista_productos")

    return render(
        request,
        "inventario/formulario_producto.html",
        {
            "form": form,
            "producto": producto,
            "titulo": "Editar producto",
            "boton": "Guardar cambios",
        },
    )


def eliminar_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == "POST":
        nombre = producto.nombre
        producto.delete()
        messages.success(request, f'El producto "{nombre}" fue eliminado correctamente.')
        return redirect("inventario:lista_productos")

    return render(request, "inventario/confirmar_eliminacion.html", {"producto": producto})


def _guardar_detalles(venta, formset, venta_anterior=None):
    producto_ids = {form.cleaned_data["producto"].pk for form in formset.forms if form.cleaned_data and not form.cleaned_data.get("DELETE")}
    if venta_anterior:
        producto_ids.update(venta_anterior.detalles.values_list("producto_id", flat=True))
    productos = {producto.pk: producto for producto in Producto.objects.select_for_update().filter(pk__in=producto_ids)}

    if venta_anterior:
        for detalle in venta_anterior.detalles.all():
            productos[detalle.producto_id].stock += detalle.cantidad
        Producto.objects.bulk_update(productos.values(), ["stock"])

    detalles = []
    for form in formset.forms:
        if not form.cleaned_data or form.cleaned_data.get("DELETE"):
            continue
        producto = productos[form.cleaned_data["producto"].pk]
        cantidad = form.cleaned_data["cantidad"]
        if not producto.activo:
            raise ValueError(f'El producto "{producto.nombre}" está inactivo.')
        if producto.stock < cantidad:
            raise ValueError(f'Stock insuficiente para "{producto.nombre}". Disponible: {producto.stock}.')
        producto.stock -= cantidad
        detalles.append(DetalleVenta(venta=venta, producto=producto, cantidad=cantidad, precio_unitario=producto.precio))

    Producto.objects.bulk_update(productos.values(), ["stock"])
    if venta_anterior:
        venta_anterior.detalles.all().delete()
    DetalleVenta.objects.bulk_create(detalles)


def lista_ventas(request):
    ventas = Venta.objects.prefetch_related("detalles").all()
    consulta = request.GET.get("q", "").strip()
    if consulta:
        ventas = ventas.filter(Q(cliente__icontains=consulta) | Q(id__icontains=consulta))
    page_obj = Paginator(ventas, 10).get_page(request.GET.get("page"))
    return render(request, "inventario/lista_ventas.html", {"ventas": page_obj, "consulta": consulta})


def crear_venta(request):
    venta = Venta()
    form = VentaForm(request.POST or None, instance=venta)
    formset = DetalleVentaFormSet(request.POST or None, instance=venta)
    if request.method == "POST" and form.is_valid() and formset.is_valid():
        try:
            with transaction.atomic():
                venta = form.save()
                _guardar_detalles(venta, formset)
        except ValueError as error:
            formset._non_form_errors = ErrorList([str(error)])
        else:
            messages.success(request, f"La venta #{venta.pk} fue registrada correctamente.")
            return redirect("inventario:detalle_venta", pk=venta.pk)
    return render(request, "inventario/formulario_venta.html", {"form": form, "formset": formset, "titulo": "Nueva venta"})


def editar_venta(request, pk):
    venta = get_object_or_404(Venta, pk=pk)
    form = VentaForm(request.POST or None, instance=venta)
    formset = DetalleVentaFormSet(request.POST or None, instance=venta)
    if request.method == "POST" and form.is_valid() and formset.is_valid():
        try:
            with transaction.atomic():
                venta = form.save()
                _guardar_detalles(venta, formset, venta_anterior=venta)
        except ValueError as error:
            formset._non_form_errors = ErrorList([str(error)])
        else:
            messages.success(request, f"La venta #{venta.pk} fue actualizada correctamente.")
            return redirect("inventario:detalle_venta", pk=venta.pk)
    return render(request, "inventario/formulario_venta.html", {"form": form, "formset": formset, "titulo": f"Editar venta #{venta.pk}", "venta": venta})


def detalle_venta(request, pk):
    venta = get_object_or_404(Venta.objects.prefetch_related("detalles__producto"), pk=pk)
    return render(request, "inventario/detalle_venta.html", {"venta": venta})


@transaction.atomic
def eliminar_venta(request, pk):
    venta = get_object_or_404(Venta.objects.prefetch_related("detalles"), pk=pk)
    if request.method == "POST":
        productos = {p.pk: p for p in Producto.objects.select_for_update().filter(pk__in=venta.detalles.values_list("producto_id", flat=True))}
        for detalle in venta.detalles.all():
            productos[detalle.producto_id].stock += detalle.cantidad
        Producto.objects.bulk_update(productos.values(), ["stock"])
        venta.delete()
        messages.success(request, f"La venta #{pk} fue eliminada y el stock fue restaurado.")
        return redirect("inventario:lista_ventas")
    return render(request, "inventario/confirmar_eliminacion.html", {"venta": venta})


def reporte_ventas(request):
    hoy = timezone.localdate()
    desde = request.GET.get("desde", hoy.replace(day=1).isoformat())
    hasta = request.GET.get("hasta", hoy.isoformat())
    try:
        fecha_desde = datetime.fromisoformat(desde).date()
        fecha_hasta = datetime.fromisoformat(hasta).date()
    except ValueError:
        fecha_desde, fecha_hasta = hoy.replace(day=1), hoy
    ventas = Venta.objects.filter(fecha__date__range=(fecha_desde, fecha_hasta)).prefetch_related("detalles")
    total = sum((venta.total for venta in ventas), 0)
    if request.GET.get("formato") == "csv":
        response = HttpResponse(content_type="text/csv; charset=utf-8")
        response["Content-Disposition"] = 'attachment; filename="reporte-ventas.csv"'
        response.write("\ufeffID,Fecha,Cliente,Estado,Total\n")
        for venta in ventas:
            response.write(f"{venta.pk},{venta.fecha:%Y-%m-%d %H:%M},{venta.cliente},{venta.get_estado_display()},{venta.total}\n")
        return response
    return render(request, "inventario/reporte_ventas.html", {"ventas": ventas, "total": total, "desde": desde, "hasta": hasta})