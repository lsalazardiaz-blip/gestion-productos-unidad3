import json
from unittest.mock import patch

from django.test import TestCase

from .models import Producto


class ProductoApiTests(TestCase):
    def setUp(self):
        self.url = "/api/productos/"
        self.valido = {
            "nombre": "Cuaderno",
            "descripcion": "Tapa dura",
            "precio": "1990.50",
            "stock": 10,
        }

    def _post(self, payload):
        return self.client.post(
            self.url,
            data=json.dumps(payload),
            content_type="application/json",
        )

    def test_crear_producto(self):
        respuesta = self._post(self.valido)
        self.assertEqual(respuesta.status_code, 201)
        cuerpo = respuesta.json()
        self.assertEqual(cuerpo["nombre"], "Cuaderno")
        self.assertEqual(cuerpo["precio"], "1990.50")
        self.assertEqual(cuerpo["stock"], 10)
        self.assertEqual(Producto.objects.count(), 1)

    def test_consultar_producto(self):
        producto_id = self._post(self.valido).json()["id"]
        listado = self.client.get(self.url)
        self.assertEqual(listado.status_code, 200)
        self.assertEqual(len(listado.json()["productos"]), 1)
        detalle = self.client.get(f"{self.url}{producto_id}/")
        self.assertEqual(detalle.status_code, 200)
        self.assertEqual(detalle.json()["nombre"], "Cuaderno")

    def test_modificar_producto(self):
        producto_id = self._post(self.valido).json()["id"]
        cambios = {**self.valido, "precio": "2500.00", "stock": 4, "nombre": "Cuaderno A4"}
        respuesta = self.client.put(
            f"{self.url}{producto_id}/",
            data=json.dumps(cambios),
            content_type="application/json",
        )
        self.assertEqual(respuesta.status_code, 200)
        cuerpo = respuesta.json()
        self.assertEqual(cuerpo["precio"], "2500.00")
        self.assertEqual(cuerpo["stock"], 4)
        self.assertEqual(cuerpo["nombre"], "Cuaderno A4")

    def test_eliminar_producto(self):
        producto_id = self._post(self.valido).json()["id"]
        respuesta = self.client.delete(f"{self.url}{producto_id}/")
        self.assertEqual(respuesta.status_code, 204)
        self.assertEqual(respuesta.content, b"")
        despues = self.client.get(f"{self.url}{producto_id}/")
        self.assertEqual(despues.status_code, 404)
        self.assertEqual(Producto.objects.count(), 0)

    def test_rechaza_datos_invalidos(self):
        casos = [
            {**self.valido, "precio": "-10"},
            {**self.valido, "precio": "0"},
            {**self.valido, "precio": "10.555"},
            {**self.valido, "nombre": "   "},
            {**self.valido, "stock": "diez"},
            {**self.valido, "stock": -1},
            {**self.valido, "stock": True},
        ]
        for caso in casos:
            respuesta = self._post(caso)
            self.assertEqual(respuesta.status_code, 400, caso)
            self.assertIn("errores", respuesta.json())
        invalido = self.client.post(self.url, data="{no es json", content_type="application/json")
        self.assertEqual(invalido.status_code, 400)
        self.assertEqual(Producto.objects.count(), 0)

    def test_ignora_campos_extra_y_guarda_texto_literal(self):
        nombre = "'; DROP TABLE productos_producto; -- <script>alert(1)</script>"
        payload = {**self.valido, "nombre": nombre, "id": 999, "creado": "2000-01-01"}
        respuesta = self._post(payload)
        self.assertEqual(respuesta.status_code, 201)
        cuerpo = respuesta.json()
        self.assertNotEqual(cuerpo["id"], 999)
        self.assertEqual(cuerpo["nombre"], nombre)
        self.assertEqual(self.client.get(self.url).status_code, 200)
        self.assertTrue(Producto.objects.filter(nombre=nombre).exists())

    @patch("productos.views.Producto.objects.create", side_effect=RuntimeError("ruta secreta /tmp/db"))
    def test_error_interno_no_muestra_la_excepcion(self, _mock):
        respuesta = self._post(self.valido)
        self.assertEqual(respuesta.status_code, 500)
        texto = respuesta.content.decode()
        self.assertNotIn("ruta secreta", texto)
        self.assertEqual(respuesta.json()["detalle"], "Error interno del servidor.")

    def test_salud(self):
        respuesta = self.client.get("/api/salud/")
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(respuesta.json()["estado"], "ok")
