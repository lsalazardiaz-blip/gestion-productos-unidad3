"""Arma el informe de la Unidad 3 en Word, con las capturas de las pruebas."""

from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor
from PIL import Image

CARPETA = Path(__file__).resolve().parent
CAPTURAS = CARPETA / "capturas"
SALIDA = CARPETA / "Apellido_Nombre_Trabajo_Unidad3.docx"
FUENTE = "Times New Roman"
NEGRO = RGBColor(0, 0, 0)


def recortar(origen):
    imagen = Image.open(origen).convert("RGB")
    ancho, alto = imagen.size
    pixeles = imagen.load()

    filas = []
    for y in range(alto):
        claros = 0
        for x in range(24, max(25, ancho - 24), 4):
            rojo, verde, azul = pixeles[x, y]
            if rojo > 170 and verde > 170 and azul > 170:
                claros += 1
                if claros >= 2:
                    filas.append(y)
                    break
    grupos = []
    inicio = anterior = filas[0]
    for y in filas[1:]:
        if y - anterior > 30:
            grupos.append((inicio, anterior))
            inicio = y
        anterior = y
    grupos.append((inicio, anterior))
    ultimo_inicio, ultimo_fin = grupos[-1]
    if len(grupos) > 1 and ultimo_fin >= alto - 16 and ultimo_fin - ultimo_inicio < 40:
        grupos.pop()
    abajo = min(alto, grupos[-1][1] + 24)
    recorte = imagen.crop((0, 0, ancho, abajo))
    destino = CAPTURAS / f"recorte-{origen.name}"
    recorte.save(destino)
    return destino


def fuente_run(run, tamano, negrita=False, cursiva=False):
    run.font.name = FUENTE
    run.font.size = Pt(tamano)
    run.bold = negrita
    run.italic = cursiva
    run.font.color.rgb = NEGRO
    run._element.rPr.rFonts.set(qn("w:eastAsia"), FUENTE)


def parrafo(doc, texto, tamano=12, negrita=False, cursiva=False, centro=False, espacio=8, izquierda=0):
    bloque = doc.add_paragraph()
    bloque.paragraph_format.space_after = Pt(espacio)
    bloque.paragraph_format.space_before = Pt(0)
    bloque.paragraph_format.line_spacing = 1.15
    if centro:
        bloque.alignment = WD_ALIGN_PARAGRAPH.CENTER
    if izquierda:
        bloque.paragraph_format.left_indent = Cm(izquierda)
    run = bloque.add_run(texto)
    fuente_run(run, tamano, negrita, cursiva)
    return bloque


def titulo(doc, texto, nivel):
    bloque = doc.add_heading(texto, level=nivel)
    bloque.paragraph_format.space_before = Pt(12 if nivel == 1 else 8)
    bloque.paragraph_format.space_after = Pt(6)
    for run in bloque.runs:
        fuente_run(run, 16 if nivel == 1 else 13, True)
        run.font.color.rgb = NEGRO
    return bloque


def viñeta(doc, texto):
    bloque = doc.add_paragraph(style="List Bullet")
    bloque.paragraph_format.space_after = Pt(3)
    bloque.paragraph_format.line_spacing = 1.15
    if bloque.runs:
        bloque.runs[0].text = texto
        fuente_run(bloque.runs[0], 12)
    else:
        run = bloque.add_run(texto)
        fuente_run(run, 12)


def pregunta(doc, texto):
    parrafo(doc, texto, negrita=True, espacio=2)


def borde_celda(celda):
    tc = celda._tc
    tcPr = tc.get_or_add_tcPr()
    bordes = OxmlElement("w:tcBorders")
    for lado in ("top", "left", "bottom", "right"):
        nodo = OxmlElement(f"w:{lado}")
        nodo.set(qn("w:val"), "single")
        nodo.set(qn("w:sz"), "4")
        nodo.set(qn("w:color"), "000000")
        bordes.append(nodo)
    tcPr.append(bordes)


def tabla(doc, filas):
    cuadro = doc.add_table(rows=len(filas), cols=len(filas[0]))
    cuadro.autofit = True
    for i, fila in enumerate(filas):
        for j, texto in enumerate(fila):
            celda = cuadro.rows[i].cells[j]
            celda.text = ""
            bloque = celda.paragraphs[0]
            run = bloque.add_run(texto)
            fuente_run(run, 11, negrita=(i == 0))
            borde_celda(celda)
    doc.add_paragraph()


