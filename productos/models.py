from django.db import models


class Producto(models.Model):
    nombre = models.CharField("nombre", max_length=120)
    descripcion = models.TextField("descripción", blank=True, default="")
    precio = models.DecimalField("precio", max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField("stock")
    creado = models.DateTimeField("creado", auto_now_add=True)
    actualizado = models.DateTimeField("actualizado", auto_now=True)

    class Meta:
        ordering = ["-creado"]
        verbose_name = "producto"
        verbose_name_plural = "productos"

    def __str__(self):
        return self.nombre
