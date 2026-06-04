from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from app.models.parent import Parent, ParentStudent
from app.models.notification import Notification
from app.models.student import Student
from app.models.report import Report
from app.models.activity import Session
from app import db
from functools import wraps
from datetime import datetime, timedelta
import json
from sqlalchemy import desc

parent_bp = Blueprint('parent', __name__, url_prefix='/parent')

def parent_required(f):
    """Decorator para rutas que requieren rol de padre"""
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if current_user.role != 'parent':
            flash('Acceso denegado. Se requiere rol de padre.', 'danger')
            return redirect(url_for('auth.dashboard'))
        return f(*args, **kwargs)
    return decorated_function

def get_parent_profile():
    """Helper para obtener el perfil del padre"""
    parent_profile = current_user.parent_profile
    
    if hasattr(parent_profile, 'first'):
        return parent_profile.first()
    
    if isinstance(parent_profile, list):
        return parent_profile[0] if parent_profile else None
    
    return parent_profile


@parent_bp.route('/')
@parent_required
def index():
    """Dashboard principal del padre"""
    parent_profile = get_parent_profile()
    
    if not parent_profile:
        flash('No se encontró perfil de padre', 'danger')
        return redirect(url_for('auth.logout'))
    
    # Obtener hijos
    children = parent_profile.get_children()
    
    # Estadísticas generales
    stats = {
        'total_children': len(children),
        'unread_notifications': parent_profile.get_notifications_count(),
        'total_tests': 0,
        'alerts': 0
    }
    
    # Calcular estadísticas de todos los hijos
    for child_data in children:
        student = child_data['student']
        
        # Contar tests
        tests_count = Report.query.filter_by(student_id=student.id).count()
        stats['total_tests'] += tests_count
        
        # Verificar si necesita re-evaluación
        if student.necesita_reevaluacion():
            stats['alerts'] += 1
    
    # Notificaciones recientes (últimas 5)
    recent_notifications = Notification.query.filter_by(
        user_id=current_user.id
    ).order_by(desc(Notification.created_at)).limit(5).all()
    
    return render_template('parent/index.html',
                         parent=parent_profile,
                         children=children,
                         stats=stats,
                         recent_notifications=recent_notifications)


@parent_bp.route('/child/<int:student_id>')
@parent_required
def view_child(student_id):
    """Ver detalles de un hijo específico"""
    parent_profile = get_parent_profile()
    
    # Verificar que el padre tenga acceso a este estudiante
    link = ParentStudent.query.filter_by(
        parent_id=parent_profile.id,
        student_id=student_id
    ).first()
    
    if not link:
        flash('No tienes acceso a este estudiante', 'danger')
        return redirect(url_for('parent.index'))
    
    student = Student.query.get_or_404(student_id)
    
    # Obtener reportes recientes
    reports = Report.query.filter_by(
        student_id=student_id
    ).order_by(desc(Report.created_at)).limit(10).all()
    
    # Procesar reportes para mostrar
    reports_data = []
    for report in reports:
        try:
            content = json.loads(report.content)
            reports_data.append({
                'id': report.id,
                'type': report.report_type,
                'date': report.created_at,
                'tipo_tdah': content.get('tipo_tdah', 'N/A'),
                'confianza': content.get('confianza', 0),
                'recommendations': report.recommendations
            })
        except:
            continue
    
    # Últimas sesiones
    recent_sessions = Session.query.filter_by(
        student_id=student_id
    ).order_by(desc(Session.created_at)).limit(5).all()
    
    # Estadísticas del hijo
    child_stats = {
        'total_reports': Report.query.filter_by(student_id=student_id).count(),
        'total_sessions': Session.query.filter_by(student_id=student_id).count(),
        'vision_tests': Report.query.filter_by(student_id=student_id, report_type='vision_test').count(),
        'audio_tests': Report.query.filter_by(student_id=student_id, report_type='audio_test').count(),
        'stroop_tests': Report.query.filter_by(student_id=student_id, report_type='stroop_test').count(),
        'gonogo_tests': Report.query.filter_by(student_id=student_id, report_type='gonogo_test').count(),
    }
    
    return render_template('parent/child_detail.html',
                         parent=parent_profile,
                         student=student,
                         relationship=link.relationship,
                         reports=reports_data,
                         recent_sessions=recent_sessions,
                         child_stats=child_stats)


