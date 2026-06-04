from flask import url_for
from flask_login import current_user


def register_context_processors(app):
    @app.context_processor
    def inject_helpers():
        def home_url():
            if not current_user.is_authenticated:
                return url_for('auth.login')
            role_map = {
                'admin':   'admin.index',
                'teacher': 'teacher.index',
                'student': 'student.index',
            }
            endpoint = role_map.get(current_user.role, 'auth.login')
            return url_for(endpoint)

        return {'home_url': home_url}
