import json

from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from app.models.user import User
from app.models.student import Student
from app.models.activity import Activity, Session
from app.models.report import Report
from app.core.models.pedagogical import PedagogicalSession, SessionResult
from app.reports.ai_generator import AIActivityGenerator
from app.reports.ai_service import AIService
from app.extensions import db
from functools import wraps
from datetime import datetime, timedelta

teacher_bp = Blueprint('teacher', __name__, url_prefix='/teacher')

def teacher_required(f):
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if current_user.role != 'teacher':
            flash('Acceso denegado. Se requiere rol de profesor.', 'danger')
            return redirect(url_for('auth.dashboard'))
        return f(*args, **kwargs)
    return decorated_function

@teacher_bp.route('/')
@teacher_required
def index():
    """Dashboard del profesor con búsqueda y filtros en el grid de alumnos."""
    from app.shared.helpers import filter_students_query, get_student_filter_options

    # ── Parámetros de filtro ──────────────────────────────────────────────
    q               = request.args.get('q', '').strip()
    tdah_filter     = request.args.get('tdah_type', '')
    grade_filter    = request.args.get('grade', '')
    activity_status = request.args.get('activity_status', '')
    sort            = request.args.get('sort', '')

    # ── Alumnos filtrados ─────────────────────────────────────────────────
    students = filter_students_query(
        teacher_id_filter=current_user.id,
        q=q or None,
        tdah_type=tdah_filter or None,
        grade=grade_filter or None,
        activity_status=activity_status or None,
        sort=sort or None,
    ).all()

    # ── Opciones de dropdowns ─────────────────────────────────────────────
    grades, _, _ = get_student_filter_options(teacher_id=current_user.id)
    grade_options = [(g, g) for g in grades]

    filter_ctx = dict(
        students=students,
        q=q,
        tdah_filter=tdah_filter,
        grade_filter=grade_filter,
        activity_status=activity_status,
        sort=sort,
        grade_options=grade_options,
    )

    # HTMX partial → devuelve solo el grid
    if request.headers.get('HX-Request'):
        return render_template('teacher/_students_grid.html', **filter_ctx)

    # ── Datos del dashboard (no afectados por filtros) ────────────────────
    all_student_ids = [
        s.id for s in Student.query.filter_by(teacher_id=current_user.id).all()
    ]
    recent_activities = Activity.query.filter_by(
        teacher_id=current_user.id
    ).order_by(Activity.created_at.desc()).limit(5).all()

    recent_sessions = Session.query.filter(
        Session.student_id.in_(all_student_ids)
    ).order_by(Session.created_at.desc()).limit(5).all() if all_student_ids else []

    stats = {
        'total_students': Student.query.filter_by(teacher_id=current_user.id).count(),
        'total_activities': Activity.query.filter_by(teacher_id=current_user.id).count(),
        'pending_reports': Report.query.filter_by(
            teacher_id=current_user.id, sent_to_parents=False
        ).count(),
        'sessions_today': Session.query.filter(
            Session.student_id.in_(all_student_ids),
            Session.created_at >= datetime.utcnow().date()
        ).count() if all_student_ids else 0,
    }

    return render_template('teacher/index.html',
                           recent_activities=recent_activities,
                           recent_sessions=recent_sessions,
                           stats=stats,
                           **filter_ctx)

@teacher_bp.route('/students')
@teacher_required
def students():
    """Lista de estudiantes asignados"""
    my_students = Student.query.filter_by(teacher_id=current_user.id).all()
    
    # Agregar estadísticas por estudiante
    student_data = []
    for student in my_students:
        sessions_count = Session.query.filter_by(student_id=student.id).count()
        
        avg_attention = db.session.query(
            db.func.avg(Session.attention_score)
        ).filter_by(student_id=student.id).scalar() or 0
        
        last_session = Session.query.filter_by(
            student_id=student.id
        ).order_by(Session.created_at.desc()).first()
        
        student_data.append({
            'student': student,
            'sessions_count': sessions_count,
            'avg_attention': round(avg_attention, 2),
            'last_session': last_session
        })
    
    return render_template('teacher/students.html', student_data=student_data)

@teacher_bp.route('/students/<int:student_id>')
@teacher_required
def student_detail(student_id):
    """Detalle de un estudiante específico"""
    student = Student.query.get_or_404(student_id)
    
    # Verificar que el estudiante esté asignado a este profesor
    if student.teacher_id != current_user.id:
        flash('No tienes acceso a este estudiante', 'danger')
        return redirect(url_for('teacher.students'))
    
    # Sesiones del estudiante
    sessions = Session.query.filter_by(
        student_id=student_id
    ).order_by(Session.created_at.desc()).all()
    
    # Actividades asignadas
    activities = Activity.query.filter_by(
        student_id=student_id
    ).order_by(Activity.created_at.desc()).all()
    
    # Reportes
    reports = Report.query.filter_by(
        student_id=student_id
    ).order_by(Report.created_at.desc()).all()
    
    # Estadísticas
    avg_attention = float(db.session.query(
        db.func.avg(Session.attention_score)
    ).filter_by(student_id=student_id).scalar() or 0)
    
    avg_completion_time = db.session.query(
        db.func.avg(Session.completion_time)
    ).filter_by(student_id=student_id).scalar() or 0
    
    stats = {
        'total_sessions': len(sessions),
        'total_activities': len(activities),
        'avg_attention': round(avg_attention, 2),
        'avg_completion_time': round(avg_completion_time / 60, 2)  # en minutos
    }
    
    return render_template('teacher/student_detail.html',
                         student=student,
                         sessions=sessions,
                         activities=activities,
                         reports=reports,
                         stats=stats)

# Tipos de Report que corresponden a tests cognitivos y a actividades AR.
# Los tests guardan su resultado como Report (ver app/assessments/*/routes.py)
# y AR hace lo mismo con prefijo ar_ (ver app/ar/routes.py).
TEST_REPORT_TYPES = ['vision_test', 'audio_test', 'stroop_test', 'gonogo_test']

TEST_TYPE_LABELS = {
    'vision_test': 'Atención visual',
    'audio_test': 'Atención auditiva',
    'stroop_test': 'Stroop',
    'gonogo_test': 'Go/No-Go',
    'ar_caza': 'AR — Caza de objetos',
    'ar_secuencia': 'AR — Secuencia de luces',
    'ar_respiracion': 'AR — Respiración',
    'ar_trail': 'AR — Trail Making',
}


def _pedagogical_status(last_session):
    """Estado visual del alumno según su última sesión pedagógica."""
    if not last_session:
        return ('new', 'Nuevo', 'blue')

    if last_session.status == 'evaluated':
        ref = last_session.completed_at or last_session.created_at
        days = (datetime.utcnow() - ref).days if ref else 0
        if days > 7:
            return ('overdue', f'Hace {days} días', 'orange')
        return ('up_to_date', 'Al día', 'green')

    return ('in_progress', 'En progreso', 'yellow')


