# Comandos rápidos

Escribe **solo la palabra** en el chat. El agente actúa sin pedir más detalle.

| Palabra | Qué hace |
| --- | --- |
| **empaquetar** | Deja en `entregas` el informe `Salazar_Luis_Trabajo_Unidad3.docx` y el código `Salazar_Luis_Proyecto_Unidad3.zip`. Alias: `entrega`, `deploy`. |
| **levantar** | Arranca `manage.py runserver` en `http://127.0.0.1:8000/`. Alias: `demo`, `subir`. |
| **parar** | Detiene ese servidor. Alias: `bajar`, `stop`. |
| **salud** | Consulta `GET /api/salud/`. Alias: `health`. |
| **version** | La versión visible está en `productos/__init__.py` (`1.0.0`). |
| **setup** | Crea `.venv`, instala `requirements.txt` y ejecuta `migrate`. |

## Atajos locales

| Archivo | Acción |
| --- | --- |
| `empaquetar.ps1` | Genera el ZIP de entrega |
| `README.md` | Instalación, variables, base de datos, ejecución y pruebas |

## Rutas útiles

| Qué | Dónde |
| --- | --- |
| Proyecto | carpeta `gestion_productos` |
| Entregas | `entregas/` (no se versiona) |
| Health | `http://127.0.0.1:8000/api/salud/` |
| Productos | `http://127.0.0.1:8000/api/productos/` |

## Notas

- Responder siempre en **español**.
- Trabajar dentro de esta carpeta, no en la raíz del workspace.
- Python del entorno: 3.13. Django fijado en `requirements.txt`.
