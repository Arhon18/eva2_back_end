from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ProductoForm
from .models import Producto


def lista_productos(request):
    productos = Producto.objects.all().order_by("nombre")
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