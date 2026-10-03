from django import forms
from django.core.exceptions import ValidationError
from django.forms import BaseInlineFormSet, inlineformset_factory

from .models import DetalleVenta, Producto, Venta


class ProductoForm(forms.ModelForm):
    """Formulario de Producto con estilos Tailwind definidos en los widgets."""

    class Meta:
        model = Producto
        fields = ("nombre", "descripcion", "precio", "stock", "activo")
        widgets = {
            "nombre": forms.TextInput(
                attrs={
                    "class": "mt-1 block w-full rounded-lg border border-slate-300 px-3 py-2 text-slate-900 shadow-sm outline-none transition focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200",
                    "placeholder": "Ej.: Teclado mecánico",
                }
            ),
            "descripcion": forms.Textarea(
                attrs={
                    "class": "mt-1 block w-full rounded-lg border border-slate-300 px-3 py-2 text-slate-900 shadow-sm outline-none transition focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200",
                    "rows": 4,
                    "placeholder": "Describe las características del producto",
                }
            ),
            "precio": forms.NumberInput(
                attrs={
                    "class": "mt-1 block w-full rounded-lg border border-slate-300 px-3 py-2 text-slate-900 shadow-sm outline-none transition focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200",
                    "min": 0,
                    "placeholder": "0",
                }
            ),
            "stock": forms.NumberInput(
                attrs={
                    "class": "mt-1 block w-full rounded-lg border border-slate-300 px-3 py-2 text-slate-900 shadow-sm outline-none transition focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200",
                    "min": 0,
                    "placeholder": "0",
                }
            ),
            "activo": forms.CheckboxInput(
                attrs={
                    "class": "h-4 w-4 rounded border-slate-300 text-indigo-600 focus:ring-indigo-500",
                }
            ),
        }
        labels = {
            "nombre": "Nombre",
            "descripcion": "Descripción",
            "precio": "Precio",
            "stock": "Stock disponible",
            "activo": "Producto activo",
        }

    def clean_nombre(self):
        nombre = self.cleaned_data["nombre"].strip()
        if not nombre:
            raise ValidationError("El nombre es obligatorio.")
        return nombre

    def clean_precio(self):
        precio = self.cleaned_data["precio"]
        if precio <= 0:
            raise ValidationError("El precio debe ser mayor que cero.")
        return precio


class VentaForm(forms.ModelForm):
    class Meta:
        model = Venta
        fields = ("cliente", "estado", "observaciones")
        widgets = {
            "cliente": forms.TextInput(attrs={"class": "field", "placeholder": "Cliente (opcional)"}),
            "estado": forms.Select(attrs={"class": "field"}),
            "observaciones": forms.Textarea(attrs={"class": "field", "rows": 3}),
        }


class DetalleVentaForm(forms.ModelForm):
    class Meta:
        model = DetalleVenta
        fields = ("producto", "cantidad")
        widgets = {
            "producto": forms.Select(attrs={"class": "field"}),
            "cantidad": forms.NumberInput(attrs={"class": "field", "min": 1}),
        }


class BaseDetalleVentaFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        productos = set()
        lineas = 0
        for form in self.forms:
            if not hasattr(form, "cleaned_data") or not form.cleaned_data:
                continue
            if form.cleaned_data.get("DELETE"):
                continue
            producto = form.cleaned_data.get("producto")
            if producto in productos:
                form.add_error("producto", "No repitas el mismo producto en una venta.")
            if producto:
                productos.add(producto)
                lineas += 1
        if lineas == 0:
            raise ValidationError("La venta debe incluir al menos un producto.")


DetalleVentaFormSet = inlineformset_factory(
    Venta,
    DetalleVenta,
    form=DetalleVentaForm,
    formset=BaseDetalleVentaFormSet,
    extra=1,
    can_delete=True,
)