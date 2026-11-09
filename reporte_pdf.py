"""
reporte_pdf.py
Genera los PDF del sistema con ReportLab:
  - generar_pdf: reporte general (tabla con encabezado, total y paginación).
  - generar_pdf_expediente: expediente clínico completo de un paciente.
Se llaman desde los botones "Generar PDF" de la interfaz (en un hilo).
"""
from datetime import date, datetime
from xml.sax.saxutils import escape
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

VERDE = colors.HexColor("#176B4D")
GRIS = colors.HexColor("#5A6B63")
FILA_ALTERNA = colors.HexColor("#F0F8F4")
LINEA = colors.HexColor("#C9DDD3")


def _estilos():
    """Estilos de texto usados en los documentos."""
    base = getSampleStyleSheet()
    return {
        "inst": ParagraphStyle("inst", parent=base["Title"], fontSize=16, textColor=VERDE),
        "titulo": ParagraphStyle("tit", parent=base["Heading2"], alignment=1),
        "sub": ParagraphStyle("sub", parent=base["Normal"], alignment=1,
                              fontSize=9, textColor=GRIS),
        "seccion": ParagraphStyle("sec", parent=base["Heading3"], textColor=VERDE,
                                  spaceBefore=10),
        "cab": ParagraphStyle("cab", parent=base["Normal"], fontName="Helvetica-Bold",
                              fontSize=9, textColor=colors.white),
        "cel": ParagraphStyle("cel", parent=base["Normal"], fontSize=8, leading=10),
        "etq": ParagraphStyle("etq", parent=base["Normal"], fontName="Helvetica-Bold",
                              fontSize=9),
        "val": ParagraphStyle("val", parent=base["Normal"], fontSize=9),
    }


def _texto(valor):
    return escape("" if valor is None else str(valor))


def _pie(canvas, doc):
    """Dibuja en cada página el pie con el nombre del sistema y el número de página."""
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(GRIS)
    canvas.drawString(doc.leftMargin, 1.1 * cm,
                      "SGCEP - Sistema Gestor de Consultas y Expedientes de Pacientes")
    canvas.drawRightString(doc.pagesize[0] - doc.rightMargin, 1.1 * cm,
                           f"Página {doc.page}")
    canvas.restoreState()


def _tabla(encabezados, filas, ancho_total, est, anchos=None):
    """Arma una tabla con estilo (TableStyle): encabezado verde y filas alternas."""
    datos = [[Paragraph(_texto(h), est["cab"]) for h in encabezados]]
    for fila in filas:
        datos.append([Paragraph(_texto(v), est["cel"]) for v in fila])
    anchos = anchos or [ancho_total / len(encabezados)] * len(encabezados)
    tabla = Table(datos, colWidths=anchos, repeatRows=1)  # repite el encabezado
    tabla.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), VERDE),
        ("GRID", (0, 0), (-1, -1), 0.4, LINEA),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, FILA_ALTERNA]),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    return tabla


def _encabezado(est, titulo, subtitulo, total=None):
    elementos = [
        Paragraph("Sistema Gestor de Consultas y Expedientes de Pacientes", est["inst"]),
        Paragraph(escape(titulo), est["titulo"]),
        Paragraph(escape(subtitulo), est["sub"]),
    ]
    pie = f"Generado: {datetime.now():%d/%m/%Y %H:%M}"
    if total is not None:
        pie += f" | Total de registros: {total}"
    elementos += [Paragraph(pie, est["sub"]), Spacer(1, 0.5 * cm)]
    return elementos


def generar_pdf(ruta, titulo, subtitulo, encabezados, filas):
    """Reporte general: una tabla con los encabezados y filas recibidos."""
    # Con muchas columnas se usa la hoja en horizontal para que quepan
    tamano = landscape(letter) if len(encabezados) > 5 else letter
    margen = 1.5 * cm
    doc = SimpleDocTemplate(ruta, pagesize=tamano, leftMargin=margen,
                            rightMargin=margen, topMargin=1.8 * cm,
                            bottomMargin=2 * cm, title=titulo)
    est = _estilos()
    contenido = _encabezado(est, titulo, subtitulo, total=len(filas))
    if filas:
        contenido.append(_tabla(encabezados, filas, tamano[0] - 2 * margen, est))
    else:
        contenido.append(Paragraph("No hay registros para mostrar.", est["val"]))
    doc.build(contenido, onFirstPage=_pie, onLaterPages=_pie)
    return ruta