@teacher_bp.route('/activities')
@teacher_required
def activities():
    """Lista de alumnos del maestro con su resumen pedagógico."""
    students = Student.query.filter_by(
        teacher_id=current_user.id
    ).order_by(Student.full_name).all()

    students_data = []
    for student in students:
        last_session = PedagogicalSession.query.filter_by(
            student_id=student.id
        ).order_by(PedagogicalSession.created_at.desc()).first()

        status, status_label, status_color = _pedagogical_status(last_session)

        students_data.append({
            'student': student,
            'tdah_profile': student.get_tipo_tdah_display(),
            'confidence': round(student.tdah_confidence or 0),
            'last_session': last_session,
            'status': status,
            'status_label': status_label,
            'status_color': status_color,
        })

    stats = {
        'total': len(students_data),
        'up_to_date': sum(1 for d in students_data if d['status'] == 'up_to_date'),
        'overdue': sum(1 for d in students_data if d['status'] == 'overdue'),
        'new': sum(1 for d in students_data if d['status'] == 'new'),
        'in_progress': sum(1 for d in students_data if d['status'] == 'in_progress'),
    }

    return render_template('teacher/students_pedagogical.html',
                           students_data=students_data, stats=stats,
                           area_labels=AIService.AREAS_PEDAGOGICAS)


def _estado_historial(ps, resultado):
    """Estado visual de una sesión en el historial que ve el docente.

    Devuelve (clave, etiqueta, color). El color lo consume historial.css.

    No usa PedagogicalSession.due_state() porque acá el color de una sesión
    completada lo decide el PUNTAJE, no el vencimiento. Sí reutiliza
    is_expired/days_remaining para no repetir la aritmética de fechas.
    Al docente lo vencido le sale en rojo (es algo para accionar); al alumno
    en gris, para no ser punitivo.
    """
    if ps.is_completed:
        if resultado and resultado.ai_score is not None:
            if resultado.ai_score >= 70:
                return ('completada', 'Completada', 'verde')
            if resultado.ai_score >= 50:
                return ('completada', 'Completada', 'naranja')
            return ('completada', 'Completada', 'rojo-suave')
        return ('completada', 'Completada', 'gris')

    if ps.is_expired:
        dias = abs(ps.days_remaining)
        etiqueta = 'Vencida ayer' if dias == 1 else f'Vencida hace {dias} días'
        return ('vencida', etiqueta, 'rojo')

    if ps.status == 'in_progress':
        return ('activa', 'En curso', 'gris')

    dias = ps.days_remaining
    if dias == 0:
        return ('activa', 'Vence HOY', 'rojo')
    if dias is not None and dias <= 3:
        return ('activa', f'Vence en {dias} día' + ('s' if dias != 1 else ''), 'naranja')

    return ('activa', 'Activa', 'gris')


def _build_historial(student):
    """Historial de sesiones pedagógicas + métricas para el perfil docente."""
    sesiones = PedagogicalSession.query.filter_by(
        student_id=student.id
    ).filter(
        PedagogicalSession.status != 'draft'
    ).order_by(
        # MariaDB no soporta NULLS LAST
        PedagogicalSession.scheduled_for.is_(None),
        PedagogicalSession.scheduled_for.desc(),
        PedagogicalSession.created_at.desc(),
    ).all()

    filas = []
    for ps in sesiones:
        resultado = ps.results.order_by(SessionResult.submitted_at.desc()).first()
        estado, etiqueta, color = _estado_historial(ps, resultado)
        filas.append({
            'sesion': ps,
            'resultado': resultado,
            'estado': estado,
            'etiqueta': etiqueta,
            'color': color,
            'area_label': AIService.AREAS_PEDAGOGICAS.get(
                ps.session_area, ps.session_area or 'General'),
        })

    return filas, _build_metricas(filas)


def _build_metricas(filas):
    """Porcentaje completado, tendencia de los últimos 3 y área más trabajada."""
    total = len(filas)
    completadas = sum(1 for f in filas if f['estado'] == 'completada')
    vencidas = sum(1 for f in filas if f['estado'] == 'vencida')
    activas = sum(1 for f in filas if f['estado'] == 'activa')

    # Puntajes en orden cronológico (filas viene de más nueva a más vieja)
    puntajes = [
        f['resultado'].ai_score for f in reversed(filas)
        if f['resultado'] and f['resultado'].ai_score is not None
    ]

    ultimos = puntajes[-3:]
    if len(ultimos) < 2:
        tendencia, tendencia_label, delta = 'sin_datos', 'Faltan sesiones evaluadas', None
    else:
        delta = round(ultimos[-1] - ultimos[0])
        if delta >= 5:
            tendencia, tendencia_label = 'mejora', 'Mejorando'
        elif delta <= -5:
            tendencia, tendencia_label = 'baja', 'Bajando'
        else:
            tendencia, tendencia_label = 'estable', 'Estable'

    areas = {}
    for f in filas:
        if f['sesion'].session_area:
            areas[f['area_label']] = areas.get(f['area_label'], 0) + 1
    area_top, area_top_n = (max(areas.items(), key=lambda kv: kv[1]) if areas else (None, 0))

    return {
        'total': total,
        'completadas': completadas,
        'vencidas': vencidas,
        'activas': activas,
        'pct_completadas': round(completadas * 100 / total) if total else 0,
        'promedio': round(sum(puntajes) / len(puntajes)) if puntajes else None,
        'puntajes': [round(p) for p in puntajes],
        'ultimos': [round(p) for p in ultimos],
        'tendencia': tendencia,
        'tendencia_label': tendencia_label,
        'delta': delta,
        'area_top': area_top,
        'area_top_n': area_top_n,
    }


def _resumen_report(report):
    """Comprime un Report de test/AR a lo que la IA necesita ver."""
    resumen = {
        'tipo': TEST_TYPE_LABELS.get(report.report_type, report.report_type),
        'fecha': report.created_at.strftime('%Y-%m-%d') if report.created_at else None,
    }

    try:
        contenido = json.loads(report.content) if report.content else {}
    except (TypeError, ValueError):
        contenido = {}

    if isinstance(contenido, dict):
        if contenido.get('tipo_tdah'):
            resumen['tipo_tdah'] = contenido['tipo_tdah']
        if contenido.get('confianza') is not None:
            resumen['confianza'] = contenido['confianza']
        # Métricas numéricas sueltas (aciertos, tiempo de reacción, etc.)
        metricas = {
            k: v for k, v in (contenido.get('metricas') or contenido).items()
            if isinstance(v, (int, float))
        }
        if metricas:
            resumen['metricas'] = dict(list(metricas.items())[:8])

    return resumen


