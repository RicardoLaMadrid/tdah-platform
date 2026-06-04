from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from app.models.user import User
from app.models.student import Student
from app.models.activity import Activity, Session
from app.models.report import Report
from app.services.ai_generator import AIActivityGenerator
from app import db
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
    """Dashboard del profesor"""
    # Mis estudiantes
    my_students = Student.query.filter_by(teacher_id=current_user.id).all()
    
    # Actividades recientes que he creado
    recent_activities = Activity.query.filter_by(
        teacher_id=current_user.id
    ).order_by(Activity.created_at.desc()).limit(5).all()
    
    # Sesiones recientes de mis estudiantes
    student_ids = [s.id for s in my_students]
    recent_sessions = Session.query.filter(
        Session.student_id.in_(student_ids)
    ).order_by(Session.created_at.desc()).limit(5).all() if student_ids else []
    
    # Estadísticas
    stats = {
        'total_students': len(my_students),
        'total_activities': Activity.query.filter_by(teacher_id=current_user.id).count(),
        'pending_reports': Report.query.filter_by(
            teacher_id=current_user.id,
            sent_to_parents=False
        ).count(),
        'sessions_today': Session.query.filter(
            Session.student_id.in_(student_ids),
            Session.created_at >= datetime.utcnow().date()
        ).count() if student_ids else 0
    }
    
    return render_template('teacher/index.html',
                         students=my_students,
                         recent_activities=recent_activities,
                         recent_sessions=recent_sessions,
                         stats=stats)

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
    avg_attention = db.session.query(
        db.func.avg(Session.attention_score)
    ).filter_by(student_id=student_id).scalar() or 0
    
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

@teacher_bp.route('/activities')
@teacher_required
def activities():
    """Lista de actividades creadas"""
    activities = Activity.query.filter_by(
        teacher_id=current_user.id
    ).order_by(Activity.created_at.desc()).all()
    
    return render_template('teacher/activities.html', activities=activities)

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
        return redirect(url_for('teacher.activities'))
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error al crear actividad: {str(e)}', 'danger')
        return redirect(url_for('teacher.create_activity'))

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
        
        # Generar actividad con IA
        ai_generator = AIActivityGenerator(current_app.config['OPENAI_API_KEY'])
        generated_activity = ai_generator.generate_activity(student_profile, session_data)
        
        # Crear la actividad en la BD
        new_activity = Activity(
            student_id=student_id,
            teacher_id=current_user.id,
            title=generated_activity['title'],
            description=generated_activity['description'],
            activity_type=generated_activity['activity_type'],
            difficulty_level=generated_activity['difficulty_level'],
            instructions=generated_activity['instructions'],
            ar_content=generated_activity.get('ar_content')
        )
        
        db.session.add(new_activity)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'activity': new_activity.to_dict(),
            'message': 'Actividad generada con IA exitosamente'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@teacher_bp.route('/reports')
@teacher_required
def reports():
    """Lista de reportes"""
    reports = Report.query.filter_by(
        teacher_id=current_user.id
    ).order_by(Report.created_at.desc()).all()
    
    return render_template('teacher/reports.html', reports=reports)

@teacher_bp.route('/reports/create/<int:session_id>', methods=['GET', 'POST'])
@teacher_required
def create_report(session_id):
    session = Session.query.get_or_404(session_id)
    student = session.student
    
    if student.teacher_id != current_user.id:
        flash('No autorizado', 'danger')
        return redirect(url_for('teacher.reports'))
    
    if request.method == 'GET':
        return render_template('teacher/create_report.html', session=session, student=student)
    
    data = request.form
    
    try:
        new_report = Report(
            student_id=student.id,
            teacher_id=current_user.id,
            session_id=session_id,
            report_type='manual_teacher',
            content=data.get('content'),
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
                    message=(data.get('content', '')[:150] + '...') if len(data.get('content', '')) > 150 else data.get('content', ''),
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
    from app.services.ai_service import ai_service
    
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
            'avg_attention': db.session.query(
                db.func.avg(Session.attention_score)
            ).filter_by(student_id=student.id).scalar() or 0,
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