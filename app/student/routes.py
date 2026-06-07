from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, current_app, send_file
from flask_login import login_required, current_user
from app.models.student import Student
from app.models.activity import Activity, Session
from app.models.report import Report
from app.extensions import db
from functools import wraps
from werkzeug.utils import secure_filename
import os
from datetime import datetime, timedelta
import json
from sqlalchemy import func, desc
import csv
from io import StringIO, BytesIO

student_bp = Blueprint('student', __name__, url_prefix='/student')

def student_required(f):
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if current_user.role != 'student':
            flash('Acceso denegado. Se requiere rol de estudiante.', 'danger')
            return redirect(url_for('auth.dashboard'))
        return f(*args, **kwargs)
    return decorated_function

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'mp3', 'wav', 'webm'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_student_profile():
    """Helper para obtener el perfil del estudiante correctamente"""
    student_profile = current_user.student_profile
    
    # Si es una relación lazy (AppenderQuery), obtener el primer resultado
    if hasattr(student_profile, 'first'):
        return student_profile.first()
    
    # Si es una lista
    if isinstance(student_profile, list):
        return student_profile[0] if student_profile else None
    
    # Si ya es el objeto directo
    return student_profile

@student_bp.route('/')
@student_required
def index():
    """Dashboard del estudiante"""
    student_profile = get_student_profile()
    
    if not student_profile:
        flash('No se encontró perfil de estudiante', 'danger')
        return redirect(url_for('auth.logout'))
    
    # Actividades pendientes
    pending_activities = Activity.query.filter_by(
        student_id=student_profile.id
    ).order_by(Activity.created_at.desc()).limit(5).all()
    
    # Últimas sesiones
    recent_sessions = Session.query.filter_by(
        student_id=student_profile.id
    ).order_by(Session.created_at.desc()).limit(5).all()
    
    # Estadísticas personales
    total_sessions = Session.query.filter_by(student_id=student_profile.id).count()
    
    avg_attention = db.session.query(
        db.func.avg(Session.attention_score)
    ).filter_by(student_id=student_profile.id).scalar() or 0
    
    # Tests completados (visión y audio)
    vision_tests = Report.query.filter_by(
        student_id=student_profile.id,
        report_type='vision_test'
    ).count()
    
    audio_tests = Report.query.filter_by(
        student_id=student_profile.id,
        report_type='audio_test'
    ).count()
    
    # ⭐ NUEVO: Tests de Stroop y Go/No-Go
    stroop_tests = Report.query.filter_by(
        student_id=student_profile.id,
        report_type='stroop_test'
    ).count()
    
    gonogo_tests = Report.query.filter_by(
        student_id=student_profile.id,
        report_type='gonogo_test'
    ).count()
    
    stats = {
        'total_activities': Activity.query.filter_by(student_id=student_profile.id).count(),
        'total_sessions': total_sessions,
        'avg_attention': round(avg_attention, 2),
        'pending_activities': len(pending_activities),
        'vision_tests': vision_tests,
        'audio_tests': audio_tests,
        'stroop_tests': stroop_tests,
        'gonogo_tests': gonogo_tests,
        'total_tests': vision_tests + audio_tests + stroop_tests + gonogo_tests,
        'total_ar': Session.query.filter_by(student_id=student_profile.id).count(),
    }

    streak = _calcular_racha(student_profile.id)

    try:
        from app.services.badge_service import get_student_badges
        badges = get_student_badges(student_profile)
    except Exception:
        badges = []

    return render_template('student/index.html',
                            student=student_profile,
                            pending_activities=pending_activities,
                            recent_sessions=recent_sessions,
                            stats=stats,
                            streak=streak,
                            badges=badges)
