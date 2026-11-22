import logging

from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from .models import Producto
from .validacion import leer_json, validar_producto

logger = logging.getLogger(__name__)


def producto_a_dict(producto):
    return {
        "id": producto.id,
        "nombre": producto.nombre,
        "descripcion": producto.descripcion,
        "precio": f"{producto.precio:.2f}",
        "stock": producto.stock,
        "creado": producto.creado.isoformat(),
        "actualizado": producto.actualizado.isoformat(),
    }


def error_json(detalle, status, errores=None):
    cuerpo = {"detalle": detalle}
    if errores:
        cuerpo["errores"] = errores
    return JsonResponse(cuerpo, status=status)


def _crear(request):
    datos, error = leer_json(request)
    if error:
        return error_json(error["detalle"], 400)
    limpio, errores = validar_producto(datos)
    if errores:
        return error_json("Datos inválidos.", 400, errores)
    producto = Producto.objects.create(**limpio)
    return JsonResponse(producto_a_dict(producto), status=201)


def _modificar(request, producto):
    datos, error = leer_json(request)
    if error:
        return error_json(error["detalle"], 400)
    limpio, errores = validar_producto(datos)
    if errores:
        return error_json("Datos inválidos.", 400, errores)
    for campo, valor in limpio.items():
        setattr(producto, campo, valor)
    producto.save(update_fields=["nombre", "descripcion", "precio", "stock", "actualizado"])
    return JsonResponse(producto_a_dict(producto))


@require_http_methods(["GET"])
def salud(request):
    return JsonResponse({"estado": "ok"})


@csrf_exempt
@require_http_methods(["GET", "POST"])
def productos_coleccion(request):
    """Lista o crea productos.

    csrf_exempt aplica solo a esta API JSON local, que no usa la sesión del
    navegador. Un formulario web sí debería conservar la protección CSRF.
    """
    try:
        if request.method == "GET":
            productos = [producto_a_dict(item) for item in Producto.objects.all()]
            return JsonResponse({"productos": productos})
        return _crear(request)
    except Exception:
        logger.exception("Error al operar la colección de productos")
        return error_json("Error interno del servidor.", 500)


@csrf_exempt
@require_http_methods(["GET", "PUT", "DELETE"])
def producto_detalle(request, producto_id):
    try:
        producto = Producto.objects.filter(pk=producto_id).first()
        if producto is None:
            return error_json("Producto no encontrado.", 404)
        if request.method == "GET":
            return JsonResponse(producto_a_dict(producto))
        if request.method == "DELETE":
            producto.delete()
            return HttpResponse(status=204)
        return _modificar(request, producto)
    except Exception:
        logger.exception("Error al operar el producto %s", producto_id)
        return error_json("Error interno del servidor.", 500)