def generar_pdf_expediente(ruta, exp):
    """Expediente clínico: datos del paciente, historial de consultas y tratamientos.
    'exp' es el diccionario que devuelve repositorio.expediente()."""
    p = exp["paciente"]
    margen = 1.5 * cm
    tamano = letter
    ancho = tamano[0] - 2 * margen
    doc = SimpleDocTemplate(ruta, pagesize=tamano, leftMargin=margen,
                            rightMargin=margen, topMargin=1.8 * cm,
                            bottomMargin=2 * cm, title="Expediente clínico")
    est = _estilos()
    nombre = f"{p['nombre']} {p['apellido']}"
    contenido = _encabezado(est, "Expediente clínico", nombre)

    # --- Datos del paciente (tabla de dos pares etiqueta/valor por fila) ---
    nac = p["fecha_nacimiento"]
    edad = ""
    if isinstance(nac, date):
        hoy = date.today()
        edad = hoy.year - nac.year - ((hoy.month, hoy.day) < (nac.month, nac.day))
    sexo = {"M": "Masculino", "F": "Femenino"}.get(p["sexo"], p["sexo"])
    pares = [
        ("Cédula", p["cedula"]), ("Sexo", sexo),
        ("Fecha de nacimiento", f"{nac} ({edad} años)" if edad != "" else nac),
        ("Tipo de sangre", p["tipo_sangre"]),
        ("Teléfono", p["telefono"]), ("Correo", p["correo"]),
        ("Dirección", p["direccion"]), ("Alergias", p["alergias"]),
    ]
    filas = []
    for i in range(0, len(pares), 2):
        fila = []
        for etq, val in pares[i:i + 2]:
            fila += [Paragraph(etq + ":", est["etq"]), Paragraph(_texto(val), est["val"])]
        filas.append(fila)
    datos = Table(filas, colWidths=[ancho * 0.17, ancho * 0.33, ancho * 0.17, ancho * 0.33])
    datos.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 0.6, LINEA),
        ("INNERGRID", (0, 0), (-1, -1), 0.3, LINEA),
        ("BACKGROUND", (0, 0), (0, -1), FILA_ALTERNA),
        ("BACKGROUND", (2, 0), (2, -1), FILA_ALTERNA),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    contenido += [Paragraph("Datos del paciente", est["seccion"]), datos]

    # --- Historial de consultas ---
    contenido.append(Paragraph(f"Historial de consultas ({len(exp['consultas'])})", est["seccion"]))
    if exp["consultas"]:
        filas_c = [(f, m, s, d, t, o) for (_i, f, m, s, d, t, o) in exp["consultas"]]
        contenido.append(_tabla(
            ["Fecha", "Motivo", "Síntomas", "Diagnóstico", "Tratamiento", "Observaciones"],
            filas_c, ancho, est,
            anchos=[ancho * 0.11, ancho * 0.16, ancho * 0.18, ancho * 0.18,
                    ancho * 0.19, ancho * 0.18]))
    else:
        contenido.append(Paragraph("El paciente no tiene consultas registradas.", est["val"]))

    # --- Tratamientos ---
    contenido.append(Paragraph(f"Tratamientos ({len(exp['tratamientos'])})", est["seccion"]))
    if exp["tratamientos"]:
        filas_t = [(m, d, f, du, ind) for (_i, m, d, f, du, ind) in exp["tratamientos"]]
        contenido.append(_tabla(
            ["Medicamento", "Dosis", "Frecuencia", "Duración", "Indicaciones"],
            filas_t, ancho, est))
    else:
        contenido.append(Paragraph("El paciente no tiene tratamientos registrados.", est["val"]))

    doc.build(contenido, onFirstPage=_pie, onLaterPages=_pie)
    return ruta
