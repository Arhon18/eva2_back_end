from datetime import date
from decimal import Decimal

from django.test import TestCase

from .models import Producto, Venta


class VentasFlowTests(TestCase):
	def setUp(self):
		self.producto = Producto.objects.create(nombre="Café", precio=Decimal("2500.00"), stock=10)

	def datos_venta(self, cantidad=2):
		return {
			"cliente": "Ana",
			"estado": "pagada",
			"observaciones": "",
			"detalles-TOTAL_FORMS": "1",
			"detalles-INITIAL_FORMS": "0",
			"detalles-MIN_NUM_FORMS": "0",
			"detalles-MAX_NUM_FORMS": "1000",
			"detalles-0-producto": str(self.producto.pk),
			"detalles-0-cantidad": str(cantidad),
		}

	def test_crear_venta_calcula_total_y_descuenta_stock(self):
		response = self.client.post("/ventas/nueva/", self.datos_venta())
		self.assertRedirects(response, "/ventas/1/")
		venta = Venta.objects.get()
		self.assertEqual(venta.total, Decimal("5000.00"))
		self.producto.refresh_from_db()
		self.assertEqual(self.producto.stock, 8)

	def test_no_permite_vender_mas_stock_disponible(self):
		response = self.client.post("/ventas/nueva/", self.datos_venta(11))
		self.assertEqual(response.status_code, 200)
		self.assertEqual(Venta.objects.count(), 0)

	def test_eliminar_venta_restaura_stock(self):
		self.client.post("/ventas/nueva/", self.datos_venta())
		response = self.client.post("/ventas/1/eliminar/")
		self.assertRedirects(response, "/ventas/")
		self.producto.refresh_from_db()
		self.assertEqual(self.producto.stock, 10)

	def test_reporte_filtra_por_fecha(self):
		self.client.post("/ventas/nueva/", self.datos_venta())
		response = self.client.get("/ventas/reporte/", {"desde": date.today().isoformat(), "hasta": date.today().isoformat()})
		self.assertContains(response, "$5000.00")

# Create your tests here.
