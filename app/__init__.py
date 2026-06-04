from flask import Flask, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, current_user
from flask_wtf.csrf import CSRFProtect
from config import config
import os

# Extensiones
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
csrf = CSRFProtect()

login_manager.login_view = 'auth.login'
login_manager.login_message = 'Por favor inicia sesión para acceder a esta página.'

@login_manager.user_loader
def load_user(user_id):
    from app.models.user import User
    # ✅ SQLAlchemy 2.x compatible (no deprecated)
    return db.session.get(User, int(user_id))


def create_app(config_name='development'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Inicializar extensiones
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)  # ⭐ Protección CSRF activada
    
    with app.app_context():
        # Importar modelos (necesario para Flask-Migrate)
        from app.models import user, student, activity, report, parent, notification
        
        # Ruta raíz
        @app.route('/')
        def index():
            if current_user.is_authenticated:
                role_redirects = {
                    'admin': 'admin.index',
                    'teacher': 'teacher.index',
                    'student': 'student.index',
                    'parent': 'parent.index'
                }
                endpoint = role_redirects.get(current_user.role)
                if endpoint:
                    return redirect(url_for(endpoint))
            return redirect(url_for('auth.login'))
        
        # Registrar blueprints
        _register_blueprints(app)
        
        print("\n" + "="*60)
        print("🚀 APLICACIÓN INICIALIZADA CORRECTAMENTE")
        print("="*60 + "\n")
    
    return app  # ✅ UN solo return, fuera del with


def _register_blueprints(app):
    # 1. Autenticación (CON CSRF — es público)
    from app.routes.auth import auth_bp
    app.register_blueprint(auth_bp)
    print("✅ Blueprint 'auth' registrado")
    
    # 2. OAuth
    try:
        from app.routes.oauth import oauth_bp, init_oauth
        init_oauth(app)
        csrf.exempt(oauth_bp)  # ⭐ exento
        app.register_blueprint(oauth_bp)
        print("✅ Blueprint 'oauth' registrado")
    except ImportError as e:
        print(f"⚠️  OAuth no disponible: {e}")
    
    # 3. Roles internos (exentos — protegidos por auth + role)
    from app.routes.admin import admin_bp
    csrf.exempt(admin_bp)  # ⭐ NUEVO
    app.register_blueprint(admin_bp)
    print("✅ Blueprint 'admin' registrado")
    
    from app.routes.student import student_bp
    csrf.exempt(student_bp)  # ⭐ NUEVO
    app.register_blueprint(student_bp)
    print("✅ Blueprint 'student' registrado")
    
    from app.routes.teacher import teacher_bp
    csrf.exempt(teacher_bp)  # ⭐ NUEVO
    app.register_blueprint(teacher_bp)
    print("✅ Blueprint 'teacher' registrado")
    
    # 4. Padres
    try:
        from app.routes.parent import parent_bp
        csrf.exempt(parent_bp)  # ⭐ NUEVO
        app.register_blueprint(parent_bp)
        print("✅ Blueprint 'parent' registrado")
    except ImportError as e:
        print(f"⚠️  parent_bp no cargado: {e}")
    
    # 5. AR
    try:
        from app.routes.ar import ar_bp
        csrf.exempt(ar_bp)  # ⭐ NUEVO
        app.register_blueprint(ar_bp)
        print("✅ Blueprint 'ar' registrado")
    except ImportError as e:
        print(f"⚠️  ar_bp no cargado: {e}")
    
    # 6. Tests cognitivos (ya estaban exentos)
    for module_path, bp_name in [
        ('app.services.vision', 'vision_bp'),
        ('app.services.audio_api', 'audio_bp'),
        ('app.services.stroop', 'stroop_bp'),
        ('app.services.gonogo', 'gonogo_bp'),
    ]:
        try:
            module = __import__(module_path, fromlist=[bp_name])
            blueprint = getattr(module, bp_name)
            csrf.exempt(blueprint)
            app.register_blueprint(blueprint)
            print(f"✅ Blueprint '{bp_name}' registrado")
        except (ImportError, AttributeError) as e:
            print(f"⚠️  {bp_name} no cargado: {e}")
    
    # 7. Manejadores de errores
    from flask import render_template
    
    @app.errorhandler(404)
    def not_found(e):
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def server_error(e):
        db.session.rollback()
        return render_template('errors/500.html'), 500