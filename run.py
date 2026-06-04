import os
from app import create_app, db
from app.models.user import User
from app.models.student import Student
from app.models.activity import Activity, Session
from app.models.report import Report

# Crear la aplicación
app = create_app(os.getenv('FLASK_ENV', 'development'))

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