def _build_pedagogical_context(student):
    """Arma el contexto que se le pasa a la IA para recomendar una sesión."""
    tests = Report.query.filter(
        Report.student_id == student.id,
        Report.report_type.in_(TEST_REPORT_TYPES),
    ).order_by(Report.created_at.desc()).limit(5).all()

    ar = Report.query.filter(
        Report.student_id == student.id,
        Report.report_type.like('ar_%'),
    ).order_by(Report.created_at.desc()).limit(5).all()

    previas = PedagogicalSession.query.filter_by(
        student_id=student.id
    ).order_by(PedagogicalSession.created_at.desc()).limit(5).all()

    sesiones_previas = []
    for ps in previas:
        item = {
            'area': ps.session_area,
            'nivel': ps.session_level,
            'estado': ps.status,
            'fecha': ps.created_at.strftime('%Y-%m-%d') if ps.created_at else None,
        }
        resultado = ps.results.order_by(SessionResult.submitted_at.desc()).first()
        if resultado:
            item['puntaje_ia'] = resultado.ai_score
            item['calificacion'] = resultado.ai_qualitative_grade
            if resultado.teacher_notes:
                item['notas_docente'] = resultado.teacher_notes[:300]
        sesiones_previas.append(item)

    return {
        'nombre': student.get_display_name(),
        'edad': student.age,
        'curso': student.grade,
        'perfil_tdah': student.get_tipo_tdah_display(),
        'confianza': round(student.tdah_confidence or 0),
        'tests': [_resumen_report(r) for r in tests],
        'ar': [_resumen_report(r) for r in ar],
        'sesiones_previas': sesiones_previas,
    }


@teacher_bp.route('/students/<int:student_id>/pedagogical/recommend', methods=['POST'])
@teacher_required
def generate_pedagogical_recommendation(student_id):
    """Genera con IA la recomendación de la próxima sesión pedagógica."""
    student = Student.query.get_or_404(student_id)

    if student.teacher_id != current_user.id:
        return jsonify({'success': False, 'error': 'No autorizado'}), 403

    datos = request.get_json(silent=True) or {}
    try:
        dias_para_completar = int(datos.get('days_to_complete')
                                  or PedagogicalSession.DIAS_PARA_COMPLETAR)
    except (TypeError, ValueError):
        dias_para_completar = PedagogicalSession.DIAS_PARA_COMPLETAR
    dias_para_completar = min(30, max(1, dias_para_completar))

    try:
        from app.reports.ai_service import ai_service
        contexto = _build_pedagogical_context(student)
        rec = ai_service.generate_pedagogical_recommendation(contexto)
    except Exception as e:
        current_app.logger.error(f"Error generando recomendación pedagógica: {e}")
        return jsonify({
            'success': False,
            'error': 'No se pudo generar la recomendación. Revisá que ANTHROPIC_API_KEY '
                     'esté configurada e intentá de nuevo.'
        }), 502

    try:
        # Si la última sesión todavía no se ejecutó, la sobreescribimos en vez
        # de acumular borradores cada vez que el docente aprieta el botón.
        sesion = PedagogicalSession.query.filter(
            PedagogicalSession.student_id == student.id,
            PedagogicalSession.status.in_(['draft', 'planned']),
        ).order_by(PedagogicalSession.created_at.desc()).first()

        if sesion is None:
            sesion = PedagogicalSession(student_id=student.id, teacher_id=current_user.id)
            db.session.add(sesion)

        sesion.ai_recommendation = rec
        sesion.recommendation_generated_at = datetime.utcnow()
        sesion.session_title = rec.get('session_title')
        sesion.session_area = rec.get('area')
        sesion.session_level = rec.get('level')
        sesion.status = 'planned'

        # Fecha límite por defecto: sin plazo no hay urgencia y la sesión
        # queda flotando. Si el docente ya eligió una fecha a mano, no se pisa.
        if sesion.scheduled_for is None:
            sesion.scheduled_for = datetime.utcnow() + timedelta(days=dias_para_completar)

        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error guardando recomendación: {e}")
        return jsonify({'success': False, 'error': f'Error al guardar: {e}'}), 500

    return jsonify({
        'success': True,
        'session_id': sesion.id,
        'recommendation': rec,
    })


def _get_own_session(session_id):
    """Devuelve la PedagogicalSession si es del docente logueado, o None."""
    ps = PedagogicalSession.query.get_or_404(session_id)
    return ps if ps.teacher_id == current_user.id else None


@teacher_bp.route('/pedagogical/<int:session_id>/plan', methods=['POST'])
@teacher_required
def generate_pedagogical_plan(session_id):
    """Convierte la recomendación en guía docente + hoja del alumno + rúbrica."""
    ps = _get_own_session(session_id)
    if ps is None:
        return jsonify({'success': False, 'error': 'No autorizado'}), 403

    if not ps.ai_recommendation:
        return jsonify({
            'success': False,
            'error': 'Esta sesión todavía no tiene recomendación. Generala primero.'
        }), 400

    try:
        from app.reports.ai_service import ai_service
        contexto = _build_pedagogical_context(ps.student)
        plan = ai_service.generate_session_plan(contexto, ps.ai_recommendation)
    except Exception as e:
        current_app.logger.error(f"Error generando plan de sesión {session_id}: {e}")
        return jsonify({
            'success': False,
            'error': 'No se pudo generar el plan. Revisá ANTHROPIC_API_KEY e intentá de nuevo.'
        }), 502

    try:
        ps.teacher_guide = plan.get('teacher_guide')
        ps.student_worksheet = plan.get('student_worksheet')
        ps.rubric = plan.get('rubric')
        if ps.status == 'draft':
            ps.status = 'planned'
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error guardando plan: {e}")
        return jsonify({'success': False, 'error': f'Error al guardar: {e}'}), 500

    return jsonify({
        'success': True,
        'redirect': url_for('teacher.pedagogical_session_detail', session_id=ps.id),
    })


@teacher_bp.route('/pedagogical/<int:session_id>')
@teacher_required
def pedagogical_session_detail(session_id):
    """Detalle de la sesión: guía, hoja del alumno, rúbrica y resultado."""
    ps = _get_own_session(session_id)
    if ps is None:
        flash('No autorizado', 'danger')
        return redirect(url_for('teacher.activities'))

    resultado = ps.results.order_by(SessionResult.submitted_at.desc()).first()

    return render_template(
        'teacher/pedagogical_session.html',
        ps=ps,
        student=ps.student,
        resultado=resultado,
        area_labels=AIService.AREAS_PEDAGOGICAS,
    )


