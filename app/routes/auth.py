from flask import Blueprint, request, render_template, redirect, url_for, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from app.models.user import User
from app.models.student import Student
from app import db
from datetime import timedelta
from functools import wraps

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


def role_required(*roles):
    def decorator(f):
        @wraps(f)
        @login_required
        def decorated_function(*args, **kwargs):
            if current_user.role not in roles:
                flash('No tienes permiso para acceder a esta página.', 'danger')
                return redirect(url_for('auth.dashboard'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator


@auth_bp.route('/register', methods=['GET'])
def register():
    """El registro público está deshabilitado. Solo admin crea usuarios."""
    return render_template('auth/register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('auth.dashboard'))
    
    if request.method == 'GET':
        return render_template('auth/login.html')
    
    # POST
    username_or_email = request.form.get('username', '').strip()
    password = request.form.get('password', '')
    remember = bool(request.form.get('remember'))
    
    if not username_or_email or not password:
        flash('Usuario/Email y contraseña son requeridos.', 'danger')
        return redirect(url_for('auth.login'))
    
    # Buscar por username o email
    user = User.query.filter(
        (User.username == username_or_email) | (User.email == username_or_email)
    ).first()
    
    if not user or not user.check_password(password):
        flash('Credenciales inválidas.', 'danger')
        return redirect(url_for('auth.login'))
    
    if not user.role or user.role.strip() == '':
        flash('Usuario sin rol asignado. Contacta al administrador.', 'danger')
        return redirect(url_for('auth.login'))
    
    # ✅ Login con "remember me" real
    login_user(user, remember=remember, duration=timedelta(days=30) if remember else None)
    
    flash(f'¡Bienvenido, {user.username}!', 'success')
    return redirect(url_for('auth.dashboard'))


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Sesión cerrada correctamente.', 'info')
    return redirect(url_for('auth.login'))


@auth_bp.route('/dashboard')
@login_required
def dashboard():
    role_redirects = {
        'admin': 'admin.index',
        'teacher': 'teacher.index',
        'student': 'student.index',
        'parent': 'parent.index'
    }
    endpoint = role_redirects.get(current_user.role)
    if endpoint:
        return redirect(url_for(endpoint))
    flash('Rol no reconocido.', 'danger')
    return redirect(url_for('auth.logout'))


@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'GET':
        return render_template('auth/profile.html')
    
    try:
        new_email = request.form.get('email', '').strip()
        new_password = request.form.get('password', '').strip()
        
        if new_email and new_email != current_user.email:
            # Verificar que el email no esté tomado
            existing = User.query.filter_by(email=new_email).first()
            if existing and existing.id != current_user.id:
                flash('Ese email ya está registrado.', 'danger')
                return redirect(url_for('auth.profile'))
            current_user.email = new_email
        
        if new_password:
            if len(new_password) < 6:
                flash('La contraseña debe tener al menos 6 caracteres.', 'warning')
                return redirect(url_for('auth.profile'))
            current_user.set_password(new_password)
        
        db.session.commit()
        flash('Perfil actualizado correctamente.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al actualizar perfil: {str(e)}', 'danger')
    
    return redirect(url_for('auth.profile'))