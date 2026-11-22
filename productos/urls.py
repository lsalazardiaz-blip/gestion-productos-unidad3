from django.urls import path

from . import views

urlpatterns = [
    path("salud/", views.salud, name="salud"),
    path("productos/", views.productos_coleccion, name="productos"),
    path("productos/<int:producto_id>/", views.producto_detalle, name="producto-detalle"),
]