@teacher_bp.route('/pedagogical/<int:session_id>/print')
@teacher_required
def pedagogical_session_print(session_id):
    """Versión imprimible: guía del docente + hoja del alumno + rúbrica."""
    ps = _get_own_session(session_id)
    if ps is None:
        flash('No autorizado', 'danger')
        return redirect(url_for('teacher.activities'))

    if not ps.pdf_generated_at:
        ps.pdf_generated_at = datetime.utcnow()
        db.session.commit()

    return render_template(
        'teacher/pedagogical_session_print.html',
        ps=ps,
        student=ps.student,
        area_labels=AIService.AREAS_PEDAGOGICAS,
    )


@teacher_bp.route('/pedagogical/<int:session_id>/export-pdf')
@teacher_required
def export_plan_pdf(session_id):
    """Descarga el plan de sesión como PDF (no la vista de impresión)."""
    ps = _get_own_session(session_id)
    if ps is None:
        flash('No autorizado', 'danger')
        return redirect(url_for('teacher.activities'))

    if not ps.teacher_guide:
        flash('Esta sesión todavía no tiene material. Generalo primero.', 'warning')
        return redirect(url_for('teacher.pedagogical_session_detail', session_id=ps.id))

    try:
        from app.reports.plan_pdf_generator import generate_session_plan_pdf
        from flask import send_file
        import io as _io

        pdf_bytes = generate_session_plan_pdf(
            ps, ps.student,
            area_label=AIService.AREAS_PEDAGOGICAS.get(ps.session_area, ps.session_area),
        )

        if not ps.pdf_generated_at:
            ps.pdf_generated_at = datetime.utcnow()
            db.session.commit()

        titulo = (ps.session_title or 'sesion')[:60]
        alumno = ps.student.get_display_name()
        nombre = _slug_archivo(f"Plan_{titulo}_{alumno}") + '.pdf'

        return send_file(
            _io.BytesIO(pdf_bytes),
            mimetype='application/pdf',
            as_attachment=True,
            download_name=nombre,
        )
    except Exception as e:
        db.session.rollback()
        import traceback; traceback.print_exc()
        current_app.logger.error(f"Error generando PDF del plan {session_id}: {e}")
        flash(f'Error al generar el PDF: {e}', 'danger')
        return redirect(url_for('teacher.pedagogical_session_detail', session_id=ps.id))


def _slug_archivo(texto):
    """Nombre de archivo seguro: sin acentos ni caracteres que rompan la
    cabecera Content-Disposition en algunos navegadores."""
    import re
    import unicodedata

    normalizado = unicodedata.normalize('NFKD', str(texto))
    ascii_only = normalizado.encode('ascii', 'ignore').decode('ascii')
    limpio = re.sub(r'[^A-Za-z0-9]+', '_', ascii_only).strip('_')
    return limpio or 'plan_sesion'


@teacher_bp.route('/pedagogical/<int:session_id>/schedule', methods=['POST'])
@teacher_required
def schedule_pedagogical_session(session_id):
    """Agenda la sesión. Sin fecha el alumno la ve como 'Pendiente' y nunca
    puede aparecer como vencida."""
    ps = _get_own_session(session_id)
    if ps is None:
        flash('No autorizado', 'danger')
        return redirect(url_for('teacher.activities'))

    fecha = (request.form.get('scheduled_for') or '').strip()

    if not fecha:
        ps.scheduled_for = None
        db.session.commit()
        flash('Se quitó la fecha de la sesión', 'success')
        return redirect(url_for('teacher.pedagogical_session_detail', session_id=ps.id))

    try:
        ps.scheduled_for = datetime.strptime(fecha, '%Y-%m-%d')
        db.session.commit()
        flash(f'Sesión agendada para el {ps.scheduled_for.strftime("%d/%m/%Y")}', 'success')
    except ValueError:
        db.session.rollback()
        flash('Fecha inválida', 'danger')

    return redirect(url_for('teacher.pedagogical_session_detail', session_id=ps.id))


@teacher_bp.route('/pedagogical/<int:session_id>/result', methods=['POST'])
@teacher_required
def submit_pedagogical_result(session_id):
    """El docente registra cómo salió la sesión y la IA lo analiza."""
    ps = _get_own_session(session_id)
    if ps is None:
        flash('No autorizado', 'danger')
        return redirect(url_for('teacher.activities'))

    notas = (request.form.get('teacher_notes') or '').strip()
    if not notas:
        flash('Escribí cómo salió la sesión antes de guardar', 'warning')
        return redirect(url_for('teacher.pedagogical_session_detail', session_id=ps.id))

    # Las métricas llegan como pares metrica_nombre / metrica_valor
    metricas = {}
    for nombre, valor in zip(request.form.getlist('metrica_nombre'),
                             request.form.getlist('metrica_valor')):
        nombre = (nombre or '').strip()
        valor = (valor or '').strip()
        if not nombre or not valor:
            continue
        try:
            metricas[nombre] = float(valor) if '.' in valor else int(valor)
        except ValueError:
            metricas[nombre] = valor

    try:
        resultado = SessionResult(
            session_id=ps.id,
            teacher_notes=notas,
            objective_metrics=metricas or None,
        )
        db.session.add(resultado)
        ps.status = 'completed'
        ps.completed_at = datetime.utcnow()
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error guardando resultado: {e}")
        flash(f'Error al guardar el resultado: {e}', 'danger')
        return redirect(url_for('teacher.pedagogical_session_detail', session_id=ps.id))

    # El análisis de IA es un extra: si falla, el resultado ya quedó guardado.
    try:
        from app.reports.ai_service import ai_service
        contexto = _build_pedagogical_context(ps.student)
        analisis = ai_service.analyze_session_result(contexto, ps, notas, metricas)

        resultado.ai_analysis = analisis.get('analysis')
        resultado.ai_score = analisis.get('score')
        resultado.ai_qualitative_grade = analisis.get('grade')
        resultado.ai_next_recommendation = analisis.get('next_recommendation')
        resultado.ai_analyzed_at = datetime.utcnow()
        ps.status = 'evaluated'
        db.session.commit()
        flash('Resultado registrado y analizado por la IA', 'success')
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error analizando resultado {resultado.id}: {e}")
        flash('Resultado guardado, pero el análisis de IA falló. '
              'Podés reintentarlo desde la sesión.', 'warning')

    return redirect(url_for('teacher.pedagogical_session_detail', session_id=ps.id))


