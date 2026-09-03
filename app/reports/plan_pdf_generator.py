"""
app/reports/plan_pdf_generator.py — PDF descargable del plan de sesión.

Usa ReportLab, igual que pdf_generator.py: ya es dependencia del proyecto y
es Python puro. WeasyPrint quedó descartado porque en Windows necesita las
librerías de sistema de GTK/Pango, que no están instaladas.

Reusa la paleta y los estilos de pdf_generator para que el plan salga con
la misma identidad visual que el reporte del alumno.

Uso: pdf_bytes = generate_session_plan_pdf(ps, student)
"""
import io
from datetime import datetime
from xml.sax.saxutils import escape as xml_escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    HRFlowable, PageBreak, Paragraph, Preformatted, SimpleDocTemplate,
    Spacer, Table, TableStyle,
)

from app.reports.pdf_generator import (
    C_AMBER, C_BLACK, C_GRAY, C_INDIGO, C_INDIGO2, C_LIGHT, C_WHITE,
    SCHOOL_CITY, SCHOOL_NAME, _build_styles,
)
from app.shared.filters import split_steps

# Ancho util con margenes de 2cm en A4. Courier 9pt mide 5.4pt por caracter,
# asi que entran ~88. Preformatted no corta solo: las lineas largas de la
# hoja del alumno se recortarian en silencio.
_ANCHO_MONO = 88


def _esc(texto):
    """ReportLab interpreta un mini-XML en Paragraph: hay que escapar."""
    return xml_escape(str(texto or ""))


def _envolver_mono(texto, ancho=_ANCHO_MONO):
    """Corta lineas largas respetando la sangria, para no perder contenido."""
    salida = []
    for linea in (texto or "").splitlines():
        if len(linea) <= ancho:
            salida.append(linea)
            continue
        sangria = len(linea) - len(linea.lstrip())
        prefijo = " " * sangria
        resto = linea.strip()
        while len(resto) > ancho - sangria:
            corte = resto.rfind(" ", 0, ancho - sangria)
            if corte <= 0:
                corte = ancho - sangria
            salida.append(prefijo + resto[:corte])
            resto = resto[corte:].lstrip()
        if resto:
            salida.append(prefijo + resto)
    return "\n".join(salida)


def _encabezado(ps, student, area_label, styles):
    rec = ps.ai_recommendation or {}
    meta = " · ".join(filter(None, [
        area_label,
        f"Nivel {ps.session_level}" if ps.session_level else None,
        f"{rec.get('duration_min')} min" if rec.get("duration_min") else None,
    ]))

    interior = [
        [Paragraph(f"{_esc(SCHOOL_NAME)}", styles["subtitle"])],
        [Paragraph("Plan de Sesión", styles["title"])],
        [Paragraph(_esc(ps.session_title or "Sesión pedagógica"), styles["subtitle"])],
    ]
    if meta:
        interior.append([Paragraph(_esc(meta), styles["subtitle"])])

    tabla = Table(interior, colWidths=[17 * cm])
    tabla.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), C_INDIGO2),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 12),
        ("RIGHTPADDING", (0, 0), (-1, -1), 12),
    ]))
    return [tabla, Spacer(1, 0.1 * cm),
            HRFlowable(width="100%", thickness=3, color=C_AMBER, spaceAfter=10)]


def _ficha(ps, student, styles):
    """Alumno / docente / fechas."""
    docente = ps.teacher.username if ps.teacher else "—"
    agendada = ps.scheduled_for.strftime("%d/%m/%Y") if ps.scheduled_for else "sin agendar"
    curso = student.grade or "—"
    if student.grade and student.section:
        curso = f"{student.grade} «{student.section}»"

    filas = [
        [Paragraph("Estudiante", styles["label"]), Paragraph(_esc(student.get_display_name()), styles["value"]),
         Paragraph("Docente", styles["label"]), Paragraph(_esc(docente), styles["value"])],
        [Paragraph("Curso", styles["label"]), Paragraph(_esc(curso), styles["value"]),
         Paragraph("Fecha de la sesión", styles["label"]), Paragraph(_esc(agendada), styles["value"])],
    ]
    tabla = Table(filas, colWidths=[3 * cm, 5.5 * cm, 3.5 * cm, 5 * cm])
    tabla.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), C_LIGHT),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#E5E7EB")),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, C_WHITE),
    ]))
    return [tabla, Spacer(1, 0.4 * cm)]


def _lista(titulo, items, styles):
    if not items:
        return []
    bloque = [Paragraph(_esc(titulo), styles["section"])]
    for i, it in enumerate(items, 1):
        bloque.append(Paragraph(f"{i}. {_esc(it)}", styles["bullet"]))
    return bloque


