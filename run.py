import os
from app import create_app, db


def get_config_name():
    # Railway inyecta RAILWAY_ENVIRONMENT en todos los deploys
    if os.environ.get('RAILWAY_ENVIRONMENT'):
        return 'production'
    return os.environ.get('FLASK_ENV', 'development')
from app.core.models.user import User
from app.core.models.student import Student
from app.core.models.activity import Activity, Session
from app.core.models.report import Report

# Crear la aplicación — detecta Railway automáticamente
app = create_app(get_config_name())

@app.shell_context_processor
def make_shell_context():
    """Contexto para flask shell"""
    return {
        'db': db,
        'User': User,
        'Student': Student,
        'Activity': Activity,
        'Session': Session,
        'Report': Report
    }

@app.cli.command()
def init_db():
    """Inicializar la base de datos"""
    db.create_all()
    print("✅ Base de datos inicializada")

@app.cli.command()
def create_admin():
    """Crear usuario administrador"""
    admin = User.query.filter_by(username='admin').first()
    
    if admin:
        print("⚠️  Usuario admin ya existe")
        return
    
    admin = User(
        username='admin',
        email='admin@tdahplatform.com',
        role='admin'
    )
    admin.set_password('admin123')
    
    db.session.add(admin)
    db.session.commit()
    
    print("✅ Usuario admin creado")
    print("   Username: admin")
    print("   Password: admin123")

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)