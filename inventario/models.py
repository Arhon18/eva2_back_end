from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import DecimalField, ExpressionWrapper, F, Sum

# Create your models here.
class Producto(models.Model):
    nombre      = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    precio      = models.DecimalField(max_digits=10, decimal_places=2)
    stock       = models.PositiveIntegerField()
    activo      = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre

    @property
    def precio_formateado(self):
        return f"${int(self.precio):,}".replace(",", ".")

    @property
    def estado_stock(self):
        if self.stock <= 0:
            return "agotado"
        elif self.stock <= 5:
            return "critico"
        return "optimo"


class Venta(models.Model):
    ESTADOS = (
        ("pendiente", "Pendiente"),
        ("pagada", "Pagada"),
        ("anulada", "Anulada"),
    )

    cliente = models.CharField(max_length=120, blank=True)
    fecha = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=12, choices=ESTADOS, default="pagada")
    observaciones = models.TextField(blank=True)

    class Meta:
        ordering = ("-fecha", "-id")
        verbose_name = "venta"
        verbose_name_plural = "ventas"

    def __str__(self):
        return f"Venta #{self.pk}"

    @property
    def folio(self):
        return f"VNT-{self.pk:05d}"

    @property
    def total(self):
        subtotal = ExpressionWrapper(
            F("cantidad") * F("precio_unitario"),
            output_field=DecimalField(max_digits=12, decimal_places=2),
        )
        return self.detalles.aggregate(total=Sum(subtotal))["total"] or Decimal("0.00")

    @property
    def total_formateado(self):
        return f"${int(self.total):,}".replace(",", ".")


class DetalleVenta(models.Model):
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE, related_name="detalles")
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT, related_name="detalles_venta")
    cantidad = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal("0.01"))])

    class Meta:
        verbose_name = "detalle de venta"
        verbose_name_plural = "detalles de venta"
        constraints = [
            models.UniqueConstraint(fields=("venta", "producto"), name="una_linea_por_producto_venta"),
        ]

    def __str__(self):
        return f"{self.producto} x {self.cantidad}"

    @property
    def subtotal(self):
        return self.cantidad * self.precio_unitario