@teacher_bp.route('/pedagogical/<int:session_id>/reanalyze', methods=['POST'])
@teacher_required
def reanalyze_pedagogical_result(session_id):
    """Reintenta el análisis de IA sobre un resultado ya cargado."""
    ps = _get_own_session(session_id)
    if ps is None:
        return jsonify({'success': False, 'error': 'No autorizado'}), 403

    resultado = ps.results.order_by(SessionResult.submitted_at.desc()).first()
    if resultado is None:
        return jsonify({'success': False, 'error': 'La sesión no tiene resultado cargado'}), 400

    try:
        from app.reports.ai_service import ai_service
        contexto = _build_pedagogical_context(ps.student)
        analisis = ai_service.analyze_session_result(
            contexto, ps, resultado.teacher_notes, resultado.objective_metrics
        )

        resultado.ai_analysis = analisis.get('analysis')
        resultado.ai_score = analisis.get('score')
        resultado.ai_qualitative_grade = analisis.get('grade')
        resultado.ai_next_recommendation = analisis.get('next_recommendation')
        resultado.ai_analyzed_at = datetime.utcnow()
        ps.status = 'evaluated'
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error reanalizando resultado: {e}")
        return jsonify({'success': False, 'error': 'No se pudo analizar. Intentá de nuevo.'}), 502

    return jsonify({'success': True})


@teacher_bp.route('/activities/library')
@teacher_required
def activities_library():
    """Catálogo de actividades creadas (era la vista de /activities)."""
    activities = Activity.query.filter_by(
        teacher_id=current_user.id
    ).order_by(Activity.created_at.desc()).all()

    return render_template('teacher/activities.html', activities=activities)


@teacher_bp.route('/students/<int:student_id>/pedagogical')
@teacher_required
def student_pedagogical_profile(student_id):
    """Perfil pedagógico detallado del alumno."""
    student = Student.query.get_or_404(student_id)

    if student.teacher_id != current_user.id:
        flash('No autorizado', 'danger')
        return redirect(url_for('teacher.activities'))

    recent_tests = Report.query.filter(
        Report.student_id == student.id,
        Report.report_type.in_(TEST_REPORT_TYPES),
    ).order_by(Report.created_at.desc()).limit(5).all()

    recent_ar_sessions = Report.query.filter(
        Report.student_id == student.id,
        Report.report_type.like('ar_%'),
    ).order_by(Report.created_at.desc()).limit(5).all()

    pedagogical_sessions = PedagogicalSession.query.filter_by(
        student_id=student.id
    ).order_by(PedagogicalSession.created_at.desc()).limit(10).all()

    historial, metricas = _build_historial(student)

    # Recomendación vigente: la última sesión planificada que ya tiene
    # análisis de la IA. Es la que se muestra en la card de recomendación.
    active_recommendation = next(
        (ps for ps in pedagogical_sessions
         if ps.ai_recommendation and ps.status in ('draft', 'planned')),
        None
    )

    return render_template(
        'teacher/student_pedagogical_profile.html',
        student=student,
        tdah_profile=student.get_tipo_tdah_display(),
        confidence=round(student.tdah_confidence or 0),
        recent_tests=recent_tests,
        recent_ar_sessions=recent_ar_sessions,
        pedagogical_sessions=pedagogical_sessions,
        active_recommendation=active_recommendation,
        historial=historial,
        metricas=metricas,
        area_labels=AIService.AREAS_PEDAGOGICAS,
        type_labels=TEST_TYPE_LABELS,
    )

@teacher_bp.route('/activities/create', methods=['GET', 'POST'])
@teacher_required
def create_activity():
    """Crear nueva actividad"""
    if request.method == 'GET':
        # Obtener estudiantes del profesor
        students = Student.query.filter_by(teacher_id=current_user.id).all()
        return render_template('teacher/create_activity.html', students=students)
    
    data = request.form
    
    try:
        new_activity = Activity(
            student_id=data.get('student_id'),
            teacher_id=current_user.id,
            title=data.get('title'),
            description=data.get('description'),
            activity_type=data.get('activity_type'),
            difficulty_level=int(data.get('difficulty_level', 1)),
            instructions=data.get('instructions')
        )
        
        # Si hay contenido AR
        if data.get('ar_enabled') == 'on':
            new_activity.ar_content = {
                'enabled': True,
                'type': data.get('ar_type', 'markerless'),
                'description': data.get('ar_description', ''),
                'interaction': data.get('ar_interaction', '')
            }
        
        db.session.add(new_activity)
        db.session.commit()
        
        flash('Actividad creada exitosamente', 'success')
        return redirect(url_for('teacher.activities_library'))
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error al crear actividad: {str(e)}', 'danger')
        return redirect(url_for('teacher.create_activity'))

@teacher_bp.route('/activities/<int:activity_id>/edit', methods=['GET', 'POST'])
@teacher_required
def edit_activity(activity_id):
    """Editar una actividad existente."""
    activity = Activity.query.get_or_404(activity_id)

    if activity.teacher_id != current_user.id:
        flash('No autorizado', 'danger')
        return redirect(url_for('teacher.activities_library'))

    if request.method == 'GET':
        return render_template('teacher/edit_activity.html', activity=activity)

    data = request.form
    try:
        activity.title = data.get('title') or activity.title
        activity.description = data.get('description')
        activity.instructions = data.get('instructions')
        activity.activity_type = data.get('activity_type') or activity.activity_type
        activity.difficulty_level = int(data.get('difficulty_level') or activity.difficulty_level or 1)

        db.session.commit()
        flash('Actividad actualizada exitosamente', 'success')
        return redirect(url_for('teacher.activities_library'))

    except Exception as e:
        db.session.rollback()
        flash(f'Error al actualizar actividad: {str(e)}', 'danger')
        return redirect(url_for('teacher.edit_activity', activity_id=activity_id))


@teacher_bp.route('/activities/<int:activity_id>/delete', methods=['POST'])
@teacher_required
def delete_activity(activity_id):
    """Elimina una actividad. Las sesiones asociadas quedan huérfanas
    (Session.activity_id es nullable), no se borra historial del alumno."""
    activity = Activity.query.get_or_404(activity_id)

    if activity.teacher_id != current_user.id:
        return jsonify({'success': False, 'error': 'No autorizado'}), 403

    try:
        Session.query.filter_by(activity_id=activity.id).update(
            {'activity_id': None}, synchronize_session=False
        )
        db.session.delete(activity)
        db.session.commit()
        return jsonify({'success': True})

    except Exception as e:
        db.session.rollback()
        import traceback; traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@teacher_bp.route('/activities/generate', methods=['POST'])