def figura(doc, archivo, pie):
    doc.add_picture(str(recortar(CAPTURAS / archivo)), width=Cm(15.5))
    ultimo = doc.paragraphs[-1]
    ultimo.alignment = WD_ALIGN_PARAGRAPH.CENTER
    parrafo(doc, pie, tamano=11, cursiva=True, centro=True, espacio=12)


def preparar_estilos(doc):
    normal = doc.styles["Normal"]
    normal.font.name = FUENTE
    normal.font.size = Pt(12)
    normal.font.color.rgb = NEGRO
    normal._element.rPr.rFonts.set(qn("w:eastAsia"), FUENTE)
    for seccion in doc.sections:
        seccion.top_margin = Cm(2.5)
        seccion.bottom_margin = Cm(2.5)
        seccion.left_margin = Cm(2.5)
        seccion.right_margin = Cm(2.5)
        seccion.page_width = Cm(21.0)
        seccion.page_height = Cm(29.7)


def construir():
    doc = Document()
    preparar_estilos(doc)
    doc.core_properties.title = "Trabajo Unidad 3. Gestión de productos"
    doc.core_properties.subject = "Framework de Desarrollo e Inteligencia Artificial"
    doc.core_properties.category = "Informe"

    parrafo(doc, "Framework de Desarrollo e Inteligencia Artificial", 14, True, centro=True, espacio=6)
    parrafo(doc, "Trabajo de desarrollo grupal", 16, True, centro=True, espacio=2)
    parrafo(doc, "Unidad 3", 16, True, centro=True, espacio=12)
    parrafo(doc, "Gestión de productos", 14, True, centro=True, espacio=18)
    parrafo(doc, "Integrantes: [completar nombre completo de cada uno]", centro=True, espacio=4)
    parrafo(doc, "Docente: [completar]", centro=True, espacio=4)
    parrafo(doc, "Fecha: 22 de noviembre de 2026", centro=True, espacio=12)
    parrafo(
        doc,
        "Antes de entregar, reemplacen los nombres y guarden el archivo como Apellido_Nombre_Trabajo_Unidad3.docx.",
        tamano=11,
        cursiva=True,
        centro=True,
    )
    doc.add_page_break()

    titulo(doc, "Índice", 1)
    for linea in (
        "1. Introducción",
        "2. Objetivos",
        "3. Desarrollo",
        "4. Pruebas",
        "5. Análisis del uso de IA",
        "6. Conclusión",
        "7. Referencias",
    ):
        parrafo(doc, linea, espacio=2)
    doc.add_page_break()

    titulo(doc, "1. Introducción", 1)
    parrafo(
        doc,
        "En este trabajo armamos una aplicación sencilla para anotar productos. De cada uno guardamos el nombre, una descripción si hace falta, el precio y cuántas unidades hay. Se puede agregar un producto, ver los que ya están, cambiar sus datos y eliminarlo. La información no se pierde al cerrar el programa, porque queda en una base de datos.",
    )
    parrafo(
        doc,
        "No hicimos una pantalla complicada. La aplicación contesta por una dirección del computador, y las pruebas se hicieron pidiendo crear, ver, modificar y borrar. Esas pruebas están más abajo, con la captura de cada una.",
    )
    parrafo(
        doc,
        "Para programar usamos Cursor, que es una inteligencia artificial que ayuda a escribir código. No la usamos para que hiciera el trabajo sola. Nos ayudó a partir más rápido, y después leímos lo que propuso, lo probamos y corregimos lo que no nos convenció.",
    )

    titulo(doc, "2. Objetivos", 1)
    parrafo(doc, "Objetivo general", negrita=True, espacio=4)
    parrafo(
        doc,
        "Armar la aplicación de productos con ayuda de la inteligencia artificial, revisar lo que generó y dejar escrito qué nos sirvió, qué falló y qué tuvimos que cambiar.",
    )
    parrafo(doc, "Objetivos específicos", negrita=True, espacio=4)
    viñeta(doc, "Poder crear, consultar, modificar y eliminar productos, y que los datos queden guardados.")
    viñeta(doc, "Rechazar datos que no sirven, como un precio negativo, un nombre vacío o un stock escrito con palabras.")
    viñeta(doc, "Revisar el código que propuso la IA y corregir los problemas que encontramos.")
    viñeta(doc, "Dejar las pruebas hechas y responder qué aprendimos al usar la herramienta.")

    titulo(doc, "3. Desarrollo", 1)
    titulo(doc, "Qué problema queríamos resolver", 2)
    parrafo(
        doc,
        "Necesitábamos un inventario chico: saber qué producto es, cuánto vale y cuánto hay. Si alguien manda el precio en negativo, deja el nombre en blanco o escribe el stock con letras, la aplicación tiene que decir que no. No nos servía que guardara cualquier cosa o que contestara con un error difícil de entender.",
    )

    titulo(doc, "Con qué lo hicimos", 2)
    parrafo(
        doc,
        "Usamos Python y Django 5.2. Django es el framework: nos da la estructura de la aplicación, las direcciones y la forma de guardar datos. La base es SQLite. En la práctica es un archivo que se crea en la carpeta del proyecto, así que no hubo que instalar otro programa de base de datos (Django Software Foundation, 2025; SQLite Consortium, s. f.).",
    )
    parrafo(
        doc,
        "Todo el trabajo quedó dentro de la carpeta gestion_productos. Ahí está el proyecto, la parte de productos, el archivo para instalar Django y este informe.",
    )

    titulo(doc, "Cómo está organizada", 2)
    parrafo(
        doc,
        "Cuando llega un pedido, primero revisamos si los datos vienen bien. Si vienen bien, se guardan. Si no, respondemos qué campo está mal. Django escribe en la base por nosotros: nosotros no armamos la consulta pegando el texto que escribió la persona. Eso importa, porque si el nombre del producto trajera una orden rara, queda guardado como texto y no se ejecuta.",
    )
    parrafo(
        doc,
        "Si algo se rompe de verdad y no lo teníamos previsto, a quien hizo el pedido solo le decimos que hubo un error interno. El detalle queda en la consola del computador, no en la respuesta.",
    )

    titulo(doc, "Qué se puede hacer", 2)
    parrafo(
        doc,
        "Estas son las acciones. El número es la respuesta del servidor cuando todo sale como corresponde.",
    )
    viñeta(doc, "Crear un producto. Si queda guardado, la respuesta es 201.")
    viñeta(doc, "Ver el listado o ver uno solo. Si los datos se muestran, la respuesta es 200.")
    viñeta(doc, "Modificar nombre, precio, stock y descripción. Si el cambio queda hecho, la respuesta es 200.")
    viñeta(doc, "Eliminar. Si se borra, la respuesta es 204 y no viene texto, porque ya no hay nada que mostrar.")
    viñeta(doc, "Si piden un producto que no existe, la respuesta es 404.")
    viñeta(doc, "Si los datos vienen mal, la respuesta es 400 y se indica qué hay que corregir.")
    parrafo(
        doc,
        "El nombre no puede ir vacío ni pasar de 120 caracteres. La descripción es opcional y llega hasta 500. El precio tiene que ser mayor que cero y con dos decimales como máximo. El stock tiene que ser un número entero, de cero hacia arriba.",
    )

    titulo(doc, "Cómo usamos la inteligencia artificial", 2)
    parrafo(
        doc,
        "Usamos Cursor en tres momentos. En cada uno anotamos qué necesitábamos, qué le pedimos, qué entregó, qué cambiamos nosotros y si el resultado nos sirvió.",
    )

    parrafo(doc, "Primera interacción. Armar el proyecto y el producto", negrita=True, espacio=4)
    parrafo(
        doc,
        "Necesitábamos partir el proyecto y definir qué datos tiene un producto, y que todo quedara en su propia carpeta. Le pedimos un proyecto Django de gestión de productos, con nombre, descripción, precio y stock, guardado en SQLite, dentro de la carpeta gestion_productos. Cursor creó el proyecto, el modelo y la base. Nosotros pedimos que no quedara suelto en la carpeta de arriba, y borramos el entorno que se había creado fuera. El resultado nos sirvió: la estructura se entiende y el producto tiene los datos que pedía el trabajo.",
    )

    parrafo(doc, "Segunda interacción. Crear, ver, modificar y eliminar", negrita=True, espacio=4)
    parrafo(
        doc,
        "Necesitábamos las cuatro acciones, sin diseñar una página. Le pedimos las direcciones para crear y listar, y para ver, cambiar y borrar un producto, con respuestas distintas según lo que pase. Cursor dejó esas direcciones en la aplicación. Nosotros preferimos no sumar otra librería: con lo que trae Django alcanza y es más fácil de explicar. El resultado nos sirvió, aunque igual lo revisamos, porque una respuesta generada puede decir que todo salió bien aunque el dato no se haya guardado.",
    )

    parrafo(doc, "Tercera interacción. Revisar los datos y los errores", negrita=True, espacio=4)
    parrafo(
        doc,
        "Necesitábamos que un dato malo no entrara, y que un error no mostrara información del computador. Le pedimos revisar el nombre, el precio, el stock, los pedidos que no son un texto válido y los campos que no corresponden. También pedimos que la respuesta de un fallo grave fuera un mensaje corto. Cursor ordenó esas reglas en un archivo aparte. Esta fue la interacción que más hubo que mirar: con datos correctos todo se ve bien, y los problemas aparecen cuando uno prueba un precio negativo o un stock que no es un número. Eso lo corregimos, como se cuenta ahora.",
    )

    titulo(doc, "Dos problemas que vimos y cómo los resolvimos", 2)
    parrafo(
        doc,
        "El primero: al crear el proyecto, Django deja escrita en un archivo una clave secreta de la aplicación. Esa clave no debería viajar en el trabajo que se entrega. La sacamos de ahí. Ahora se lee desde una configuración del computador. En la carpeta hay un archivo de ejemplo, no la clave de verdad. Si alguien apaga el modo de prueba y olvida poner la clave, el programa no parte. Así evitamos publicar con una clave de mentira.",
    )
    parrafo(
        doc,
        "El segundo: el stock y el precio se podían colar mal. En Python, un verdadero o falso a veces se confunde con un número, y un stock en true podía guardarse como 1. El precio, si se trata como un decimal cualquiera, se puede redondear mal. Lo corregimos antes de guardar. El stock tiene que ser un entero de verdad. El precio tiene que ser mayor que cero y no puede traer más de dos decimales. Si mandan un id u otro dato que no pedimos, lo ignoramos y no dejamos que cambie datos internos.",
    )
    parrafo(
        doc,
        "Dejamos una limitación a la vista: la aplicación no tiene usuarios ni contraseñas. Alcanza para probarla en nuestro computador. No está pensada para subirla a internet así como está.",
    )

    titulo(doc, "Cuidados que dejamos puestos", 2)
    viñeta(doc, "Revisamos nombre, precio y stock antes de guardar.")
    viñeta(doc, "Si el pedido viene mal, respondemos 400 y decimos qué falló. Si el producto no está, respondemos 404.")
    viñeta(doc, "Si hay un error que no esperábamos, la persona solo ve un mensaje general. No le mostramos rutas ni detalles internos.")
    viñeta(doc, "La clave de Django no va en las respuestas ni en el archivo que se entrega.")
    viñeta(
        doc,
        "Las consultas a la base las hace Django. Probamos guardar un nombre que parece una orden para borrar la tabla: se guardó como texto y la tabla siguió existiendo (OWASP Foundation, s. f.).",
    )
    viñeta(doc, "Solo declaramos Django como dependencia. No instalamos paquetes de más.")

    titulo(doc, "4. Pruebas", 1)
    parrafo(
        doc,
        "Hicimos las cinco pruebas que pide el trabajo, el 22 de noviembre de 2026, contra la aplicación encendida en el computador. En la tabla, Exitoso quiere decir que pasó lo que dice la columna de al lado. En la última fila, el éxito es que el pedido haya sido rechazado.",
    )
    tabla(
        doc,
        [
            ("Prueba", "Resultado esperado", "Resultado obtenido"),
            ("Creación de información", "Registro realizado correctamente", "Exitoso"),
            ("Consulta de información", "Datos mostrados correctamente", "Exitoso"),
            ("Modificación de información", "Datos actualizados correctamente", "Exitoso"),
            ("Eliminación de información", "Registro eliminado correctamente", "Exitoso"),
            ("Ingreso de datos inválidos", "Solicitud rechazada o validada correctamente", "Exitoso"),
        ],
    )
    parrafo(
        doc,
        "Primero creamos un cuaderno de tapa dura, a 1990.50 y con 10 unidades. El servidor respondió 201, que significa creado. Después consultamos el listado y el producto suelto, y aparecieron esos mismos datos. Luego lo cambiamos a Cuaderno A4, precio 2500.00 y stock 4. Al eliminarlo, la respuesta fue 204, y al volver a pedirlo el servidor contestó 404: ya no estaba.",
    )
    parrafo(
        doc,
        "La quinta prueba es la de seguridad. Mandamos un nombre en blanco, un precio de -5 y un stock escrito como diez. El servidor respondió 400 y explicó cada error. No guardó ese producto.",
    )

    figura(doc, "01-crear.png", "Figura 1. Creación del cuaderno. La respuesta 201 indica que quedó guardado.")
    figura(doc, "02-consultar.png", "Figura 2. Consulta del listado y del producto recién creado.")
    figura(doc, "03-modificar.png", "Figura 3. Modificación del nombre, el precio y el stock.")
    figura(doc, "04-eliminar.png", "Figura 4. Eliminación del producto y comprobación de que ya no existe.")
    figura(
        doc,
        "05-datos-invalidos.png",
        "Figura 5. Rechazo de un nombre vacío, un precio negativo y un stock que no es un número.",
    )
    parrafo(
        doc,
        "Además, el propio programa trae ocho pruebas automáticas que cubren estos mismos casos y algunos más, como un precio con tres decimales o un error interno que no debe mostrar la ruta del computador. Esas ocho terminaron bien.",
    )

    titulo(doc, "5. Análisis del uso de IA", 1)

    pregunta(doc, "¿Qué tareas fueron aceleradas mediante IA?")
    parrafo(
        doc,
        "Nos ahorró el arranque: la carpeta del proyecto, los datos del producto, las direcciones y un primer borrador de las pruebas. Eso, escrito a mano, es bastante repetitivo. Con un pedido claro, Cursor lo dejó armado y nosotros pasamos el tiempo en revisar y probar, no en crear archivos vacíos.",
    )

    pregunta(doc, "¿Qué resultados generados fueron útiles?")
    parrafo(
        doc,
        "Nos sirvió la separación entre el proyecto y la parte de productos, que el precio quedara como un decimal de verdad y que cada acción tuviera su respuesta. También nos sirvió tener de una vez las pruebas de crear, ver, cambiar, borrar y rechazar. Eso sí, lo útil fue el punto de partida. Igual hubo que leerlo.",
    )

    pregunta(doc, "¿Qué errores o limitaciones fueron detectados?")
    parrafo(
        doc,
        "Django dejó la clave secreta escrita en el archivo de configuración. Ese no es un error de la IA sola: es lo que hace el comando al crear el proyecto, y había que notarlo. El otro límite es de los datos: un stock en verdadero o falso se podía confundir con un 1, y un precio mal escrito no debía llegar a la base. Además, la aplicación no pide usuario. Si solo probáramos el cuaderno con un precio correcto, esos problemas no se ven.",
    )

    pregunta(doc, "¿Qué modificaciones tuvieron que realizar los estudiantes?")
    parrafo(
        doc,
        "Dejamos todo dentro de la carpeta gestion_productos. Sacamos la clave del código y la pasamos a una configuración aparte. Rechazamos el stock que no es un entero, los precios negativos o con demasiados decimales, y los campos que no corresponden al producto. Hicimos que un error grave no cuente detalles. Y agregamos las pruebas que demuestran eso, no solo el caso que sale bien.",
    )

    pregunta(doc, "¿Qué riesgos identificaron al utilizar código generado por IA?")
    parrafo(
        doc,
        "El riesgo más claro es que el código se ve bien y funciona con el ejemplo, pero falla en los casos raros. También puede mostrar de más cuando hay un error, o guardar todo lo que venga en el pedido, incluso datos que el usuario no debería poder cambiar. Si lo entregamos sin leerlo, después no sabemos explicar qué hace ni darnos cuenta del fallo.",
    )

    pregunta(doc, "¿En qué situaciones consideran que la IA no debería utilizarse sin revisión humana?")
    parrafo(
        doc,
        "Cuando el código toca claves, datos de personas, permisos, pagos o borrado de información. También cuando el resultado se va a entregar como propio y nadie del grupo puede recorrerlo y explicarlo. En este trabajo la revisión era parte de la tarea, no un extra.",
    )

    pregunta(doc, "¿Cuál es la principal diferencia entre generar código con IA y desarrollar software asistido por IA?")
    parrafo(
        doc,
        "Generar código es pedir un pedazo y pegarlo. Desarrollar con asistencia es pedir una parte, leerla, probarla y cambiar lo que no cumple lo que nosotros necesitamos. En este trabajo hicimos lo segundo: las tres interacciones terminan con un cambio nuestro o con un límite que dejamos escrito. No aceptamos un archivo a ciegas.",
    )

    pregunta(doc, "¿Por qué un desarrollador debe revisar y validar el código generado por una herramienta de inteligencia artificial?")
    parrafo(
        doc,
        "Porque la herramienta propone un texto que suele funcionar, pero no demuestra que cumpla nuestra regla ni que sea seguro. En este proyecto, aceptar true como stock es un ejemplo chico y real: el programa no se cae, el dato queda mal y nadie avisa. Por eso hay que probar también lo que no debería guardarse.",
    )

    pregunta(doc, "¿Qué ventajas y limitaciones encontraron al utilizar IA durante el desarrollo de la aplicación?")
    parrafo(
        doc,
        "La ventaja fue tener pronto una aplicación ordenada y pruebas que se pueden volver a correr. La limitación fue que el primer resultado alcanzaba para el caso feliz y no para los datos malos ni para la clave secreta. Hizo falta un pedido más concreto y, después, mirar el código. Sin ese segundo paso, este informe no tendría nada que corregir y eso habría sido mala señal.",
    )

    pregunta(doc, "¿Qué riesgos de seguridad puede introducir el código generado por IA?")
    parrafo(
        doc,
        "Puede armar consultas a la base juntando texto del usuario, puede guardar campos que no debería, puede contar en el error la ruta de un archivo o una clave, y puede sumar librerías que nadie revisó. También puede dejar una aplicación abierta como si ya estuviera lista para internet. En la nuestra, Django hace las consultas y solo guardamos los campos que definimos. La falta de usuarios sigue ahí, y por eso decimos que es una aplicación local.",
    )

    pregunta(doc, "¿Por qué un prompt con mayor contexto puede producir mejores resultados que una instrucción demasiado general?")
    parrafo(
        doc,
        "Si solo decimos «haz un sistema de productos», la herramienta elige por su cuenta si el precio puede ser cero, si el stock lleva decimales y qué contestar cuando algo falla. Esas elecciones pueden no ser las del enunciado. Cuando contamos que es Django, que la base es SQLite, cuáles son las cuatro acciones y qué datos no se aceptan, la propuesta nace más cerca de lo que hay que entregar. El contexto no reemplaza la revisión: evita una parte de las correcciones.",
    )

    titulo(doc, "6. Conclusión", 1)
    parrafo(
        doc,
        "La aplicación permite crear, consultar, modificar y eliminar productos, guarda los datos y rechaza los que vienen mal. Las cinco pruebas del enunciado salieron como esperábamos, y también las ocho pruebas automáticas del programa.",
    )
    parrafo(
        doc,
        "Lo más difícil no fue crear el cuaderno. Fue tratar lo que escribió la IA como una propuesta y no como la versión final. El proyecto nació con la clave secreta a la vista, y una revisión floja de los datos habría dejado pasar un stock que no es un número. Corregir eso, y probarlo, es la parte que no se puede delegar.",
    )
    parrafo(
        doc,
        "Lo que nos queda es que programar con ayuda de una IA pide tres cosas juntas: un pedido con el contexto de la tarea, una lectura de lo que devolvió y una prueba que falle si la regla se rompe. Si falta la última, la herramienta solo nos hace ir más rápido hacia un programa que no revisamos.",
    )

    titulo(doc, "7. Referencias", 1)
    for cita in (
        "Django Software Foundation. (2025). Django documentation (5.2). https://docs.djangoproject.com/en/5.2/",
        "OWASP Foundation. (s. f.). SQL injection. https://owasp.org/www-community/attacks/SQL_Injection",
        "SQLite Consortium. (s. f.). About SQLite. https://www.sqlite.org/about.html",
    ):
        bloque = parrafo(doc, cita, espacio=8)
        bloque.paragraph_format.left_indent = Cm(1.25)
        bloque.paragraph_format.first_line_indent = Cm(-1.25)

    doc.save(SALIDA)
    print(SALIDA)


if __name__ == "__main__":
    construir()
