from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models.user import User
from app.models.student import Student
from app.models.activity import Activity, Session
from app.models.report import Report
from app import db
from functools import wraps
from werkzeug.security import generate_password_hash

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if current_user.role != 'admin':
            flash('Acceso denegado. Se requiere rol de administrador.', 'danger')
            return redirect(url_for('auth.dashboard'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/')
@admin_required
def index():
    """Dashboard del administrador"""
    # Estadísticas generales
    total_users = User.query.count()
    total_students = Student.query.count()
    total_teachers = User.query.filter_by(role='teacher').count()
    total_activities = Activity.query.count()
    total_sessions = Session.query.count()
    
    # ⭐ NUEVO: Contar padres
    total_parents = User.query.filter_by(role='parent').count()
    
    # Usuarios recientes
    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
    
    # Sesiones recientes
    recent_sessions = Session.query.order_by(Session.created_at.desc()).limit(5).all()
    
    stats = {
        'total_users': total_users,
        'total_students': total_students,
        'total_teachers': total_teachers,
        'total_parents': total_parents,  # ⭐ NUEVO
        'total_activities': total_activities,
        'total_sessions': total_sessions
    }
    
    return render_template('admin/index.html', 
                        stats=stats,
                        recent_users=recent_users,
                        recent_sessions=recent_sessions)

@admin_bp.route('/users')
@admin_required
def users():
    """Lista de usuarios — padres se gestionan a través de los alumnos"""
    role_filter = request.args.get('role', 'all')
    
    query = User.query
    if role_filter == 'all':
        # Excluye padres del listado general
        query = query.filter(User.role != 'parent')
    elif role_filter == 'parent':
        # Si alguien fuerza el filtro de padres, redirigir
        return redirect(url_for('admin.users'))
    else:
        query = query.filter_by(role=role_filter)
    
    users = query.order_by(User.created_at.desc()).all()
    return render_template('admin/users.html', users=users, role_filter=role_filter)

@admin_bp.route('/users/create', methods=['GET', 'POST'])
@admin_required
def create_user():
    """Crear nuevo usuario"""
    if request.method == 'GET':
        teachers = User.query.filter_by(role='teacher').all()
        return render_template('admin/create_user.html', teachers=teachers)
    
    data = request.form
    
    try:
        # Validaciones
        if User.query.filter_by(username=data.get('username')).first():
            flash('El nombre de usuario ya existe', 'danger')
            return redirect(url_for('admin.create_user'))
        
        if User.query.filter_by(email=data.get('email')).first():
            flash('El email ya está registrado', 'danger')
            return redirect(url_for('admin.create_user'))
        
        # Crear usuario
        new_user = User(
            username=data.get('username'),
            email=data.get('email'),
            role=data.get('role'),
            password_hash=generate_password_hash(data.get('password'))
        )
        
        db.session.add(new_user)
        db.session.flush()  # Para obtener el ID
        
        # Si es estudiante, crear perfil
        if data.get('role') == 'student':
            student_profile = Student(
                user_id=new_user.id,
                grade=data.get('grade'),
                section=data.get('section')
            )
            db.session.add(student_profile)
        
        # ⭐ NUEVO: Si es padre, crear perfil de padre
        elif data.get('role') == 'parent':
            from app.models.parent import Parent
            parent_profile = Parent(
                user_id=new_user.id,
                phone=data.get('phone', '')
            )
            db.session.add(parent_profile)
        
        db.session.commit()
        
        flash(f'Usuario {new_user.username} creado exitosamente', 'success')
        return redirect(url_for('admin.users'))
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error al crear usuario: {str(e)}', 'danger')
        return redirect(url_for('admin.create_user'))

@admin_bp.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_user(user_id):
    """Vista detallada + edición de cualquier usuario"""
    user = User.query.get_or_404(user_id)
    
    if request.method == 'GET':
        teachers = User.query.filter_by(role='teacher').all()
        return render_template('admin/edit_user.html', user=user, teachers=teachers)
    
    data = request.form
    
    try:
        # Datos básicos de cuenta
        new_email = data.get('email', '').strip()
        if new_email and new_email != user.email:
            existing = User.query.filter_by(email=new_email).first()
            if existing and existing.id != user.id:
                flash('Ese email ya está registrado por otro usuario', 'danger')
                return redirect(url_for('admin.edit_user', user_id=user_id))
            user.email = new_email
        
        if data.get('password'):
            user.set_password(data.get('password'))
        
        # Si es estudiante: actualizar todos los campos
        if user.role == 'student':
            sp = user.student_profile.first()
            if sp:
                sp.full_name = data.get('full_name', '').strip() or None
                sp.national_id = data.get('national_id', '').strip() or None
                sp.age = int(data.get('age')) if data.get('age') else None
                sp.grade = data.get('grade', '').strip() or None
                sp.section = data.get('section', '').strip() or None
                sp.teacher_id = int(data.get('teacher_id')) if data.get('teacher_id') else None
                
                # Médico
                sp.allergies = data.get('allergies', '').strip() or None
                sp.medical_conditions = data.get('medical_conditions', '').strip() or None
                sp.medications = data.get('medications', '').strip() or None
                
                # Dirección y emergencia
                sp.address = data.get('address', '').strip() or None
                sp.emergency_contact_name = data.get('emergency_contact_name', '').strip() or None
                sp.emergency_contact_phone = data.get('emergency_contact_phone', '').strip() or None
        
        # Si es padre: actualizar perfil
        elif user.role == 'parent':
            from app.models.parent import Parent
            pp = user.parent_profile.first()
            if pp:
                pp.full_name = data.get('parent_full_name', '').strip() or None
                pp.phone = data.get('parent_phone', '').strip() or None
                pp.whatsapp_enabled = bool(data.get('parent_whatsapp_enabled'))
                pp.receive_notifications = bool(data.get('parent_receive_notifications'))
        
        db.session.commit()
        flash(f'✅ Cambios guardados para {user.username}', 'success')
        return redirect(url_for('admin.edit_user', user_id=user_id))
    
    except Exception as e:
        db.session.rollback()
        import traceback
        traceback.print_exc()
        flash(f'Error al actualizar: {str(e)}', 'danger')
        return redirect(url_for('admin.edit_user', user_id=user_id))

@admin_bp.route('/users/<int:user_id>/delete', methods=['POST'])
@admin_required
def delete_user(user_id):
    """Eliminar usuario"""
    user = User.query.get_or_404(user_id)
    
    # No permitir eliminar al propio admin
    if user.id == current_user.id:
        flash('No puedes eliminar tu propia cuenta', 'danger')
        return redirect(url_for('admin.users'))
    
    try:
        username = user.username
        db.session.delete(user)
        db.session.commit()
        
        flash(f'Usuario {username} eliminado exitosamente', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar usuario: {str(e)}', 'danger')
    
    return redirect(url_for('admin.users'))

@admin_bp.route('/assignments')
@admin_required
def assignments():
    """Ver y gestionar asignaciones estudiante-profesor"""
    students = Student.query.join(Student.user).all()
    teachers = User.query.filter_by(role='teacher').all()
    
    return render_template('admin/assignments.html', 
                         students=students, 
                         teachers=teachers)

@admin_bp.route('/assignments/assign', methods=['POST'])
@admin_required
def assign_student():
    """Asignar estudiante a profesor"""
    data = request.form
    
    try:
        student = Student.query.get_or_404(data.get('student_id'))
        teacher_id = data.get('teacher_id')
        
        if teacher_id:
            teacher = User.query.filter_by(id=teacher_id, role='teacher').first()
            if not teacher:
                flash('Profesor no encontrado', 'danger')
                return redirect(url_for('admin.assignments'))
        
        student.teacher_id = teacher_id if teacher_id else None
        db.session.commit()
        
        flash('Asignación actualizada exitosamente', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error al asignar estudiante: {str(e)}', 'danger')
    
    return redirect(url_for('admin.assignments'))

# ⭐ NUEVO: Gestión de vínculos padre-hijo
@admin_bp.route('/parent-links')
@admin_required
def parent_links():
    """Ver y gestionar vínculos padre-hijo"""
    from app.models.parent import Parent, ParentStudent
    
    parents = Parent.query.all()
    students = Student.query.all()
    links = ParentStudent.query.all()
    
    return render_template('admin/parent_links.html',
                         parents=parents,
                         students=students,
                         links=links)

@admin_bp.route('/parent-links/create', methods=['POST'])
@admin_required
def create_parent_link():
    """Crear vínculo padre-hijo"""
    from app.models.parent import Parent, ParentStudent
    
    data = request.form
    
    try:
        parent_id = data.get('parent_id')
        student_id = data.get('student_id')
        relationship = data.get('relationship', 'padre/madre')
        
        # Verificar que no exista
        existing = ParentStudent.query.filter_by(
            parent_id=parent_id,
            student_id=student_id
        ).first()
        
        if existing:
            flash('Este vínculo ya existe', 'warning')
            return redirect(url_for('admin.parent_links'))
        
        # Crear vínculo
        link = ParentStudent(
            parent_id=parent_id,
            student_id=student_id,
            relationship=relationship
        )
        db.session.add(link)
        db.session.commit()
        
        # ⭐ Notificar al padre
        from app.models.notification import Notification
        parent = Parent.query.get(parent_id)
        student = Student.query.get(student_id)
        
        if parent and student:
            Notification.create_notification(
                user_id=parent.user_id,
                title="Cuenta vinculada",
                message=f"Tu cuenta ha sido vinculada con el estudiante {student.user.username}",
                notification_type='info',
                student_id=student_id
            )
        
        flash('Vínculo creado exitosamente', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error al crear vínculo: {str(e)}', 'danger')
    
    return redirect(url_for('admin.parent_links'))

@admin_bp.route('/parent-links/<int:link_id>/delete', methods=['POST'])
@admin_required
def delete_parent_link(link_id):
    """Eliminar vínculo padre-hijo"""
    from app.models.parent import ParentStudent
    
    try:
        link = ParentStudent.query.get_or_404(link_id)
        db.session.delete(link)
        db.session.commit()
        
        flash('Vínculo eliminado exitosamente', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar vínculo: {str(e)}', 'danger')
    
    return redirect(url_for('admin.parent_links'))

@admin_bp.route('/reports')
@admin_required
def reports():
    """Reportes y estadísticas generales"""
    # Estadísticas por tipo de TDAH
    tdah_stats_raw = db.session.query(
        Student.tdah_type,
        db.func.count(Student.id)
    ).group_by(Student.tdah_type).all()
    
    tdah_stats = [[row[0] or 'No especificado', row[1]] for row in tdah_stats_raw]
    
    # Promedio de sesiones por estudiante
    session_counts = db.session.query(
        db.func.count(Session.id).label('count')
    ).join(Student).group_by(Student.id).all()
    
    if session_counts:
        avg_sessions = sum([count[0] for count in session_counts]) / len(session_counts)
    else:
        avg_sessions = 0
    
    # Actividades más usadas
    popular_activities_raw = db.session.query(
        Activity.title,
        Activity.activity_type,
        db.func.count(Session.id).label('usage_count')
    ).join(Session).group_by(Activity.id).order_by(
        db.desc('usage_count')
    ).limit(5).all()
    
    popular_activities = [[row[0], row[1], row[2]] for row in popular_activities_raw]
    
    return render_template('admin/reports.html',
                         tdah_stats=tdah_stats,
                         avg_sessions=round(avg_sessions, 2),
                         popular_activities=popular_activities)

@admin_bp.route('/api/stats')
@admin_required
def api_stats():
    """API para obtener estadísticas en JSON"""
    stats = {
        'users': {
            'total': User.query.count(),
            'admins': User.query.filter_by(role='admin').count(),
            'teachers': User.query.filter_by(role='teacher').count(),
            'students': User.query.filter_by(role='student').count(),
            'parents': User.query.filter_by(role='parent').count()  # ⭐ NUEVO
        },
        'activities': {
            'total': Activity.query.count(),
            'by_type': dict(
                db.session.query(
                    Activity.activity_type,
                    db.func.count(Activity.id)
                ).group_by(Activity.activity_type).all()
            )
        },
        'sessions': {
            'total': Session.query.count(),
            'avg_attention_score': db.session.query(
                db.func.avg(Session.attention_score)
            ).scalar() or 0
        }
    }
    
    return jsonify(stats)

# ============================================================
# ⭐ INSCRIPCIÓN UNIFICADA (Alumno + Padres + Vínculos)
# ============================================================

@admin_bp.route('/inscribir-alumno', methods=['GET', 'POST'])
@admin_required
def inscribir_alumno():
    """Inscribe un alumno con todos sus datos + sus tutores en un solo paso"""
    if request.method == 'GET':
        return render_template('admin/inscribir_alumno.html')
    
    data = request.form
    
    try:
        # Validaciones básicas
        username = data.get('student_username', '').strip()
        email = data.get('student_email', '').strip()
        
        if not username or not email:
            flash('Username y email del alumno son obligatorios', 'danger')
            return redirect(url_for('admin.inscribir_alumno'))
        
        if User.query.filter_by(username=username).first():
            flash(f'El username "{username}" ya está en uso', 'danger')
            return redirect(url_for('admin.inscribir_alumno'))
        
        if User.query.filter_by(email=email).first():
            flash(f'El email "{email}" ya está registrado', 'danger')
            return redirect(url_for('admin.inscribir_alumno'))
        
        # 1. Crear User del alumno
        student_user = User(
            username=username,
            email=email,
            role='student'
        )
        student_user.set_password(data.get('student_password', 'estudiante123'))
        db.session.add(student_user)
        db.session.flush()
        
        # 2. Crear Student con info completa
        age_value = data.get('student_age')
        student = Student(
            user_id=student_user.id,
            full_name=data.get('student_full_name', '').strip(),
            national_id=data.get('student_national_id', '').strip() or None,
            age=int(age_value) if age_value else None,
            grade=data.get('student_grade', '').strip() or None,
            section=data.get('student_section', '').strip() or None,
            address=data.get('student_address', '').strip() or None,
            allergies=data.get('student_allergies', '').strip() or None,
            medical_conditions=data.get('student_medical_conditions', '').strip() or None,
            medications=data.get('student_medications', '').strip() or None,
            emergency_contact_name=data.get('emergency_contact_name', '').strip() or None,
            emergency_contact_phone=data.get('emergency_contact_phone', '').strip() or None,
        )
        db.session.add(student)
        db.session.flush()
        
        # 3. Tutor Principal (obligatorio)
        if not data.get('parent1_email'):
            raise ValueError('Tutor principal es obligatorio')
        _crear_o_vincular_tutor(data, prefix='parent1', student=student)
        
        # 4. Tutor Secundario (opcional)
        if data.get('parent2_email'):
            _crear_o_vincular_tutor(data, prefix='parent2', student=student)
        
        db.session.commit()
        
        flash(f'✅ Alumno {student.get_display_name()} inscrito correctamente', 'success')
        return redirect(url_for('admin.users'))
    
    except ValueError as ve:
        db.session.rollback()
        flash(f'Error de validación: {str(ve)}', 'danger')
        return redirect(url_for('admin.inscribir_alumno'))
    except Exception as e:
        db.session.rollback()
        import traceback
        traceback.print_exc()
        flash(f'Error al inscribir alumno: {str(e)}', 'danger')
        return redirect(url_for('admin.inscribir_alumno'))


def _crear_o_vincular_tutor(data, prefix, student):
    """Helper: crea o vincula un tutor a un estudiante"""
    from app.models.parent import Parent, ParentStudent
    import secrets
    
    email = data.get(f'{prefix}_email', '').strip()
    full_name = data.get(f'{prefix}_full_name', '').strip()
    relationship = data.get(f'{prefix}_relationship', 'padre/madre')
    phone = data.get(f'{prefix}_phone', '').strip()
    whatsapp_enabled = bool(data.get(f'{prefix}_whatsapp_enabled'))
    create_account = bool(data.get(f'{prefix}_create_account'))
    
    if not email or not full_name:
        raise ValueError(f'Tutor {prefix}: nombre y email son obligatorios')
    
    # ¿Ya existe usuario con ese email?
    parent_user = User.query.filter_by(email=email).first()
    
    if parent_user:
        if parent_user.role != 'parent':
            raise ValueError(f'El email {email} pertenece a un usuario con rol {parent_user.role}')
        
        parent = Parent.query.filter_by(user_id=parent_user.id).first()
        if not parent:
            parent = Parent(
                user_id=parent_user.id,
                full_name=full_name,
                phone=phone,
                whatsapp_enabled=whatsapp_enabled,
                receive_notifications=True
            )
            db.session.add(parent)
            db.session.flush()
    else:
        # Generar username único basado en email
        base_username = email.split('@')[0].lower().replace('.', '_')
        username = base_username
        counter = 1
        while User.query.filter_by(username=username).first():
            username = f"{base_username}_{counter}"
            counter += 1
        
        parent_user = User(
            username=username,
            email=email,
            role='parent'
        )
        
        # Si pidió crear cuenta: usa password del form. Si no: random
        if create_account:
            password = data.get(f'{prefix}_password', '').strip() or 'padre123'
        else:
            password = secrets.token_urlsafe(12)
        parent_user.set_password(password)
        db.session.add(parent_user)
        db.session.flush()
        
        parent = Parent(
            user_id=parent_user.id,
            full_name=full_name,
            phone=phone,
            whatsapp_enabled=whatsapp_enabled,
            receive_notifications=True
        )
        db.session.add(parent)
        db.session.flush()
    
    # Vincular padre con estudiante (si no está ya vinculado)
    existing = ParentStudent.query.filter_by(
        parent_id=parent.id, student_id=student.id
    ).first()
    if not existing:
        link = ParentStudent(
            parent_id=parent.id,
            student_id=student.id,
            relationship=relationship
        )
        db.session.add(link)