@teacher_required
def generate_activity():
    """Generar actividad con IA"""
    data = request.get_json()
    
    try:
        student_id = data.get('student_id')
        student = Student.query.get_or_404(student_id)
        
        # Verificar que sea estudiante del profesor
        if student.teacher_id != current_user.id:
            return jsonify({'error': 'No autorizado'}), 403
        
        # Preparar perfil del estudiante
        student_profile = {
            'tdah_type': student.tdah_type,
            'age': student.age,
            'difficulty_level': data.get('difficulty_level', 1)
        }
        
        # Obtener última sesión para contexto
        last_session = Session.query.filter_by(
            student_id=student_id
        ).order_by(Session.created_at.desc()).first()
        
        session_data = None
        if last_session:
            session_data = {
                'attention_score': last_session.attention_score,
                'completion_time': last_session.completion_time,
                'difficulties': []
            }
        
        # Generar actividad con IA (solo draft — la BD se escribe cuando el
        # profesor confirma con el formulario "Crear Actividad")
        ai_generator = AIActivityGenerator(current_app.config.get('ANTHROPIC_API_KEY'))
        generated_activity = ai_generator.generate_activity(student_profile, session_data)

        return jsonify({
            'success': True,
            'activity': {
                'title':          generated_activity.get('title', ''),
                'description':    generated_activity.get('description', ''),
                'activity_type':  generated_activity.get('activity_type', 'mixta'),
                'difficulty_level': int(generated_activity.get('difficulty_level', 1)),
                'instructions':   generated_activity.get('instructions', ''),
                'ar_content':     generated_activity.get('ar_content', {'enabled': False}),
            },
            'message': 'Actividad generada con IA exitosamente'
        })
        
    except Exception as e:
        db.session.rollback()
        import traceback; traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

REPORTE_DESACTUALIZADO_DIAS = 30


def _estado_reportes(ultimo, sin_enviar):
    """Estado visual del alumno en la lista de reportes."""
    if ultimo is None:
        return ('sin_reportes', 'Sin reportes', 'blue')

    dias = (datetime.utcnow() - ultimo.created_at).days if ultimo.created_at else 0
    if dias > REPORTE_DESACTUALIZADO_DIAS:
        return ('desactualizado', f'Hace {dias} días', 'orange')

    if sin_enviar:
        return ('pendiente', f'{sin_enviar} sin enviar', 'yellow')

    return ('al_dia', 'Al día', 'green')


@teacher_bp.route('/reports')
@teacher_required
def reports():
    """Lista de alumnos con el resumen de sus reportes.

    El listado global de todos los reportes mezclados quedó en
    /reports/all: acá se entra por alumno, igual que en Actividades.
    """
    students = Student.query.filter_by(
        teacher_id=current_user.id
    ).order_by(Student.full_name).all()

    students_data = []
    for student in students:
        reportes = Report.query.filter_by(
            student_id=student.id
        ).order_by(Report.created_at.desc()).all()

        ultimo = reportes[0] if reportes else None
        sin_enviar = sum(1 for r in reportes if not r.sent_to_parents)
        estado, status_label, status_color = _estado_reportes(ultimo, sin_enviar)

        students_data.append({
            'student': student,
            'tdah_profile': student.get_tipo_tdah_display(),
            'confidence': round(student.tdah_confidence or 0),
            'total': len(reportes),
            'ultimo': ultimo,
            'ultimo_label': REPORT_TYPE_LABELS.get(
                ultimo.report_type, ultimo.report_type) if ultimo else None,
            'sin_enviar': sin_enviar,
            'estado': estado,
            'status_label': status_label,
            'status_color': status_color,
        })

    stats = {
        'total': len(students_data),
        'al_dia': sum(1 for d in students_data if d['estado'] == 'al_dia'),
        'desactualizados': sum(1 for d in students_data if d['estado'] == 'desactualizado'),
        'sin_reportes': sum(1 for d in students_data if d['estado'] == 'sin_reportes'),
        'reportes': sum(d['total'] for d in students_data),
    }

    return render_template('teacher/reports.html',
                           students_data=students_data, stats=stats)


@teacher_bp.route('/reports/all')
@teacher_required
def reports_all():
    """Listado global de todos los reportes (era la vista de /reports)."""
    reports = Report.query.filter_by(
        teacher_id=current_user.id
    ).order_by(Report.created_at.desc()).all()

    return render_template('teacher/reports_all.html', reports=reports)


# Etiquetas legibles para los slugs que guarda Student.tdah_type
TDAH_PERFIL_LABELS = {
    'typical': 'Típico (sin TDAH)',
    'inatento': 'TDAH — Inatento',
    'hiperactivo': 'TDAH — Hiperactivo',
    'combinado': 'TDAH — Combinado',
    'sin_determinar': 'En análisis',
}


REPORT_TYPE_LABELS = {
    'pedagogical_summary': 'Seguimiento pedagógico',
    'manual_teacher': 'Reporte del docente',
    'vision_test': 'Test de atención visual',
    'audio_test': 'Test de atención auditiva',
    'stroop_test': 'Test de Stroop',
    'gonogo_test': 'Test Go/No-Go',
}


def _build_reporte_context(student):
    """Métricas del alumno que alimentan el reporte de seguimiento."""
    sesiones = PedagogicalSession.query.filter_by(
        student_id=student.id
    ).order_by(PedagogicalSession.created_at.asc()).all()

    evaluadas = []
    for ps in sesiones:
        r = ps.results.order_by(SessionResult.submitted_at.desc()).first()
        if r and r.ai_score is not None:
            evaluadas.append((ps, r))

    puntajes = [round(r.ai_score) for _, r in evaluadas]
    promedio = round(sum(puntajes) / len(puntajes)) if puntajes else None

    # Desempeño por área: promedio y cuántas sesiones
    por_area = {}
    for ps, r in evaluadas:
        etiqueta = AIService.AREAS_PEDAGOGICAS.get(ps.session_area, ps.session_area or 'General')
        por_area.setdefault(etiqueta, []).append(round(r.ai_score))
    por_area_lista = [
        {'area': a, 'sesiones': len(v), 'promedio': round(sum(v) / len(v)), 'puntajes': v}
        for a, v in sorted(por_area.items(), key=lambda kv: -len(kv[1]))
    ]

    # Últimas 2 semanas vs. los 30 días previos
    ahora = datetime.utcnow()
    corte_reciente = ahora - timedelta(days=14)
    corte_previo = ahora - timedelta(days=44)

    recientes = [round(r.ai_score) for ps, r in evaluadas
                 if (ps.completed_at or ps.created_at) >= corte_reciente]
    previos = [round(r.ai_score) for ps, r in evaluadas
               if corte_previo <= (ps.completed_at or ps.created_at) < corte_reciente]

    if recientes and previos:
        d = round(sum(recientes) / len(recientes) - sum(previos) / len(previos))
        signo = '+' if d > 0 else ''
        comparacion = (f'{len(recientes)} sesión(es) recientes promedian '
                       f'{round(sum(recientes)/len(recientes))}, contra '
                       f'{round(sum(previos)/len(previos))} del período anterior ({signo}{d})')
    elif recientes:
        comparacion = (f'{len(recientes)} sesión(es) en las últimas 2 semanas; '
                       f'no hay período anterior con el que comparar')
    else:
        comparacion = 'Sin sesiones evaluadas en las últimas 2 semanas'

    if len(puntajes) >= 2:
        delta = puntajes[-1] - puntajes[0]
        tendencia_label = ('Mejorando' if delta >= 5
                           else 'Bajando' if delta <= -5 else 'Estable')
    else:
        tendencia_label = 'Faltan sesiones evaluadas para calcular tendencia'

    tests = Report.query.filter(
        Report.student_id == student.id,
        Report.report_type.in_(TEST_REPORT_TYPES),
    ).order_by(Report.created_at.desc()).limit(5).all()

    ar = Report.query.filter(
        Report.student_id == student.id,
        Report.report_type.like('ar_%'),
    ).order_by(Report.created_at.desc()).limit(5).all()

    return {
        'nombre': student.get_display_name(),
        'edad': student.age,
        'curso': student.grade,
        'perfil_tdah': student.get_tipo_tdah_display(),
        'confianza': round(student.tdah_confidence or 0),
        'sesiones_completadas': len(evaluadas),
        'promedio': promedio,
        'puntajes': puntajes,
        'tendencia_label': tendencia_label,
        'comparacion': comparacion,
        'por_area': por_area_lista,
        'tests': [_resumen_report(r) for r in tests],
        'ar': [_resumen_report(r) for r in ar],
    }


