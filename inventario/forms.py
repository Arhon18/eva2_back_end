from django import forms

from .models import Producto


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