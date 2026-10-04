from django import forms
from django.core.exceptions import ValidationError
from django.forms import BaseInlineFormSet, inlineformset_factory

from .models import DetalleVenta, Producto, Venta


class ProductoForm(forms.ModelForm):
    """Formulario de Producto con estilos uniformes."""

    class Meta:
        model = Producto
        fields = ("nombre", "descripcion", "precio", "stock", "activo")
        widgets = {
            "nombre": forms.TextInput(
                attrs={
                    "class": "form-input",
                    "placeholder": "Ej.: Laptop Lenovo ThinkPad T14",
                }
            ),
            "descripcion": forms.Textarea(
                attrs={
                    "class": "form-input",
                    "rows": 3,
                    "placeholder": "Descripción técnica, especificaciones o notas del producto...",
                }
            ),
            "precio": forms.NumberInput(
                attrs={
                    "class": "form-input",
                    "min": 0,
                    "step": "any",
                    "placeholder": "0",
                }
            ),
            "stock": forms.NumberInput(
                attrs={
                    "class": "form-input",
                    "min": 0,
                    "placeholder": "0",
                }
            ),
            "activo": forms.CheckboxInput(
                attrs={
                    "class": "form-checkbox",
                }
            ),
        }
        labels = {
            "nombre": "Nombre del producto",
            "descripcion": "Descripción",
            "precio": "Precio de venta ($)",
            "stock": "Stock disponible",
            "activo": "Producto disponible para la venta",
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
            "cliente": forms.TextInput(
                attrs={
                    "class": "form-input",
                    "placeholder": "Cliente (ej.: Juan Pérez o Consumidor Final)",
                }
            ),
            "estado": forms.Select(attrs={"class": "form-input"}),
            "observaciones": forms.Textarea(
                attrs={
                    "class": "form-input",
                    "rows": 2,
                    "placeholder": "Detalles adicionales, número de boleta, método de pago...",
                }
            ),
        }
        labels = {
            "cliente": "Nombre del Cliente",
            "estado": "Estado de la Venta",
            "observaciones": "Observaciones / Notas",
        }


class DetalleVentaForm(forms.ModelForm):
    class Meta:
        model = DetalleVenta
        fields = ("producto", "cantidad")
        widgets = {
            "producto": forms.Select(attrs={"class": "form-input select-producto"}),
            "cantidad": forms.NumberInput(
                attrs={
                    "class": "form-input input-cantidad text-center",
                    "min": 1,
                    "value": 1,
                }
            ),
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