def _guia(ps, styles):
    if not ps.teacher_guide:
        return []

    pasos, es_lista = split_steps(ps.teacher_guide)
    bloque = [Paragraph("Guía para el docente", styles["section"])]

    if es_lista:
        for i, paso in enumerate(pasos, 1):
            bloque.append(Paragraph(f"<b>{i}.</b> {_esc(paso)}", styles["bullet"]))
    else:
        for linea in pasos:
            bloque.append(Paragraph(_esc(linea), styles["body"]))
    return bloque


def _rubrica(ps, styles):
    criterios = (ps.rubric or {}).get("criterios") or []
    if not criterios:
        return []

    celda = ParagraphStyle("CeldaRubrica", parent=styles["value"], fontSize=8, leading=11)
    encabezado = ParagraphStyle("EncRubrica", parent=styles["label"], fontSize=8,
                                textColor=C_WHITE, alignment=TA_CENTER)

    filas = [[
        Paragraph("Criterio", encabezado),
        Paragraph("Logrado", encabezado),
        Paragraph("En proceso", encabezado),
        Paragraph("Inicial", encabezado),
    ]]

    for c in criterios:
        niveles = c.get("niveles") or {}
        titulo = f"<b>{_esc(c.get('nombre'))}</b>"
        if c.get("descripcion"):
            titulo += f"<br/><font color='#6B7280'>{_esc(c.get('descripcion'))}</font>"
        filas.append([
            Paragraph(titulo, celda),
            Paragraph(_esc(niveles.get("logrado") or "—"), celda),
            Paragraph(_esc(niveles.get("en_proceso") or "—"), celda),
            Paragraph(_esc(niveles.get("inicial") or "—"), celda),
        ])

    tabla = Table(filas, colWidths=[4.6 * cm, 4.2 * cm, 4.2 * cm, 4 * cm], repeatRows=1)
    tabla.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), C_INDIGO),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#D1D5DB")),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [C_WHITE, colors.HexColor("#F9FAFB")]),
    ]))
    return [Paragraph("Rúbrica de evaluación", styles["section"]), tabla]


def _hoja_alumno(ps, student, styles):
    """Va en página nueva: es lo que se le entrega al niño."""
    if not ps.student_worksheet:
        return []

    mono = ParagraphStyle(
        "HojaMono", parent=styles["body"],
        fontName="Courier", fontSize=9, leading=13, alignment=0,
    )
    encabezado_hoja = ParagraphStyle(
        "EncHoja", parent=styles["value"], fontSize=10, leading=18,
    )

    return [
        PageBreak(),
        Paragraph("Hoja de trabajo", styles["section"]),
        Paragraph(_esc(ps.session_title or ""), styles["body"]),
        Spacer(1, 0.2 * cm),
        Paragraph("Nombre: ______________________________  "
                  "Fecha: ____ / ____ / ______", encabezado_hoja),
        HRFlowable(width="100%", thickness=1, color=colors.HexColor("#D1D5DB"),
                   spaceBefore=6, spaceAfter=10),
        Preformatted(_envolver_mono(ps.student_worksheet), mono),
    ]


def _pie(ps, styles):
    generado = datetime.utcnow().strftime("%d/%m/%Y %H:%M")
    return [
        Spacer(1, 0.5 * cm),
        HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#E5E7EB"), spaceAfter=8),
        Paragraph(
            "<b>Aviso:</b> material orientativo generado con asistencia de IA. "
            "No constituye diagnóstico clínico. Adaptalo a tu criterio docente "
            "y al momento del alumno.",
            styles["disclaimer"],
        ),
        Spacer(1, 0.35 * cm),
        Paragraph(
            f"{_esc(SCHOOL_NAME)} · {_esc(SCHOOL_CITY)}<br/>"
            f"Generado el {generado} · Asistido por Claude · Anthropic",
            styles["small"],
        ),
    ]


def _numerar_paginas(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(C_GRAY)
    canvas.drawRightString(19 * cm, 1.2 * cm, f"Página {canvas.getPageNumber()}")
    canvas.restoreState()


def generate_session_plan_pdf(ps, student, area_label=None) -> bytes:
    """Genera el PDF del plan de sesión y devuelve los bytes."""
    buffer = io.BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2 * cm, leftMargin=2 * cm,
        topMargin=1.5 * cm, bottomMargin=2 * cm,
        title=f"Plan de sesión — {student.get_display_name()}",
        author=SCHOOL_NAME,
    )

    styles = _build_styles()
    rec = ps.ai_recommendation or {}

    elementos = []
    elementos += _encabezado(ps, student, area_label or ps.session_area or "", styles)
    elementos += _ficha(ps, student, styles)
    elementos += _lista("Objetivos", rec.get("objectives"), styles)
    elementos += _lista("Materiales", rec.get("materials"), styles)
    elementos += _guia(ps, styles)
    elementos += _rubrica(ps, styles)
    elementos += _pie(ps, styles)
    elementos += _hoja_alumno(ps, student, styles)

    doc.build(elementos, onFirstPage=_numerar_paginas, onLaterPages=_numerar_paginas)
    buffer.seek(0)
    return buffer.getvalue()
