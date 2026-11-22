"""Completa la plantilla institucional sin tocar la portada ni el membrete."""

from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

RAIZ = Path(__file__).resolve().parents[1].parent
PLANTILLA = RAIZ / "Salazar_Luis_Trabajo_Unidad3.docx"
CAPTURAS = Path(__file__).resolve().parent / "capturas"
GRIS = RGBColor(0x7F, 0x7F, 0x7F)
NEGRO = RGBColor(0x00, 0x00, 0x00)


def fuente(run, tamano, negrita=False, cursiva=False, color=NEGRO):
    run.bold = negrita
    run.italic = cursiva
    run.font.size = Pt(tamano)
    run.font.color.rgb = color
    run.font.name = "Calibri"
    rpr = run._element.get_or_add_rPr()
    rfonts = rpr.find(qn("w:rFonts"))
    if rfonts is None:
        rfonts = OxmlElement("w:rFonts")
        rpr.append(rfonts)
    for atributo in ("w:ascii", "w:hAnsi", "w:cs"):
        rfonts.set(qn(atributo), "Calibri")


def texto(doc, contenido, tamano=12, negrita=False, cursiva=False, color=NEGRO, centro=False, antes=0, despues=6):
    bloque = doc.add_paragraph()
    formato = bloque.paragraph_format
    formato.space_before = Pt(antes)
    formato.space_after = Pt(despues)
    formato.line_spacing = 1.15
    if centro:
        bloque.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = bloque.add_run(contenido)
    fuente(run, tamano, negrita, cursiva, color)
    return bloque


def seccion(doc, contenido):
    texto(doc, contenido, tamano=16, negrita=True, color=GRIS, antes=14, despues=6)


def subseccion(doc, contenido):
    texto(doc, contenido, tamano=13, negrita=True, color=GRIS, antes=10, despues=4)


def viñeta(doc, contenido):
    texto(doc, f"• {contenido}", despues=3)


def pregunta(doc, contenido):
    texto(doc, contenido, negrita=True, antes=8, despues=2)


def borde(celda):
    tcpr = celda._tc.get_or_add_tcPr()
    bordes = OxmlElement("w:tcBorders")
    for lado in ("top", "left", "bottom", "right"):
        nodo = OxmlElement(f"w:{lado}")
        nodo.set(qn("w:val"), "single")
        nodo.set(qn("w:sz"), "4")
        nodo.set(qn("w:color"), "7F7F7F")
        bordes.append(nodo)
    tcpr.append(bordes)


def tabla(doc, filas):
    cuadro = doc.add_table(rows=len(filas), cols=len(filas[0]))
    for i, fila in enumerate(filas):
        for j, valor in enumerate(fila):
            celda = cuadro.rows[i].cells[j]
            celda.text = ""
            bloque = celda.paragraphs[0]
            bloque.paragraph_format.space_after = Pt(2)
            run = bloque.add_run(valor)
            fuente(run, 11, negrita=(i == 0))
            borde(celda)
    texto(doc, "", despues=6)


def figura(doc, archivo, pie):
    ruta = CAPTURAS / archivo
    if not ruta.exists():
        ruta = CAPTURAS / archivo.replace("recorte-", "")
    bloque = doc.add_paragraph()
    bloque.alignment = WD_ALIGN_PARAGRAPH.CENTER
    bloque.paragraph_format.space_before = Pt(6)
    bloque.paragraph_format.space_after = Pt(2)
    bloque.add_run().add_picture(str(ruta), width=Cm(14.8))
    texto(doc, pie, tamano=10, cursiva=True, color=GRIS, centro=True, despues=8)


def titulo_en_portada(doc):
    for bloque in doc.paragraphs:
        if bloque.text.strip():
            continue
        marca = bloque._p.find(qn("w:pPr"))
        if marca is None:
            continue
        rpr = marca.find(qn("w:rPr"))
        if rpr is None or rpr.find(qn("w:sz")) is None:
            continue
        if rpr.find(qn("w:sz")).get(qn("w:val")) != "32":
            continue
        bloque.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = bloque.add_run("Gestión de productos")
        fuente(run, 20, negrita=True, color=GRIS)
        return


