from django.db import models

# Create your models here.
class Producto(models.Model):
    nombre      = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    precio      = models.DecimalField(max_digits=10, decimal_places=2)
    stock       = models.PositiveIntegerField()
    activo      = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre