"""
app/reports/pdf_generator.py — Generador de PDFs con ReportLab
Uso: pdf_bytes = generate_report_pdf(report, student)
"""
import io
import json
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    HRFlowable, PageBreak, Paragraph, SimpleDocTemplate,
    Spacer, Table, TableStyle,
)

# ── Paleta ──────────────────────────────────────────────────────────────────
C_INDIGO  = colors.HexColor("#4F46E5")
C_INDIGO2 = colors.HexColor("#312E81")
C_AMBER   = colors.HexColor("#F59E0B")
C_GRAY    = colors.HexColor("#6B7280")
C_LIGHT   = colors.HexColor("#F3F4F6")
C_WHITE   = colors.white
C_BLACK   = colors.HexColor("#1F2937")

SCHOOL_NAME = "Unidad Educativa San Martín de Porres"
SCHOOL_CITY = "Cochabamba, Bolivia"

DISCLAIMER = (
    "AVISO IMPORTANTE: Este reporte es orientativo y NO reemplaza una evaluación clínica "
    "profesional. Los resultados mostrados son generados por un sistema de apoyo educativo "
    "y no constituyen un diagnóstico médico. Para un diagnóstico formal de TDAH, consulte "
    "con un neuropediatra o psicólogo certificado."
)

TDAH_LABELS = {
    "typical":     "Típico (Sin TDAH aparente)",
    "inatento":    "TDAH — Predominantemente Inatento",
    "hiperactivo": "TDAH — Predominantemente Hiperactivo-Impulsivo",
    "combinado":   "TDAH — Tipo Combinado",
    "sin_determinar": "Sin determinar (tests insuficientes)",
}


def _build_styles():
    base = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "TitleStyle", parent=base["Title"],
        fontSize=18, textColor=C_WHITE, alignment=TA_CENTER,
        spaceAfter=4, fontName="Helvetica-Bold",
    )
    subtitle_style = ParagraphStyle(
        "SubtitleStyle", parent=base["Normal"],
        fontSize=10, textColor=colors.HexColor("#C7D2FE"),
        alignment=TA_CENTER, spaceAfter=2,
    )
    section_header = ParagraphStyle(
        "SectionHeader", parent=base["Heading2"],
        fontSize=12, textColor=C_INDIGO,
        spaceBefore=14, spaceAfter=6,
        fontName="Helvetica-Bold",
        borderPad=0,
    )
    body = ParagraphStyle(
        "Body", parent=base["Normal"],
        fontSize=10, textColor=C_BLACK,
        leading=16, spaceAfter=4, alignment=TA_JUSTIFY,
    )
    small_gray = ParagraphStyle(
        "SmallGray", parent=base["Normal"],
        fontSize=8, textColor=C_GRAY, leading=12,
    )
    disclaimer_style = ParagraphStyle(
        "Disclaimer", parent=base["Normal"],
        fontSize=8, textColor=colors.HexColor("#92400E"),
        leading=12, alignment=TA_JUSTIFY,
        backColor=colors.HexColor("#FEF3C7"),
        borderColor=colors.HexColor("#F59E0B"),
        borderWidth=1, borderPad=8,
    )
    label_style = ParagraphStyle(
        "Label", parent=base["Normal"],
        fontSize=9, textColor=C_GRAY, fontName="Helvetica-Bold",
    )
    value_style = ParagraphStyle(
        "Value", parent=base["Normal"],
        fontSize=10, textColor=C_BLACK,
    )
    bullet_style = ParagraphStyle(
        "Bullet", parent=base["Normal"],
        fontSize=10, textColor=C_BLACK,
        leading=15, leftIndent=12, spaceAfter=3,
        bulletIndent=0,
    )
    return {
        "title": title_style,
        "subtitle": subtitle_style,
        "section": section_header,
        "body": body,
        "small": small_gray,
        "disclaimer": disclaimer_style,
        "label": label_style,
        "value": value_style,
        "bullet": bullet_style,
    }


def _header_table(report, student, styles) -> list:
    """Bloque de encabezado con fondo indigo + datos del colegio."""
    header_data = [
        [
            Paragraph(SCHOOL_NAME, styles["title"]),
        ],
        [
            Paragraph(f"{SCHOOL_CITY} · Tel: +591 4 4XXXXXX", styles["subtitle"]),
        ],
    ]
    header_table = Table(
        [[Paragraph(SCHOOL_NAME, styles["title"])],
         [Paragraph(f"{SCHOOL_CITY}", styles["subtitle"])]],
        colWidths=[17 * cm],
    )
    header_table.setStyle(TableStyle([
        ("BACKGROUND",  (0, 0), (-1, -1), C_INDIGO2),
        ("TOPPADDING",  (0, 0), (-1, -1), 16),
        ("BOTTOMPADDING", (0, -1), (-1, -1), 16),
        ("LEFTPADDING",  (0, 0), (-1, -1), 20),
        ("RIGHTPADDING", (0, 0), (-1, -1), 20),
        ("ROUNDEDCORNERS", [6]),
    ]))

    report_type_label = {
        "manual_teacher": "Reporte del Docente",
        "vision_test": "Resultado: Test de Visión",
        "audio_test": "Resultado: Test de Audio",
        "stroop_test": "Resultado: Test de Colores (Stroop)",
        "gonogo_test": "Resultado: Test de Reacción (Go/No-Go)",
    }.get(report.report_type, "Reporte Escolar")

    return [
        header_table,
        Spacer(1, 0.3 * cm),
        Paragraph(f"<b>{report_type_label}</b>", ParagraphStyle(
            "RepType", fontName="Helvetica-Bold", fontSize=14,
            textColor=C_INDIGO, alignment=TA_CENTER,
        )),
        Spacer(1, 0.2 * cm),
    ]


def _student_info_table(student, report, styles) -> list:
    """Tabla 2×N con datos del alumno."""
    fecha_str = report.created_at.strftime("%d/%m/%Y") if report.created_at else "—"

    rows = [
        ["Nombre completo", student.get_display_name(), "Fecha del reporte", fecha_str],
        ["Edad", f"{student.age} años" if student.age else "—",
         "Grado / Sección", f"{student.grade or '—'} — {student.section or '—'}"],
        ["C.I.", student.national_id or "—",
         "Tipo TDAH detectado", TDAH_LABELS.get(student.tdah_type or "", "No evaluado")],
        ["Tutor/a", student.tutor_full_name or "—",
         "Teléfono tutor", student.tutor_phone or "—"],
    ]

    table_data = []
    for label1, val1, label2, val2 in rows:
        table_data.append([
            Paragraph(label1, styles["label"]),
            Paragraph(str(val1), styles["value"]),
            Paragraph(label2, styles["label"]),
            Paragraph(str(val2), styles["value"]),
        ])

    t = Table(table_data, colWidths=[3.5 * cm, 5.5 * cm, 4 * cm, 4 * cm])
    t.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), C_WHITE),
        ("BACKGROUND",    (0, 0), (0, -1), C_LIGHT),
        ("BACKGROUND",    (2, 0), (2, -1), C_LIGHT),
        ("GRID",          (0, 0), (-1, -1), 0.5, colors.HexColor("#E5E7EB")),
        ("TOPPADDING",    (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING",   (0, 0), (-1, -1), 8),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 8),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [C_WHITE, colors.HexColor("#FAFAF9")]),
    ]))
    return [
        Paragraph("Información del Alumno", styles["section"]),
        HRFlowable(width="100%", thickness=1, color=C_INDIGO, spaceAfter=6),
        t,
        Spacer(1, 0.3 * cm),
    ]


def _confidence_bar(confidence: float, tdah_type: str, styles) -> list:
    """Barra de confianza visual del algoritmo TDAH."""
    if not confidence:
        return []

    bar_width = 14 * cm
    fill = min(confidence / 100, 1.0)
    bar_color = C_AMBER if fill < 0.65 else C_INDIGO

    bar_data = [["", ""]]
    bar_t = Table(bar_data, colWidths=[bar_width * fill, bar_width * (1 - fill)], rowHeights=[0.5 * cm])
    bar_t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, 0), bar_color),
        ("BACKGROUND", (1, 0), (1, 0), C_LIGHT),
        ("TOPPADDING",    (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
        ("LEFTPADDING",   (0, 0), (-1, -1), 0),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 0),
    ]))

    label = TDAH_LABELS.get(tdah_type, tdah_type or "—")
    return [
        Paragraph("Clasificación TDAH (Algoritmo de Consenso)", styles["section"]),
        HRFlowable(width="100%", thickness=1, color=C_INDIGO, spaceAfter=6),
        Paragraph(f"<b>Resultado:</b> {label}", styles["body"]),
        Paragraph(f"<b>Confianza del algoritmo:</b> {confidence:.1f}%", styles["body"]),
        Spacer(1, 0.2 * cm),
        bar_t,
        Paragraph(
            "La confianza refleja la consistencia entre múltiples tests. "
            "Valores ≥ 70% indican resultados estables.",
            styles["small"],
        ),
        Spacer(1, 0.3 * cm),
    ]