def quitar_cuerpo_vacio(doc):
    corte = None
    for bloque in doc.paragraphs:
        if bloque._p.xml.find("w:type=\"page\"") != -1 or "w:type=\"page\"" in bloque._p.xml:
            corte = bloque
            break
    if corte is None:
        raise SystemExit("No encontré el salto de página de la portada.")
    siguiente = corte._element.getnext()
    while siguiente is not None and siguiente.tag != qn("w:sectPr"):
        borrar = siguiente
        siguiente = siguiente.getnext()
        borrar.getparent().remove(borrar)


def completar():
    doc = Document(str(PLANTILLA))
    titulo_en_portada(doc)
    quitar_cuerpo_vacio(doc)

    seccion(doc, "Índice")
    for linea in (
        "1. Introducción",
        "2. Objetivos",
        "3. Desarrollo",
        "4. Pruebas",
        "5. Análisis del uso de IA",
        "6. Conclusión",
        "7. Referencias",
    ):
        texto(doc, linea, despues=2)
    doc.add_page_break()

    seccion(doc, "1. Introducción")
    texto(
        doc,
        "En este trabajo armamos una aplicación sencilla para anotar productos. De cada uno guardamos el nombre, una descripción si hace falta, el precio y cuántas unidades hay. Se puede agregar un producto, ver los que ya están, cambiar sus datos y eliminarlo. La información no se pierde al cerrar el programa, porque queda en una base de datos.",
    )
    texto(
        doc,
        "No hicimos una pantalla complicada. La aplicación contesta por una dirección del computador, y las pruebas se hicieron pidiendo crear, ver, modificar y borrar. Esas pruebas están más abajo, con la captura de cada una.",
    )
    texto(
        doc,
        "Para programar usamos Cursor, que es una inteligencia artificial que ayuda a escribir código. No la usamos para que hiciera el trabajo sola. Nos ayudó a partir más rápido, y después leímos lo que propuso, lo probamos y corregimos lo que no nos convenció.",
    )

    seccion(doc, "2. Objetivos")
    texto(doc, "Objetivo general", negrita=True, despues=2)
    texto(
        doc,
        "Armar la aplicación de productos con ayuda de la inteligencia artificial, revisar lo que generó y dejar escrito qué nos sirvió, qué falló y qué tuvimos que cambiar.",
    )
    texto(doc, "Objetivos específicos", negrita=True, antes=6, despues=2)
    viñeta(doc, "Poder crear, consultar, modificar y eliminar productos, y que los datos queden guardados.")
    viñeta(doc, "Rechazar datos que no sirven, como un precio negativo, un nombre vacío o un stock escrito con palabras.")
    viñeta(doc, "Revisar el código que propuso la IA y corregir los problemas que encontramos.")
    viñeta(doc, "Dejar las pruebas hechas y responder qué aprendimos al usar la herramienta.")

    seccion(doc, "3. Desarrollo")
    subseccion(doc, "Qué problema queríamos resolver")
    texto(
        doc,
        "Necesitábamos un inventario chico: saber qué producto es, cuánto vale y cuánto hay. Si alguien manda el precio en negativo, deja el nombre en blanco o escribe el stock con letras, la aplicación tiene que decir que no. No nos servía que guardara cualquier cosa o que contestara con un error difícil de entender.",
    )

    subseccion(doc, "Con qué lo hicimos")
    texto(
        doc,
        "Usamos Python y Django 5.2. Django es el framework: nos da la estructura de la aplicación, las direcciones y la forma de guardar datos. La base es SQLite. En la práctica es un archivo que se crea en la carpeta del proyecto, así que no hubo que instalar otro programa de base de datos (Django Software Foundation, 2025; SQLite Consortium, s. f.).",
    )
    texto(
        doc,
        "Todo el trabajo quedó dentro de la carpeta gestion_productos. Ahí está el proyecto, la parte de productos, el archivo para instalar Django y las instrucciones para ejecutarlo.",
    )

    subseccion(doc, "Cómo está organizada")
    texto(
        doc,
        "Cuando llega un pedido, primero revisamos si los datos vienen bien. Si vienen bien, se guardan. Si no, respondemos qué campo está mal. Django escribe en la base por nosotros: nosotros no armamos la consulta pegando el texto que escribió la persona. Eso importa, porque si el nombre del producto trajera una orden rara, queda guardado como texto y no se ejecuta.",
    )
    texto(
        doc,
        "Si algo se rompe de verdad y no lo teníamos previsto, a quien hizo el pedido solo le decimos que hubo un error interno. El detalle queda en la consola del computador, no en la respuesta.",
    )

    subseccion(doc, "Qué se puede hacer")
    texto(doc, "Estas son las acciones. El número es la respuesta del servidor cuando todo sale como corresponde.")
    viñeta(doc, "Crear un producto. Si queda guardado, la respuesta es 201.")
    viñeta(doc, "Ver el listado o ver uno solo. Si los datos se muestran, la respuesta es 200.")
    viñeta(doc, "Modificar nombre, precio, stock y descripción. Si el cambio queda hecho, la respuesta es 200.")
    viñeta(doc, "Eliminar. Si se borra, la respuesta es 204 y no viene texto, porque ya no hay nada que mostrar.")
    viñeta(doc, "Si piden un producto que no existe, la respuesta es 404.")
    viñeta(doc, "Si los datos vienen mal, la respuesta es 400 y se indica qué hay que corregir.")
    texto(
        doc,
        "El nombre no puede ir vacío ni pasar de 120 caracteres. La descripción es opcional y llega hasta 500. El precio tiene que ser mayor que cero y con dos decimales como máximo. El stock tiene que ser un número entero, de cero hacia arriba.",
    )

    subseccion(doc, "Cómo usamos la inteligencia artificial")
    texto(
        doc,
        "Usamos Cursor en tres momentos. En cada uno anotamos qué necesitábamos, qué le pedimos, qué entregó, qué cambiamos nosotros y si el resultado nos sirvió.",
    )
    texto(doc, "Primera interacción. Armar el proyecto y el producto", negrita=True, antes=6, despues=2)
    texto(
        doc,
        "Necesitábamos partir el proyecto y definir qué datos tiene un producto, y que todo quedara en su propia carpeta. Le pedimos un proyecto Django de gestión de productos, con nombre, descripción, precio y stock, guardado en SQLite, dentro de la carpeta gestion_productos. Cursor creó el proyecto, el modelo y la base. Nosotros pedimos que no quedara suelto en la carpeta de arriba, y borramos el entorno que se había creado fuera. El resultado nos sirvió: la estructura se entiende y el producto tiene los datos que pedía el trabajo.",
    )
    texto(doc, "Segunda interacción. Crear, ver, modificar y eliminar", negrita=True, antes=6, despues=2)
    texto(
        doc,
        "Necesitábamos las cuatro acciones, sin diseñar una página. Le pedimos las direcciones para crear y listar, y para ver, cambiar y borrar un producto, con respuestas distintas según lo que pase. Cursor dejó esas direcciones en la aplicación. Nosotros preferimos no sumar otra librería: con lo que trae Django alcanza y es más fácil de explicar. El resultado nos sirvió, aunque igual lo revisamos, porque una respuesta generada puede decir que todo salió bien aunque el dato no se haya guardado.",
    )
    texto(doc, "Tercera interacción. Revisar los datos y los errores", negrita=True, antes=6, despues=2)
    texto(
        doc,
        "Necesitábamos que un dato malo no entrara, y que un error no mostrara información del computador. Le pedimos revisar el nombre, el precio, el stock, los pedidos que no son un texto válido y los campos que no corresponden. También pedimos que la respuesta de un fallo grave fuera un mensaje corto. Cursor ordenó esas reglas en un archivo aparte. Esta fue la interacción que más hubo que mirar: con datos correctos todo se ve bien, y los problemas aparecen cuando uno prueba un precio negativo o un stock que no es un número. Eso lo corregimos, como se cuenta ahora.",
    )

    subseccion(doc, "Dos problemas que vimos y cómo los resolvimos")
    texto(
        doc,
        "El primero: al crear el proyecto, Django deja escrita en un archivo una clave secreta de la aplicación. Esa clave no debería viajar en el trabajo que se entrega. La sacamos de ahí. Ahora se lee desde una configuración del computador. En la carpeta hay un archivo de ejemplo, no la clave de verdad. Si alguien apaga el modo de prueba y olvida poner la clave, el programa no parte. Así evitamos publicar con una clave de mentira.",
    )
    texto(
        doc,
        "El segundo: el stock y el precio se podían colar mal. En Python, un verdadero o falso a veces se confunde con un número, y un stock en true podía guardarse como 1. El precio, si se trata como un decimal cualquiera, se puede redondear mal. Lo corregimos antes de guardar. El stock tiene que ser un entero de verdad. El precio tiene que ser mayor que cero y no puede traer más de dos decimales. Si mandan un id u otro dato que no pedimos, lo ignoramos y no dejamos que cambie datos internos.",
    )
    texto(
        doc,
        "Dejamos una limitación a la vista: la aplicación no tiene usuarios ni contraseñas. Alcanza para probarla en nuestro computador. No está pensada para subirla a internet así como está.",
    )

    subseccion(doc, "Cuidados que dejamos puestos")
    viñeta(doc, "Revisamos nombre, precio y stock antes de guardar.")
    viñeta(doc, "Si el pedido viene mal, respondemos 400 y decimos qué falló. Si el producto no está, respondemos 404.")
    viñeta(doc, "Si hay un error que no esperábamos, la persona solo ve un mensaje general. No le mostramos rutas ni detalles internos.")
    viñeta(doc, "La clave de Django no va en las respuestas ni en el archivo que se entrega.")
    viñeta(
        doc,
        "Las consultas a la base las hace Django. Probamos guardar un nombre que parece una orden para borrar la tabla: se guardó como texto y la tabla siguió existiendo (OWASP Foundation, s. f.).",
    )
    viñeta(doc, "Solo declaramos Django como dependencia. No instalamos paquetes de más.")

    seccion(doc, "4. Pruebas")
    texto(
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
    texto(
        doc,
        "Primero creamos un cuaderno de tapa dura, a 1990.50 y con 10 unidades. El servidor respondió 201, que significa creado. Después consultamos el listado y el producto suelto, y aparecieron esos mismos datos. Luego lo cambiamos a Cuaderno A4, precio 2500.00 y stock 4. Al eliminarlo, la respuesta fue 204, y al volver a pedirlo el servidor contestó 404: ya no estaba.",
    )
    texto(
        doc,
        "La quinta prueba es la de seguridad. Mandamos un nombre en blanco, un precio de -5 y un stock escrito como diez. El servidor respondió 400 y explicó cada error. No guardó ese producto.",
    )
    figura(doc, "recorte-01-crear.png", "Figura 1. Creación del cuaderno. La respuesta 201 indica que quedó guardado.")
    figura(doc, "recorte-02-consultar.png", "Figura 2. Consulta del listado y del producto recién creado.")
    figura(doc, "recorte-03-modificar.png", "Figura 3. Modificación del nombre, el precio y el stock.")
    figura(doc, "recorte-04-eliminar.png", "Figura 4. Eliminación del producto y comprobación de que ya no existe.")
    figura(
        doc,
        "recorte-05-datos-invalidos.png",
        "Figura 5. Rechazo de un nombre vacío, un precio negativo y un stock que no es un número.",
    )
    texto(
        doc,
        "Además, el propio programa trae ocho pruebas automáticas que cubren estos mismos casos y algunos más, como un precio con tres decimales o un error interno que no debe mostrar la ruta del computador. Esas ocho terminaron bien.",
    )

    seccion(doc, "5. Análisis del uso de IA")
    pregunta(doc, "¿Qué tareas fueron aceleradas mediante IA?")
    texto(
        doc,
        "Nos ahorró el arranque: la carpeta del proyecto, los datos del producto, las direcciones y un primer borrador de las pruebas. Eso, escrito a mano, es bastante repetitivo. Con un pedido claro, Cursor lo dejó armado y nosotros pasamos el tiempo en revisar y probar, no en crear archivos vacíos.",
    )
    pregunta(doc, "¿Qué resultados generados fueron útiles?")
    texto(
        doc,
        "Nos sirvió la separación entre el proyecto y la parte de productos, que el precio quedara como un decimal de verdad y que cada acción tuviera su respuesta. También nos sirvió tener de una vez las pruebas de crear, ver, cambiar, borrar y rechazar. Eso sí, lo útil fue el punto de partida. Igual hubo que leerlo.",
    )
    pregunta(doc, "¿Qué errores o limitaciones fueron detectados?")
    texto(
        doc,
        "Django dejó la clave secreta escrita en el archivo de configuración. Ese no es un error de la IA sola: es lo que hace el comando al crear el proyecto, y había que notarlo. El otro límite es de los datos: un stock en verdadero o falso se podía confundir con un 1, y un precio mal escrito no debía llegar a la base. Además, la aplicación no pide usuario. Si solo probáramos el cuaderno con un precio correcto, esos problemas no se ven.",
    )
    pregunta(doc, "¿Qué modificaciones tuvieron que realizar los estudiantes?")
    texto(
        doc,
        "Dejamos todo dentro de la carpeta gestion_productos. Sacamos la clave del código y la pasamos a una configuración aparte. Rechazamos el stock que no es un entero, los precios negativos o con demasiados decimales, y los campos que no corresponden al producto. Hicimos que un error grave no cuente detalles. Y agregamos las pruebas que demuestran eso, no solo el caso que sale bien.",
    )
    pregunta(doc, "¿Qué riesgos identificaron al utilizar código generado por IA?")
    texto(
        doc,
        "El riesgo más claro es que el código se ve bien y funciona con el ejemplo, pero falla en los casos raros. También puede mostrar de más cuando hay un error, o guardar todo lo que venga en el pedido, incluso datos que el usuario no debería poder cambiar. Si lo entregamos sin leerlo, después no sabemos explicar qué hace ni darnos cuenta del fallo.",
    )
    pregunta(doc, "¿En qué situaciones consideran que la IA no debería utilizarse sin revisión humana?")
    texto(
        doc,
        "Cuando el código toca claves, datos de personas, permisos, pagos o borrado de información. También cuando el resultado se va a entregar como propio y nadie del grupo puede recorrerlo y explicarlo. En este trabajo la revisión era parte de la tarea, no un extra.",
    )
    pregunta(doc, "¿Cuál es la principal diferencia entre generar código con IA y desarrollar software asistido por IA?")
    texto(
        doc,
        "Generar código es pedir un pedazo y pegarlo. Desarrollar con asistencia es pedir una parte, leerla, probarla y cambiar lo que no cumple lo que nosotros necesitamos. En este trabajo hicimos lo segundo: las tres interacciones terminan con un cambio nuestro o con un límite que dejamos escrito. No aceptamos un archivo a ciegas.",
    )
    pregunta(doc, "¿Por qué un desarrollador debe revisar y validar el código generado por una herramienta de inteligencia artificial?")
    texto(
        doc,
        "Porque la herramienta propone un texto que suele funcionar, pero no demuestra que cumpla nuestra regla ni que sea seguro. En este proyecto, aceptar true como stock es un ejemplo chico y real: el programa no se cae, el dato queda mal y nadie avisa. Por eso hay que probar también lo que no debería guardarse.",
    )
    pregunta(doc, "¿Qué ventajas y limitaciones encontraron al utilizar IA durante el desarrollo de la aplicación?")
    texto(
        doc,
        "La ventaja fue tener pronto una aplicación ordenada y pruebas que se pueden volver a correr. La limitación fue que el primer resultado alcanzaba para el caso feliz y no para los datos malos ni para la clave secreta. Hizo falta un pedido más concreto y, después, mirar el código. Sin ese segundo paso, este informe no tendría nada que corregir y eso habría sido mala señal.",
    )
    pregunta(doc, "¿Qué riesgos de seguridad puede introducir el código generado por IA?")
    texto(
        doc,
        "Puede armar consultas a la base juntando texto del usuario, puede guardar campos que no debería, puede contar en el error la ruta de un archivo o una clave, y puede sumar librerías que nadie revisó. También puede dejar una aplicación abierta como si ya estuviera lista para internet. En la nuestra, Django hace las consultas y solo guardamos los campos que definimos. La falta de usuarios sigue ahí, y por eso decimos que es una aplicación local.",
    )
    pregunta(doc, "¿Por qué un prompt con mayor contexto puede producir mejores resultados que una instrucción demasiado general?")
    texto(
        doc,
        "Si solo decimos «haz un sistema de productos», la herramienta elige por su cuenta si el precio puede ser cero, si el stock lleva decimales y qué contestar cuando algo falla. Esas elecciones pueden no ser las del enunciado. Cuando contamos que es Django, que la base es SQLite, cuáles son las cuatro acciones y qué datos no se aceptan, la propuesta nace más cerca de lo que hay que entregar. El contexto no reemplaza la revisión: evita una parte de las correcciones.",
    )

    seccion(doc, "6. Conclusión")
    texto(
        doc,
        "La aplicación permite crear, consultar, modificar y eliminar productos, guarda los datos y rechaza los que vienen mal. Las cinco pruebas del enunciado salieron como esperábamos, y también las ocho pruebas automáticas del programa.",
    )
    texto(
        doc,
        "Lo más difícil no fue crear el cuaderno. Fue tratar lo que escribió la IA como una propuesta y no como la versión final. El proyecto nació con la clave secreta a la vista, y una revisión floja de los datos habría dejado pasar un stock que no es un número. Corregir eso, y probarlo, es la parte que no se puede delegar.",
    )
    texto(
        doc,
        "Lo que nos queda es que programar con ayuda de una IA pide tres cosas juntas: un pedido con el contexto de la tarea, una lectura de lo que devolvió y una prueba que falle si la regla se rompe. Si falta la última, la herramienta solo nos hace ir más rápido hacia un programa que no revisamos.",
    )

    seccion(doc, "7. Referencias")
    for cita in (
        "Django Software Foundation. (2025). Django documentation (5.2). https://docs.djangoproject.com/en/5.2/",
        "OWASP Foundation. (s. f.). SQL injection. https://owasp.org/www-community/attacks/SQL_Injection",
        "SQLite Consortium. (s. f.). About SQLite. https://www.sqlite.org/about.html",
    ):
        bloque = texto(doc, cita, tamano=11)
        bloque.paragraph_format.left_indent = Cm(1.25)
        bloque.paragraph_format.first_line_indent = Cm(-1.25)

    doc.core_properties.title = "Trabajo Unidad 3. Gestión de productos"
    doc.core_properties.subject = "Framework de Desarrollo e Inteligencia Artificial"
    doc.core_properties.creator = "Luis Salazar Diaz"
    doc.save(str(PLANTILLA))
    print(PLANTILLA)


if __name__ == "__main__":
    completar()
