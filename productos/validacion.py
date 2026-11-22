import json
from decimal import Decimal, InvalidOperation

NOMBRE_MAX = 120
DESCRIPCION_MAX = 500
PRECIO_MAX = Decimal("99999999.99")
STOCK_MAX = 1_000_000


def leer_json(request):
    if not request.body:
        return None, {"detalle": "El cuerpo de la solicitud está vacío."}
    try:
        datos = json.loads(request.body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return None, {"detalle": "El cuerpo debe ser JSON válido."}
    if not isinstance(datos, dict):
        return None, {"detalle": "El cuerpo debe ser un objeto JSON."}
    return datos, None


def validar_producto(datos):
    """Devuelve los campos aceptados y un diccionario de errores.

    Solo se copian nombre, descripcion, precio y stock. Cualquier otra clave
    del JSON se ignora para no asignar id, fechas ni atributos internos.
    """
    errores = {}
    limpio = {}

    nombre = datos.get("nombre", "")
    if not isinstance(nombre, str):
        errores["nombre"] = "El nombre debe ser texto."
    else:
        nombre = " ".join(nombre.split())
        if not nombre:
            errores["nombre"] = "El nombre es obligatorio."
        elif len(nombre) > NOMBRE_MAX:
            errores["nombre"] = f"El nombre no puede superar {NOMBRE_MAX} caracteres."
        else:
            limpio["nombre"] = nombre

    if "descripcion" not in datos or datos["descripcion"] is None:
        limpio["descripcion"] = ""
    elif not isinstance(datos["descripcion"], str):
        errores["descripcion"] = "La descripción debe ser texto."
    else:
        descripcion = datos["descripcion"].strip()
        if len(descripcion) > DESCRIPCION_MAX:
            errores["descripcion"] = (
                f"La descripción no puede superar {DESCRIPCION_MAX} caracteres."
            )
        else:
            limpio["descripcion"] = descripcion

    if "precio" not in datos:
        errores["precio"] = "El precio es obligatorio."
    else:
        _validar_precio(datos["precio"], errores, limpio)

    if "stock" not in datos:
        errores["stock"] = "El stock es obligatorio."
    else:
        _validar_stock(datos["stock"], errores, limpio)

    return limpio, errores


def _validar_precio(valor, errores, limpio):
    if isinstance(valor, bool) or not isinstance(valor, (int, float, str)):
        errores["precio"] = "El precio debe ser un número."
        return
    try:
        precio = Decimal(str(valor))
    except (InvalidOperation, ValueError):
        errores["precio"] = "El precio debe ser un número."
        return
    if not precio.is_finite():
        errores["precio"] = "El precio debe ser un número."
    elif precio <= 0:
        errores["precio"] = "El precio debe ser mayor que 0."
    elif precio > PRECIO_MAX:
        errores["precio"] = "El precio supera el máximo permitido."
    else:
        cuantizado = precio.quantize(Decimal("0.01"))
        if cuantizado != precio:
            errores["precio"] = "El precio admite como máximo dos decimales."
        else:
            limpio["precio"] = cuantizado


def _validar_stock(valor, errores, limpio):
    # bool es subclase de int: True pasaría como stock 1 si solo se usara isinstance(valor, int).
    if isinstance(valor, bool) or not isinstance(valor, int):
        errores["stock"] = "El stock debe ser un número entero."
    elif valor < 0:
        errores["stock"] = "El stock no puede ser negativo."
    elif valor > STOCK_MAX:
        errores["stock"] = "El stock supera el máximo permitido."
    else:
        limpio["stock"] = valor
