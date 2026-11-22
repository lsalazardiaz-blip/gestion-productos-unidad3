# Gestión de productos

API local para registrar, consultar, modificar y eliminar productos. Usa Django 5.2 y SQLite. No tiene pantalla: las operaciones se prueban con un cliente HTTP (PowerShell, Postman o Insomnia).

## Requisitos

- Python 3.13
- pip

## Instalar dependencias

Desde esta carpeta (`gestion_productos`):

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## Configurar variables

Copia el ejemplo y, si quieres, cambia la clave:

```powershell
Copy-Item .env.example .env
```

Variables:

| Variable | Uso |
| --- | --- |
| `DJANGO_SECRET_KEY` | Clave de Django. Obligatoria si `DJANGO_DEBUG` es `False`. |
| `DJANGO_DEBUG` | `True` solo en local. |
| `DJANGO_ALLOWED_HOSTS` | Hosts permitidos, separados por coma. |

Si no existe `.env`, la aplicación arranca en modo local con una clave de desarrollo. No uses esa clave fuera de tu computador.

## Configurar la base de datos

SQLite no se instala aparte. El archivo `db.sqlite3` se crea al migrar:

```powershell
.\.venv\Scripts\python.exe manage.py migrate
```

## Ejecutar la aplicación

```powershell
.\.venv\Scripts\python.exe manage.py runserver
```

Queda en `http://127.0.0.1:8000/`.

- Salud: `GET /api/salud/`
- Listar y crear: `GET` y `POST /api/productos/`
- Ver, modificar y eliminar: `GET`, `PUT` y `DELETE /api/productos/<id>/`

Ejemplo en PowerShell:

```powershell
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/api/productos/ -ContentType "application/json; charset=utf-8" -Body '{"nombre":"Cuaderno","descripcion":"Tapa dura","precio":"1990.50","stock":10}'
Invoke-RestMethod http://127.0.0.1:8000/api/productos/
```

`PUT` reemplaza el producto: hay que enviar nombre, precio y stock. La descripción es opcional. El precio va con punto decimal y como máximo dos decimales. El stock es un entero mayor o igual que 0.

## Ejecutar las pruebas

```powershell
.\.venv\Scripts\python.exe manage.py test
```

## Entrega

El ZIP del código no debe incluir `.venv`, `db.sqlite3`, `__pycache__` ni `.env`. Para armarlo:

```powershell
.\empaquetar.ps1
```

El informe para el profesor es `Salazar_Luis_Trabajo_Unidad3.docx`, en la raíz de este proyecto.

El ZIP local, si hace falta subirlo aparte, queda en `entregas/Salazar_Luis_Proyecto_Unidad3.zip`. No incluye el entorno virtual, `db.sqlite3` ni `.env`.