def _test_metrics_table(content_json: str, report_type: str, styles) -> list:
    """Tabla de métricas del test cognitivo."""
    try:
        data = json.loads(content_json or "{}")
    except Exception:
        return []

    if not data:
        return []

    metric_labels = {
        "vision_test": [
            ("attention_score_center", "Atención central", "%"),
            ("gaze_stability_index", "Estabilidad de mirada", ""),
            ("distraction_events", "Eventos de distracción", ""),
            ("fixation_duration_avg_ms", "Duración fijación promedio", "ms"),
        ],
        "stroop_test": [
            ("tiempo_reaccion_promedio_ms", "Tiempo reacción promedio", "ms"),
            ("errores", "Errores totales", ""),
            ("interferencia_score", "Score de interferencia", "%"),
            ("inhibicion_cognitiva", "Inhibición cognitiva", "%"),
        ],
        "gonogo_test": [
            ("false_positives", "Falsos positivos (impulsos)", ""),
            ("misses", "Omisiones (Go no presionado)", ""),
            ("inhibicion_rate", "Tasa de inhibición", ""),
            ("impulsividad_score", "Score de impulsividad", "%"),
        ],
        "audio_test": [
            ("comprension_score", "Comprensión auditiva", "%"),
            ("pausas_detectadas", "Pausas detectadas", ""),
            ("tiempo_respuesta_promedio_s", "Tiempo respuesta promedio", "s"),
            ("precision_transcripcion", "Precisión transcripción", ""),
        ],
    }

    fields = metric_labels.get(report_type, [])
    if not fields:
        return []

    rows = []
    for key, label, unit in fields:
        val = data.get(key)
        if val is not None:
            display = f"{val}{unit}" if unit else str(val)
            rows.append([
                Paragraph(label, styles["label"]),
                Paragraph(display, styles["value"]),
            ])

    if not rows:
        return []

    t = Table(rows, colWidths=[9 * cm, 8 * cm])
    t.setStyle(TableStyle([
        ("GRID",          (0, 0), (-1, -1), 0.5, colors.HexColor("#E5E7EB")),
        ("BACKGROUND",    (0, 0), (0, -1), C_LIGHT),
        ("TOPPADDING",    (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING",   (0, 0), (-1, -1), 8),
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [C_WHITE, colors.HexColor("#FAFAF9")]),
    ]))

    label_map = {
        "vision_test": "Métricas: Test de Visión",
        "stroop_test": "Métricas: Test de Colores (Stroop)",
        "gonogo_test": "Métricas: Test de Reacción (Go/No-Go)",
        "audio_test":  "Métricas: Test de Audio",
    }
    return [
        Paragraph(label_map.get(report_type, "Métricas del Test"), styles["section"]),
        HRFlowable(width="100%", thickness=1, color=C_INDIGO, spaceAfter=6),
        t,
        Spacer(1, 0.3 * cm),
    ]


def _narrative_section(content: str, recommendations: str, parent_comments: str, styles) -> list:
    """Sección narrativa del reporte docente."""
    elements = []

    if content:
        elements += [
            Paragraph("Observaciones del Docente", styles["section"]),
            HRFlowable(width="100%", thickness=1, color=C_INDIGO, spaceAfter=6),
            Paragraph(content, styles["body"]),
            Spacer(1, 0.3 * cm),
        ]

    if recommendations:
        elements += [
            Paragraph("Recomendaciones", styles["section"]),
            HRFlowable(width="100%", thickness=1, color=C_INDIGO, spaceAfter=6),
        ]
        for line in recommendations.strip().split("\n"):
            line = line.strip().lstrip("-•").strip()
            if line:
                elements.append(Paragraph(f"• {line}", styles["bullet"]))
        elements.append(Spacer(1, 0.3 * cm))

    if parent_comments:
        elements += [
            Paragraph("Comentarios del Tutor", styles["section"]),
            HRFlowable(width="100%", thickness=1, color=C_INDIGO, spaceAfter=6),
            Paragraph(parent_comments, styles["body"]),
            Spacer(1, 0.3 * cm),
        ]

    return elements


def _footer_section(report, teacher_name: str, styles) -> list:
    """Firma + disclaimer."""
    fecha = report.created_at.strftime("%d de %B de %Y") if report.created_at else "—"
    return [
        Spacer(1, 0.5 * cm),
        HRFlowable(width="100%", thickness=0.5, color=C_GRAY),
        Spacer(1, 0.3 * cm),
        Table(
            [[
                Paragraph(f"Emitido por: <b>{teacher_name}</b><br/>Fecha: {fecha}", styles["small"]),
                Paragraph(f"{SCHOOL_NAME}<br/>Sistema de Evaluación TDAH", ParagraphStyle(
                    "FooterRight", parent=styles["small"], alignment=TA_RIGHT,
                )),
            ]],
            colWidths=[9 * cm, 8 * cm],
        ),
        Spacer(1, 0.4 * cm),
        Paragraph(DISCLAIMER, styles["disclaimer"]),
    ]


def generate_report_pdf(report, student) -> bytes:
    """
    Genera el PDF del reporte y retorna los bytes para enviar como archivo.
    """
    buffer = io.BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=1.5 * cm,
        bottomMargin=2 * cm,
        title=f"Reporte — {student.get_display_name()}",
        author=SCHOOL_NAME,
    )

    styles = _build_styles()
    elements = []

    # Header
    elements += _header_table(report, student, styles)
    elements.append(Spacer(1, 0.4 * cm))

    # Info alumno
    elements += _student_info_table(student, report, styles)

    # Barra de confianza TDAH
    elements += _confidence_bar(student.tdah_confidence or 0, student.tdah_type or "", styles)

    # Métricas del test (si es test cognitivo)
    if report.report_type in ("vision_test", "stroop_test", "gonogo_test", "audio_test"):
        elements += _test_metrics_table(report.content or "", report.report_type, styles)

    # Narrativa (si es reporte del docente)
    if report.report_type == "manual_teacher":
        elements += _narrative_section(
            report.content or "",
            report.recommendations or "",
            report.parent_comments or "",
            styles,
        )

    # Footer + disclaimer
    from app.core.models.user import User
    teacher = User.query.get(report.teacher_id) if report.teacher_id else None
    teacher_name = teacher.username if teacher else "Sistema"
    elements += _footer_section(report, teacher_name, styles)

    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()