def _calcular_racha(student_id: int) -> int:
    """Días consecutivos con actividad (sesión o test) hasta hoy."""
    from sqlalchemy import cast, Date as SqlDate
    today = datetime.utcnow().date()
    streak = 0
    for offset in range(0, 30):
        day = today - timedelta(days=offset)
        has_session = db.session.query(Session.id).filter(
            Session.student_id == student_id,
            cast(Session.created_at, SqlDate) == day,
        ).first()
        has_report = db.session.query(Report.id).filter(
            Report.student_id == student_id,
            cast(Report.created_at, SqlDate) == day,
            Report.report_type != 'manual_teacher',
        ).first()
        if has_session or has_report:
            streak += 1
        elif streak > 0:
            break
    return streak


@student_bp.route('/tests')
@student_required
def tests_index():
    """Selector visual de tests cognitivos."""
    student_profile = get_student_profile()
    counts = {
        'vision_test':  Report.query.filter_by(student_id=student_profile.id, report_type='vision_test').count(),
        'audio_test':   Report.query.filter_by(student_id=student_profile.id, report_type='audio_test').count(),
        'stroop_test':  Report.query.filter_by(student_id=student_profile.id, report_type='stroop_test').count(),
        'gonogo_test':  Report.query.filter_by(student_id=student_profile.id, report_type='gonogo_test').count(),
    }
    return render_template('student/tests_index.html', student=student_profile, counts=counts)


@student_bp.route('/activities')
@student_required
def activities():
    """Lista de actividades disponibles"""
    student_profile = get_student_profile()
    
    activities = Activity.query.filter_by(
        student_id=student_profile.id
    ).order_by(Activity.created_at.desc()).all()
    
    activities_data = []
    for activity in activities:
        sessions_count = Session.query.filter_by(
            activity_id=activity.id,
            student_id=student_profile.id
        ).count()
        
        last_session = Session.query.filter_by(
            activity_id=activity.id,
            student_id=student_profile.id
        ).order_by(Session.created_at.desc()).first()
        
        activities_data.append({
            'activity': activity,
            'sessions_count': sessions_count,
            'last_session': last_session
        })
    
    return render_template('student/activities.html', 
                        activities_data=activities_data)

@student_bp.route('/activities/<int:activity_id>')
@student_required
def activity_detail(activity_id):
    """Ver detalle de una actividad"""
    activity = Activity.query.get_or_404(activity_id)
    student_profile = get_student_profile()
    
    if activity.student_id != student_profile.id:
        flash('No tienes acceso a esta actividad', 'danger')
        return redirect(url_for('student.activities'))
    
    previous_sessions = Session.query.filter_by(
        activity_id=activity_id,
        student_id=student_profile.id
    ).order_by(Session.created_at.desc()).all()
    
    return render_template('student/activity_detail.html',
                        activity=activity,
                        previous_sessions=previous_sessions)

@student_bp.route('/activities/<int:activity_id>/start')
@student_required
def start_activity(activity_id):
    """Iniciar una actividad"""
    activity = Activity.query.get_or_404(activity_id)
    student_profile = get_student_profile()
    
    if activity.student_id != student_profile.id:
        flash('No autorizado', 'danger')
        return redirect(url_for('student.activities'))
    
    return render_template('student/activity_player.html', activity=activity)

@student_bp.route('/sessions/record', methods=['POST'])
@student_required
def record_session():
    """Guardar una sesión"""
    student_profile = get_student_profile()
    
    activity_id = request.form.get('activity_id')
    
    if not activity_id:
        return jsonify({'error': 'activity_id requerido'}), 400
    
    try:
        new_session = Session(
            student_id=student_profile.id,
            activity_id=activity_id,
            created_at=datetime.utcnow()
        )
        
        if 'video' in request.files:
            video = request.files['video']
            if video and allowed_file(video.filename):
                filename = secure_filename(f"video_{student_profile.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{video.filename.rsplit('.', 1)[1]}")
                video_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'videos', filename)
                video.save(video_path)
                new_session.video_path = video_path
        
        if 'audio' in request.files:
            audio = request.files['audio']
            if audio and allowed_file(audio.filename):
                filename = secure_filename(f"audio_{student_profile.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{audio.filename.rsplit('.', 1)[1]}")
                audio_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'audios', filename)
                audio.save(audio_path)
                new_session.audio_path = audio_path
        
        completion_time = request.form.get('completion_time')
        if completion_time:
            new_session.completion_time = int(completion_time)
        
        if not new_session.attention_score:
            new_session.attention_score = 75
        
        db.session.add(new_session)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'session_id': new_session.id,
            'message': 'Sesión guardada exitosamente'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@student_bp.route('/progress')
