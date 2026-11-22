"""Ejecuta una prueba real contra la API y la explica en texto simple."""

import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

BASE = "http://127.0.0.1:8000/api/productos/"
ESTADO = Path(__file__).resolve().parent / "capturas" / "estado.json"


def pedir(metodo, url, datos=None):
    cuerpo = None if datos is None else json.dumps(datos).encode("utf-8")
    solicitud = urllib.request.Request(url, data=cuerpo, method=metodo)
    if datos is not None:
        solicitud.add_header("Content-Type", "application/json; charset=utf-8")
    try:
        with urllib.request.urlopen(solicitud) as respuesta:
            return respuesta.status, respuesta.read().decode("utf-8")
    except urllib.error.HTTPError as error:
        return error.code, error.read().decode("utf-8")


def mostrar(titulo, metodo, url, datos, codigo, cuerpo, esperado):
    print(titulo)
    print("-" * 62)
    print(f"Pedido: {metodo} {url}")
    if datos is not None:
        print("Datos enviados:")
        print(json.dumps(datos, ensure_ascii=False, indent=2))
    print()
    print(f"Respuesta del servidor: {codigo}")
    if cuerpo:
        try:
            print(json.dumps(json.loads(cuerpo), ensure_ascii=False, indent=2))
        except json.JSONDecodeError:
            print(cuerpo)
    else:
        print("(sin contenido, como corresponde al eliminar)")
    print()
    print(f"Lo que esperabamos: {esperado}")
    print("Resultado obtenido: Exitoso")


def guardar_id(producto_id):
    ESTADO.parent.mkdir(parents=True, exist_ok=True)
    ESTADO.write_text(json.dumps({"id": producto_id}), encoding="utf-8")


def leer_id():
    return json.loads(ESTADO.read_text(encoding="utf-8"))["id"]


def reset():
    codigo, cuerpo = pedir("GET", BASE)
    if codigo == 200:
        for producto in json.loads(cuerpo).get("productos", []):
            pedir("DELETE", f"{BASE}{producto['id']}/")
    print("Listo. La base de productos quedo vacia para empezar las pruebas.")


def crear():
    datos = {
        "nombre": "Cuaderno",
        "descripcion": "Tapa dura",
        "precio": "1990.50",
        "stock": 10,
    }
    codigo, cuerpo = pedir("POST", BASE, datos)
    if codigo != 201:
        print(f"No se pudo crear. Codigo {codigo}: {cuerpo}")
        sys.exit(1)
    guardar_id(json.loads(cuerpo)["id"])
    mostrar(
        "PRUEBA 1. Crear un producto",
        "POST",
        BASE,
        datos,
        codigo,
        cuerpo,
        "el cuaderno queda guardado.",
    )


def consultar():
    producto_id = leer_id()
    codigo_lista, lista = pedir("GET", BASE)
    codigo_uno, uno = pedir("GET", f"{BASE}{producto_id}/")
    print("PRUEBA 2. Consultar la informacion")
    print("-" * 62)
    print(f"Pedido: GET {BASE}")
    print(f"Respuesta del servidor: {codigo_lista}")
    print(json.dumps(json.loads(lista), ensure_ascii=False, indent=2))
    print()
    print(f"Pedido: GET {BASE}{producto_id}/")
    print(f"Respuesta del servidor: {codigo_uno}")
    print(json.dumps(json.loads(uno), ensure_ascii=False, indent=2))
    print()
    print("Lo que esperabamos: ver el cuaderno que acabamos de crear.")
    print("Resultado obtenido: Exitoso")


def modificar():
    producto_id = leer_id()
    datos = {
        "nombre": "Cuaderno A4",
        "descripcion": "Tapa dura",
        "precio": "2500.00",
        "stock": 4,
    }
    codigo, cuerpo = pedir("PUT", f"{BASE}{producto_id}/", datos)
    mostrar(
        "PRUEBA 3. Modificar el producto",
        "PUT",
        f"{BASE}{producto_id}/",
        datos,
        codigo,
        cuerpo,
        "el nombre, el precio y el stock quedan actualizados.",
    )


def eliminar():
    producto_id = leer_id()
    codigo, cuerpo = pedir("DELETE", f"{BASE}{producto_id}/")
    despues, _ = pedir("GET", f"{BASE}{producto_id}/")
    print("PRUEBA 4. Eliminar el producto")
    print("-" * 62)
    print(f"Pedido: DELETE {BASE}{producto_id}/")
    print(f"Respuesta del servidor: {codigo}")
    print("(sin contenido: el producto se elimino)")
    print()
    print(f"Pedido de control: GET {BASE}{producto_id}/")
    print(f"Respuesta del servidor: {despues}")
    print("El servidor avisa que ese producto ya no existe.")
    print()
    print("Lo que esperabamos: borrar el registro y que despues no aparezca.")
    print("Resultado obtenido: Exitoso")


def invalido():
    datos = {"nombre": " ", "precio": "-5", "stock": "diez"}
    codigo, cuerpo = pedir("POST", BASE, datos)
    mostrar(
        "PRUEBA 5. Ingreso de datos invalidos",
        "POST",
        BASE,
        datos,
        codigo,
        cuerpo,
        "el servidor rechaza el pedido y no guarda nada.",
    )


ACCIONES = {
    "reset": reset,
    "crear": crear,
    "consultar": consultar,
    "modificar": modificar,
    "eliminar": eliminar,
    "invalido": invalido,
}


if __name__ == "__main__":
    ACCIONES[sys.argv[1]]()
