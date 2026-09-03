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

@teacher_bp.route('/reports')
@teacher_required
def reports():
    """Lista de reportes"""
    reports = Report.query.filter_by(
        teacher_id=current_user.id
    ).order_by(Report.created_at.desc()).all()
    
    return render_template('teacher/reports.html', reports=reports)


# Etiquetas legibles para los slugs que guarda Student.tdah_type
TDAH_PERFIL_LABELS = {
    'typical': 'Típico (sin TDAH)',
    'inatento': 'TDAH — Inatento',
    'hiperactivo': 'TDAH — Hiperactivo',
    'combinado': 'TDAH — Combinado',
    'sin_determinar': 'En análisis',
}


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