@student_required
def progress():
    """Dashboard de progreso mejorado con gráficas"""
    student_profile = get_student_profile()
    
    # Parámetros de filtro
    days = request.args.get('days', 30, type=int)
    test_type = request.args.get('type', 'all')
    
    # Fecha de inicio
    start_date = datetime.now() - timedelta(days=days)
    
    # Obtener tests de visión (para gráficas existentes)
    vision_reports = Report.query.filter(
        Report.student_id == student_profile.id,
        Report.report_type == 'vision_test',
        Report.created_at >= start_date
    ).order_by(Report.created_at.asc()).all()

    # Obtener tests de audio (para gráficas existentes)
    audio_reports = Report.query.filter(
        Report.student_id == student_profile.id,
        Report.report_type == 'audio_test',
        Report.created_at >= start_date
    ).order_by(Report.created_at.asc()).all()

    # Procesar datos de visión
    vision_data = []
    for report in vision_reports:
        try:
            content = json.loads(report.content)
            vision_data.append({
                'fecha': report.created_at.strftime('%Y-%m-%d %H:%M'),
                'tipo': content.get('tipo_tdah', 'N/A'),
                'confianza': content.get('confianza', 0),
                'metricas': content.get('metricas', {}),
                'scores': content.get('scores_detallados', {})
            })
        except:
            continue

    # Procesar datos de audio
    audio_data = []
    for report in audio_reports:
        try:
            content = json.loads(report.content)
            audio_data.append({
                'fecha': report.created_at.strftime('%Y-%m-%d %H:%M'),
                'tipo': content.get('tipo_tdah', 'N/A'),
                'confianza': content.get('confianza', 0),
                'metricas': content.get('metricas', {})
            })
        except:
            continue

    # Timeline unificado: TODOS los tipos de test
    ALL_TEST_TYPES = [
        'vision_test', 'audio_test', 'stroop_test', 'gonogo_test',
        'ar_caza', 'ar_secuencia', 'ar_respiracion', 'ar_trail_making',
    ]
    TYPE_META = {
        'vision_test':    {'label': 'Test Visual',           'icon': '👁️',  'color': 'indigo'},
        'audio_test':     {'label': 'Test de Audio',         'icon': '🎙️',  'color': 'pink'},
        'stroop_test':    {'label': 'Test Stroop',           'icon': '🎨',  'color': 'violet'},
        'gonogo_test':    {'label': 'Go / No-Go',            'icon': '⚡',  'color': 'amber'},
        'ar_caza':        {'label': 'AR: Caza de Objetos',   'icon': '🎯',  'color': 'emerald'},
        'ar_secuencia':   {'label': 'AR: Secuencia Luces',   'icon': '💡',  'color': 'yellow'},
        'ar_respiracion': {'label': 'AR: Respiración',       'icon': '🧘',  'color': 'teal'},
        'ar_trail_making':{'label': 'AR: Trail Making',      'icon': '🔢',  'color': 'blue'},
    }
    all_reports = Report.query.filter(
        Report.student_id == student_profile.id,
        Report.report_type.in_(ALL_TEST_TYPES),
        Report.created_at >= start_date
    ).order_by(Report.created_at.desc()).all()

    all_tests = []
    for r in all_reports:
        meta = TYPE_META.get(r.report_type, {'label': r.report_type, 'icon': '📋', 'color': 'gray'})
        try:
            content = json.loads(r.content) if r.content else {}
            tipo_tdah = content.get('tipo_tdah', r.tipo_tdah or 'N/A')
            confianza = content.get('confianza', r.confianza or 0)
            results_dict = content.get('results', {})
            score = content.get('score', results_dict.get('score', 0) if isinstance(results_dict, dict) else 0)
        except Exception:
            tipo_tdah = r.tipo_tdah or 'N/A'
            confianza = r.confianza or 0
            score = 0
        all_tests.append({
            'fecha': r.created_at.strftime('%d/%m/%Y %H:%M'),
            'tipo_label': meta['label'],
            'icon': meta['icon'],
            'color': meta['color'],
            'tipo_tdah': tipo_tdah,
            'confianza': round(float(confianza), 1),
            'score': round(float(score), 1) if score else None,
            'report_type': r.report_type,
        })

    # Calcular tendencias
    tendencias = calcular_tendencias(vision_data, audio_data)

    # Estadísticas generales (ahora incluye todos los tipos)
    stats = {
        'total_vision': len(vision_reports),
        'total_audio': len(audio_reports),
        'total_stroop': sum(1 for t in all_tests if t['report_type'] == 'stroop_test'),
        'total_gonogo': sum(1 for t in all_tests if t['report_type'] == 'gonogo_test'),
        'total_ar': sum(1 for t in all_tests if t['report_type'].startswith('ar_')),
        'total_tests': len(all_tests),
        'promedio_confianza_vision': sum([d['confianza'] for d in vision_data]) / len(vision_data) if vision_data else 0,
        'promedio_confianza_audio': sum([d['confianza'] for d in audio_data]) / len(audio_data) if audio_data else 0
    }

    # Datos para gráficas
    chart_data = preparar_datos_graficas(vision_data, audio_data)

    return render_template('student/progress.html',
                         student=student_profile,
                         vision_data=vision_data,
                         audio_data=audio_data,
                         all_tests=all_tests,
                         stats=stats,
                         tendencias=tendencias,
                         chart_data=chart_data,
                         days=days,
                         test_type=test_type)

