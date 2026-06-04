"""
Blueprint para actividades de Realidad Aumentada
"""
from flask import Blueprint, render_template, request, jsonify, current_app
from flask_login import login_required, current_user
from functools import wraps
from datetime import datetime
import json

ar_bp = Blueprint('ar', __name__, url_prefix='/ar')

def student_required(f):
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if current_user.role != 'student':
            return jsonify({'error': 'Solo estudiantes pueden acceder'}), 403
        return f(*args, **kwargs)
    return decorated_function


@ar_bp.route('/')
@student_required
def index():
    from app.models.student import Student
    from app.models.report import Report
    
    student = Student.query.filter_by(user_id=current_user.id).first()
    
    ar_types = ['ar_caza', 'ar_secuencia', 'ar_respiracion']
    ar_reports = Report.query.filter_by(student_id=student.id).filter(
        Report.report_type.in_(ar_types)  # ✅ report_type, no test_type
    ).all()
    
    stats = {
        'total_ar_activities': len(ar_reports),
        'caza_completed': len([r for r in ar_reports if r.report_type == 'ar_caza']),
        'secuencia_completed': len([r for r in ar_reports if r.report_type == 'ar_secuencia']),
        'respiracion_completed': len([r for r in ar_reports if r.report_type == 'ar_respiracion']),
    }
    
    return render_template('ar/index.html', student=student, stats=stats)


@ar_bp.route('/caza-objetos')
@student_required
def caza_objetos():
    from app.models.student import Student
    student = Student.query.filter_by(user_id=current_user.id).first()
    return render_template('ar/caza_objetos.html', student=student)


@ar_bp.route('/secuencia-luces')
@student_required
def secuencia_luces():
    from app.models.student import Student
    student = Student.query.filter_by(user_id=current_user.id).first()
    return render_template('ar/secuencia_luces.html', student=student)


@ar_bp.route('/respiracion')
@student_required
def respiracion():
    from app.models.student import Student
    student = Student.query.filter_by(user_id=current_user.id).first()
    return render_template('ar/respiracion.html', student=student)


@ar_bp.route('/save-result', methods=['POST'])
@student_required
def save_result():
    from app.extensions import db, csrf
    from app.models.student import Student
    from app.models.report import Report
    
    try:
        data = request.get_json()
        student = Student.query.filter_by(user_id=current_user.id).first()
        
        activity_type = data.get('activity_type', 'ar_unknown')
        results = data.get('results', {})
        
        # Análisis
        tipo_tdah = _analizar_resultado_ar(results, activity_type)
        confianza = int(results.get('score', 0))
        
        # ✅ Crear reporte con los campos correctos
        report = Report(
            student_id=student.id,
            report_type=activity_type,  # ar_caza, ar_secuencia, ar_respiracion
            content=json.dumps({
                'tipo_tdah': tipo_tdah,
                'confianza': confianza,
                'metricas': results,
                'activity_type': activity_type
            }, ensure_ascii=False),
            tipo_tdah=tipo_tdah,
            confianza=confianza,
            recommendations=f"Actividad AR completada: {activity_type}",
            created_at=datetime.utcnow()
        )
        
        db.session.add(report)
        db.session.commit()
        
        # Notificar a padres
        try:
            from app.models.notification import Notification
            Notification.notify_parents_of_student(
                student_id=student.id,
                title="Actividad AR Completada",
                message=f"Tu hijo/a completó la actividad '{activity_type}' con {confianza}% de puntaje.",
                notification_type='test_completed'
            )
        except Exception as e:
            print(f"⚠️  No se pudo notificar padres: {e}")
        
        return jsonify({
            'success': True,
            'report_id': report.id,
            'message': '¡Actividad guardada!'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error guardando resultado AR: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


def _analizar_resultado_ar(results, activity_type):
    """Heurística simple de clasificación. NO es diagnóstico."""
    score = results.get('score', 0)
    errors = results.get('errors', 0)
    time = results.get('time', 0)
    
    if activity_type == 'ar_caza':
        if errors > 3:
            return 'inatento'
        elif time and time < 30:
            return 'hiperactivo'
        return 'typical'
    elif activity_type == 'ar_secuencia':
        return 'inatento' if score < 50 else 'typical'
    elif activity_type == 'ar_respiracion':
        return 'hiperactivo' if score < 60 else 'typical'
    return 'sin_determinar'