@teacher_bp.route('/student/<int:student_id>/reports')
@teacher_required
def student_reports(student_id):
    """Historial de reportes de UN alumno."""
    student = Student.query.get_or_404(student_id)

    if student.teacher_id != current_user.id:
        flash('No autorizado', 'danger')
        return redirect(url_for('teacher.students'))

    reportes = Report.query.filter_by(
        student_id=student.id
    ).order_by(Report.created_at.desc()).all()

    return render_template(
        'teacher/student_reports.html',
        student=student,
        reportes=reportes,
        tdah_profile=student.get_tipo_tdah_display(),
        confidence=round(student.tdah_confidence or 0),
        type_labels=REPORT_TYPE_LABELS,
    )


@teacher_bp.route('/student/<int:student_id>/generate-report', methods=['POST'])
@teacher_required
def generate_student_report(student_id):
    """Genera con IA un reporte de seguimiento y lo guarda en el historial."""
    student = Student.query.get_or_404(student_id)

    if student.teacher_id != current_user.id:
        return jsonify({'success': False, 'error': 'No autorizado'}), 403

    try:
        from app.reports.ai_service import ai_service
        contexto = _build_reporte_context(student)
        datos = ai_service.generate_student_summary_report(contexto)
    except Exception as e:
        current_app.logger.error(f"Error generando reporte de {student_id}: {e}")
        return jsonify({
            'success': False,
            'error': 'No se pudo generar el reporte. Revisá ANTHROPIC_API_KEY e intentá de nuevo.'
        }), 502

    # content y recommendations son campos de texto: armamos la narrativa con
    # las secciones separadas por títulos, que es como las renderiza la vista.
    contenido = '\n\n'.join(filter(None, [
        datos.get('resumen'),
        f"Fortalezas observadas:\n{datos['fortalezas']}" if datos.get('fortalezas') else '',
        f"Áreas de dificultad:\n{datos['debilidades']}" if datos.get('debilidades') else '',
    ]))

    recomendaciones = '\n\n'.join(filter(None, [
        datos.get('recomendaciones'),
        f"Sugerencias para la familia:\n{datos['familia']}" if datos.get('familia') else '',
    ]))

    try:
        reporte = Report(
            student_id=student.id,
            teacher_id=current_user.id,
            report_type='pedagogical_summary',
            content=contenido,
            recommendations=recomendaciones,
            tipo_tdah=student.tdah_type or 'sin_determinar',
            confianza=student.tdah_confidence or 0,
        )
        db.session.add(reporte)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error guardando reporte: {e}")
        return jsonify({'success': False, 'error': f'Error al guardar: {e}'}), 500

    return jsonify({
        'success': True,
        'report_id': reporte.id,
        'redirect': url_for('teacher.report_detail', report_id=reporte.id),
    })


@teacher_bp.route('/reports/<int:report_id>/delete', methods=['POST'])
@teacher_required
def delete_report(report_id):
    """Elimina un reporte del historial del alumno."""
    reporte = Report.query.get_or_404(report_id)
    student = reporte.student

    if not student or student.teacher_id != current_user.id:
        return jsonify({'success': False, 'error': 'No autorizado'}), 403

    try:
        db.session.delete(reporte)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error eliminando reporte {report_id}: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@teacher_bp.route('/reports/<int:report_id>')
@teacher_required
def report_detail(report_id):
    """Vista de lectura de un reporte, con formato institucional."""
    report = Report.query.get_or_404(report_id)
    student = report.student

    if student.teacher_id != current_user.id:
        flash('No autorizado', 'danger')
        return redirect(url_for('teacher.reports'))

    # El reporte guarda su propio snapshot del perfil, pero create_report
    # todavía no lo completa: si viene vacío usamos el del alumno.
    perfil_slug = report.tipo_tdah
    if not perfil_slug or perfil_slug == 'sin_determinar':
        perfil_slug = student.tdah_type or 'sin_determinar'

    confianza = report.confianza or student.tdah_confidence or 0

    return render_template(
        'teacher/report_detail.html',
        report=report,
        student=student,
        perfil_slug=perfil_slug,
        perfil_label=TDAH_PERFIL_LABELS.get(perfil_slug, 'En análisis'),
        confianza=round(confianza) if confianza else None,
        num_sesiones=student.sessions.count(),
    )


def _build_student_data(student):
    """Arma el dict de contexto del alumno que se pasa a la IA."""
    recent_reports = Report.query.filter_by(
        student_id=student.id
    ).order_by(Report.created_at.desc()).limit(5).all()
    return {
        'username': student.user.username,
        'tdah_type': student.tdah_type or 'En evaluación',
        'tdah_confidence': student.tdah_confidence or 0,
        'total_tests': Report.query.filter_by(student_id=student.id).count(),
        'avg_attention': float(db.session.query(
            db.func.avg(Session.attention_score)
        ).filter_by(student_id=student.id).scalar() or 0),
        'recent_history': [
            {
                'type': r.report_type,
                'tipo_tdah': r.tipo_tdah,
                'confianza': r.confianza,
                'date': r.created_at.strftime('%Y-%m-%d')
            }
            for r in recent_reports
        ]
    }


