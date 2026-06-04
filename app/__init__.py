from flask import Flask, redirect, url_for
import os
from flask_login import current_user
from config import config
from app.extensions import db, migrate, login_manager, csrf


@login_manager.user_loader
def load_user(user_id):
    from app.core.models.user import User
    return db.session.get(User, int(user_id))


def create_app(config_name='development'):
    from jinja2 import ChoiceLoader, FileSystemLoader
    app = Flask(__name__)
    # Agrega shared/templates como directorio adicional de plantillas
    shared_tpl = os.path.join(os.path.dirname(__file__), 'shared', 'templates')
    # shared/templates primero: base.html, macros y layouts Tailwind
    app.jinja_loader = ChoiceLoader([FileSystemLoader(shared_tpl), app.jinja_loader])
    app.config.from_object(config[config_name])

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)

    with app.app_context():
        # Importar modelos para que Flask-Migrate los detecte
        from app.core.models import user, student, activity, report, parent, notification, badge

        @app.route('/')
        def index():
            if current_user.is_authenticated:
                role_redirects = {
                    'admin': 'admin.index',
                    'teacher': 'teacher.index',
                    'student': 'student.index',
                }
                endpoint = role_redirects.get(current_user.role)
                if endpoint:
                    return redirect(url_for(endpoint))
            return redirect(url_for('auth.login'))

        _register_blueprints(app)

        print("\n" + "="*60)
        print("APLICACION INICIALIZADA CORRECTAMENTE")
        print("="*60 + "\n")

    return app


def _register_blueprints(app):
    from app.auth.routes import auth_bp
    app.register_blueprint(auth_bp)

    try:
        from app.auth.oauth import oauth_bp, init_oauth
        init_oauth(app)
        csrf.exempt(oauth_bp)
        app.register_blueprint(oauth_bp)
    except ImportError:
        pass

    from app.admin.routes import admin_bp
    csrf.exempt(admin_bp)
    app.register_blueprint(admin_bp)

    from app.student.routes import student_bp
    csrf.exempt(student_bp)
    app.register_blueprint(student_bp)

    from app.teacher.routes import teacher_bp
    csrf.exempt(teacher_bp)
    app.register_blueprint(teacher_bp)

    try:
        from app.ar.routes import ar_bp
        csrf.exempt(ar_bp)
        app.register_blueprint(ar_bp)
    except ImportError:
        pass

    for module_path, bp_name in [
        ('app.assessments.vision.routes', 'vision_bp'),
        ('app.assessments.audio.routes', 'audio_bp'),
        ('app.assessments.stroop.routes', 'stroop_bp'),
        ('app.assessments.gonogo.routes', 'gonogo_bp'),
    ]:
        try:
            module = __import__(module_path, fromlist=[bp_name])
            blueprint = getattr(module, bp_name)
            csrf.exempt(blueprint)
            app.register_blueprint(blueprint)
        except (ImportError, AttributeError):
            pass

    from flask import render_template

    @app.errorhandler(404)
    def not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def server_error(e):
        db.session.rollback()
        return render_template('errors/500.html'), 500