def calcular_tendencias(vision_data, audio_data):
    """Calcula tendencias de mejora/empeoramiento"""
    tendencias = {
        'vision': {'direccion': '→', 'texto': 'Sin cambios', 'porcentaje': 0},
        'audio': {'direccion': '→', 'texto': 'Sin cambios', 'porcentaje': 0}
    }
    
    # Tendencia visión
    if len(vision_data) >= 2:
        primera_mitad = vision_data[:len(vision_data)//2]
        segunda_mitad = vision_data[len(vision_data)//2:]
        
        avg_primera = sum([d['confianza'] for d in primera_mitad]) / len(primera_mitad) if primera_mitad else 0
        avg_segunda = sum([d['confianza'] for d in segunda_mitad]) / len(segunda_mitad) if segunda_mitad else 0
        
        cambio = avg_segunda - avg_primera
        porcentaje = (cambio / avg_primera * 100) if avg_primera > 0 else 0
        
        if cambio > 5:
            tendencias['vision'] = {'direccion': '↑', 'texto': 'Mejorando', 'porcentaje': round(porcentaje, 1)}
        elif cambio < -5:
            tendencias['vision'] = {'direccion': '↓', 'texto': 'Disminuyendo', 'porcentaje': round(abs(porcentaje), 1)}
    
    # Tendencia audio
    if len(audio_data) >= 2:
        primera_mitad = audio_data[:len(audio_data)//2]
        segunda_mitad = audio_data[len(audio_data)//2:]
        
        avg_primera = sum([d['confianza'] for d in primera_mitad]) / len(primera_mitad) if primera_mitad else 0
        avg_segunda = sum([d['confianza'] for d in segunda_mitad]) / len(segunda_mitad) if segunda_mitad else 0
        
        cambio = avg_segunda - avg_primera
        porcentaje = (cambio / avg_primera * 100) if avg_primera > 0 else 0
        
        if cambio > 5:
            tendencias['audio'] = {'direccion': '↑', 'texto': 'Mejorando', 'porcentaje': round(porcentaje, 1)}
        elif cambio < -5:
            tendencias['audio'] = {'direccion': '↓', 'texto': 'Disminuyendo', 'porcentaje': round(abs(porcentaje), 1)}
    
    return tendencias

def preparar_datos_graficas(vision_data, audio_data):
    """Prepara datos para Chart.js"""
    return {
        'vision': {
            'labels': [d['fecha'] for d in vision_data],
            'confianza': [d['confianza'] for d in vision_data],
            'dispersion': [d['metricas'].get('dispersion_promedio', 0) for d in vision_data],
            'atencion_central': [d['metricas'].get('atencion_central', 0) for d in vision_data]
        },
        'audio': {
            'labels': [d['fecha'] for d in audio_data],
            'confianza': [d['confianza'] for d in audio_data],
            'precision': [d['metricas'].get('precision', 0) for d in audio_data],
            'velocidad': [d['metricas'].get('velocidad_lectura', 0) for d in audio_data]
        }
    }

@student_bp.route('/progress/export')
@student_required
def progress_export():
    """Exportar progreso a CSV"""
    student_profile = get_student_profile()
    
    # Obtener todos los reportes
    vision_reports = Report.query.filter_by(
        student_id=student_profile.id,
        report_type='vision_test'
    ).order_by(Report.created_at.asc()).all()
    
    audio_reports = Report.query.filter_by(
        student_id=student_profile.id,
        report_type='audio_test'
    ).order_by(Report.created_at.asc()).all()
    
    # Crear CSV
    output = StringIO()
    writer = csv.writer(output)
    
    # Headers
    writer.writerow(['Fecha', 'Tipo de Test', 'Clasificación', 'Confianza %', 'Métricas'])
    
    # Datos de visión
    for report in vision_reports:
        try:
            content = json.loads(report.content)
            metricas_str = f"Dispersión: {content.get('metricas', {}).get('dispersion_promedio', 0)}, " \
                          f"Atención: {content.get('metricas', {}).get('atencion_central', 0)}%"
            writer.writerow([
                report.created_at.strftime('%Y-%m-%d %H:%M'),
                'Visión',
                content.get('tipo_tdah', 'N/A'),
                content.get('confianza', 0),
                metricas_str
            ])
        except:
            continue
    
    # Datos de audio
    for report in audio_reports:
        try:
            content = json.loads(report.content)
            metricas_str = f"Precisión: {content.get('metricas', {}).get('precision', 0)}%, " \
                          f"Velocidad: {content.get('metricas', {}).get('velocidad_lectura', 0)} ppm"
            writer.writerow([
                report.created_at.strftime('%Y-%m-%d %H:%M'),
                'Audio',
                content.get('tipo_tdah', 'N/A'),
                content.get('confianza', 0),
                metricas_str
            ])
        except:
            continue
    
    # Preparar respuesta
    output.seek(0)
    return send_file(
        BytesIO(output.getvalue().encode('utf-8')),
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'progreso_{student_profile.id}_{datetime.now().strftime("%Y%m%d")}.csv'
    )

@student_bp.route('/sessions/<int:session_id>')
@student_required
def session_detail(session_id):
    """Ver detalles de una sesión"""
    session = Session.query.get_or_404(session_id)
    student_profile = get_student_profile()
    
    if session.student_id != student_profile.id:
        flash('No autorizado', 'danger')
        return redirect(url_for('student.progress'))
    
    return render_template('student/session_detail.html', session=session)

@student_bp.route('/feedback')
@student_required
def feedback():
    """Ver retroalimentación del profesor"""
    student_profile = get_student_profile()
    
    reports = Report.query.filter_by(
        student_id=student_profile.id
    ).order_by(Report.created_at.desc()).all()
    
    return render_template('student/feedback.html', reports=reports)