@teacher_bp.route('/reports/create/<int:session_id>', methods=['GET', 'POST'])
@teacher_required
def create_report(session_id):
    session = Session.query.get_or_404(session_id)
    student = session.student

    if student.teacher_id != current_user.id:
        flash('No autorizado', 'danger')
        return redirect(url_for('teacher.reports'))

    if request.method == 'GET':
        ai_draft = None
        observations_text = ''
        recommendations_text = ''
        alerts_text = ''
        try:
            from app.reports.ai_service import ai_service
            from app.shared.helpers import build_observations, build_recommendations
            student_data = _build_student_data(student)
            ai_draft = ai_service.generate_teacher_report(student_data, period='última sesión')
            observations_text = build_observations(ai_draft)
            recommendations_text = build_recommendations(ai_draft)
            if ai_draft and ai_draft.get('alertas'):
                alerts_text = '• ' + '\n• '.join(ai_draft['alertas'])
        except Exception as e:
            current_app.logger.error(f"Error generando borrador IA: {e}")

        return render_template(
            'teacher/create_report.html',
            session=session,
            student=student,
            ai_draft=ai_draft,
            observations_text=observations_text,
            recommendations_text=recommendations_text,
            alerts_text=alerts_text,
        )

    data = request.form

    # Combinar alertas al final del contenido si el profesor las ingresó
    content_text = data.get('content', '')
    alerts_val = (data.get('alerts') or '').strip()
    if alerts_val:
        content_text = content_text.rstrip() + '\n\nAlertas:\n' + alerts_val

    try:
        new_report = Report(
            student_id=student.id,
            teacher_id=current_user.id,
            session_id=session_id,
            report_type='manual_teacher',
            content=content_text,
            recommendations=data.get('recommendations'),
            parent_comments=data.get('parent_comments'),
        )
        
        db.session.add(new_report)
        db.session.commit()
        
        # Si se marca para enviar a padres
        if data.get('send_to_parents'):
            try:
                from app.models.notification import Notification
                Notification.notify_parents_of_student(
                    student_id=student.id,
                    title=f"Nuevo reporte de {current_user.username}",
                    message=(content_text[:150] + '...') if len(content_text) > 150 else content_text,
                    notification_type='new_report'
                )
                new_report.sent_to_parents = True
                db.session.commit()
                flash('Reporte enviado a los tutores', 'success')
            except Exception as e:
                print(f"⚠️ Error al notificar padres: {e}")
                flash('Reporte creado, pero falló el envío a padres', 'warning')
        else:
            flash('Reporte creado exitosamente', 'success')
        
        return redirect(url_for('teacher.reports'))
    
    except Exception as e:
        db.session.rollback()
        import traceback
        traceback.print_exc()
        flash(f'Error al crear reporte: {str(e)}', 'danger')
        return redirect(url_for('teacher.create_report', session_id=session_id))

@teacher_bp.route('/reports/<int:report_id>/pdf')
@teacher_required
def report_pdf(report_id):
    """Genera y descarga el PDF del reporte."""
    report = Report.query.get_or_404(report_id)
    student = report.student
    if student.teacher_id != current_user.id:
        flash('No autorizado', 'danger')
        return redirect(url_for('teacher.reports'))
    try:
        from app.reports.pdf_generator import generate_report_pdf
        from flask import send_file
        import io
        pdf_bytes = generate_report_pdf(report, student)
        nombre = student.get_display_name().replace(' ', '_')
        fecha = report.created_at.strftime('%Y%m%d') if report.created_at else 'sin_fecha'
        filename = f"reporte_{nombre}_{fecha}.pdf"
        return send_file(
            io.BytesIO(pdf_bytes),
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename,
        )
    except Exception as e:
        import traceback; traceback.print_exc()
        flash(f'Error al generar PDF: {str(e)}', 'danger')
        return redirect(url_for('teacher.reports'))


@teacher_bp.route('/reports/<int:report_id>/send-whatsapp', methods=['POST'])
@teacher_required
def report_send_whatsapp(report_id):
    """Genera el PDF y lo envía por WhatsApp al tutor."""
    report = Report.query.get_or_404(report_id)
    student = report.student
    if student.teacher_id != current_user.id:
        return jsonify({'error': 'No autorizado'}), 403

    phone = student.tutor_phone or student.emergency_contact_phone
    if not phone:
        return jsonify({'error': 'El alumno no tiene teléfono del tutor registrado'}), 400

    try:
        from app.reports.pdf_generator import generate_report_pdf
        pdf_bytes = generate_report_pdf(report, student)

        # Notificación interna siempre
        from app.core.models.notification import Notification
        Notification.notify_tutor_of_student(
            student_id=student.id,
            title="Nuevo reporte disponible",
            message=f"El docente {current_user.username} ha generado un nuevo reporte. "
                    f"Consulta la plataforma para verlo completo.",
            notification_type='new_report',
            send_whatsapp=True,
        )

        return jsonify({'success': True, 'message': f'Notificación enviada al tutor ({phone})'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@teacher_bp.route('/sessions/<int:session_id>')
@teacher_required
def session_detail(session_id):
    """Ver detalles de una sesión"""
    session = Session.query.get_or_404(session_id)
    student = session.student
    
    # Verificar autorización
    if student.teacher_id != current_user.id:
        flash('No autorizado', 'danger')
        return redirect(url_for('teacher.index'))
    
    return render_template('teacher/session_detail.html', 
                        session=session, 
                        student=student)
    
@teacher_bp.route('/api/ai-suggestions', methods=['POST'])
@teacher_required
def ai_suggestions():
    """Genera sugerencias de IA reales para un reporte"""
    from app.reports.ai_service import ai_service
    
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        
        session = Session.query.get_or_404(session_id)
        student = session.student
        
        if student.teacher_id != current_user.id:
            return jsonify({'error': 'No autorizado'}), 403
        
        # Recopilar contexto
        recent_reports = Report.query.filter_by(
            student_id=student.id
        ).order_by(Report.created_at.desc()).limit(5).all()
        
        student_data = {
            'username': student.user.username,
            'tdah_type': student.tdah_type or 'En evaluación',
            'tdah_confidence': student.tdah_confidence or 0,
            'total_tests': Report.query.filter_by(student_id=student.id).count(),
            'avg_attention': float(db.session.query(
                db.func.avg(Session.attention_score)
            ).filter_by(student_id=student.id).scalar() or 0),
            'recent_history': [
                {
                    'type': r.report_type,
                    'tipo_tdah': r.tipo_tdah,
                    'confianza': r.confianza,
                    'date': r.created_at.strftime('%Y-%m-%d')
                }
                for r in recent_reports
            ]
        }
        
        # Llamar a IA
        report_ai = ai_service.generate_teacher_report(student_data, period='sesión actual')
        
        return jsonify({
            'success': True,
            'suggestions': report_ai
        })
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500