@parent_bp.route('/child/<int:student_id>/progress')
@parent_required
def child_progress(student_id):
    """Ver progreso detallado del hijo"""
    parent_profile = get_parent_profile()
    
    # Verificar acceso
    link = ParentStudent.query.filter_by(
        parent_id=parent_profile.id,
        student_id=student_id
    ).first()
    
    if not link:
        flash('No tienes acceso a este estudiante', 'danger')
        return redirect(url_for('parent.index'))
    
    student = Student.query.get_or_404(student_id)
    
    # Obtener datos de progreso (últimos 30 días)
    start_date = datetime.now() - timedelta(days=30)
    
    # Tests de visión
    vision_reports = Report.query.filter(
        Report.student_id == student_id,
        Report.report_type == 'vision_test',
        Report.created_at >= start_date
    ).order_by(Report.created_at.asc()).all()
    
    # Tests de audio
    audio_reports = Report.query.filter(
        Report.student_id == student_id,
        Report.report_type == 'audio_test',
        Report.created_at >= start_date
    ).order_by(Report.created_at.asc()).all()
    
    # Procesar datos para gráficas
    progress_data = {
        'vision': {
            'labels': [],
            'confianza': []
        },
        'audio': {
            'labels': [],
            'confianza': []
        }
    }
    
    for report in vision_reports:
        try:
            content = json.loads(report.content)
            progress_data['vision']['labels'].append(report.created_at.strftime('%d/%m'))
            progress_data['vision']['confianza'].append(content.get('confianza', 0))
        except:
            continue
    
    for report in audio_reports:
        try:
            content = json.loads(report.content)
            progress_data['audio']['labels'].append(report.created_at.strftime('%d/%m'))
            progress_data['audio']['confianza'].append(content.get('confianza', 0))
        except:
            continue
    
    return render_template('parent/child_progress.html',
                         parent=parent_profile,
                         student=student,
                         progress_data=progress_data)


@parent_bp.route('/notifications')
@parent_required
def notifications():
    """Ver todas las notificaciones"""
    parent_profile = get_parent_profile()
    
    # Obtener todas las notificaciones
    all_notifications = Notification.query.filter_by(
        user_id=current_user.id
    ).order_by(desc(Notification.created_at)).all()
    
    return render_template('parent/notifications.html',
                         parent=parent_profile,
                         notifications=all_notifications)


@parent_bp.route('/notifications/<int:notification_id>/read', methods=['POST'])
@parent_required
def mark_notification_read(notification_id):
    """Marcar notificación como leída"""
    notification = Notification.query.get_or_404(notification_id)
    
    # Verificar que la notificación pertenece al padre
    if notification.user_id != current_user.id:
        return jsonify({'success': False, 'message': 'No autorizado'}), 403
    
    notification.is_read = True
    db.session.commit()
    
    return jsonify({'success': True})


@parent_bp.route('/notifications/mark_all_read', methods=['POST'])
@parent_required
def mark_all_notifications_read():
    """Marcar todas las notificaciones como leídas"""
    Notification.query.filter_by(
        user_id=current_user.id,
        is_read=False
    ).update({'is_read': True})
    
    db.session.commit()
    
    flash('Todas las notificaciones marcadas como leídas', 'success')
    return redirect(url_for('parent.notifications'))


@parent_bp.route('/report/<int:report_id>')
@parent_required
def view_report(report_id):
    """Ver reporte detallado"""
    parent_profile = get_parent_profile()
    report = Report.query.get_or_404(report_id)
    
    # Verificar que el padre tenga acceso al estudiante
    link = ParentStudent.query.filter_by(
        parent_id=parent_profile.id,
        student_id=report.student_id
    ).first()
    
    if not link:
        flash('No tienes acceso a este reporte', 'danger')
        return redirect(url_for('parent.index'))
    
    # Parsear contenido
    try:
        content = json.loads(report.content)
    except:
        content = {}
    
    return render_template('parent/report_detail.html',
                         parent=parent_profile,
                         report=report,
                         content=content,
                         student=report.student)