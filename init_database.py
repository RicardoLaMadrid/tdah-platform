"""
Script de inicialización completa de la base de datos
Ejecutar con: python init_database.py
"""

import os
import sys
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models.user import User
from app.models.student import Student
from app.models.activity import Activity, Session
from app.models.report import Report

def init_database():
    """Inicializar base de datos"""
    print("=" * 50)
    print("INICIALIZANDO BASE DE DATOS")
    print("=" * 50)
    
    app = create_app('development')
    
    with app.app_context():
        # Crear todas las tablas
        print("\n✓ Creando tablas...")
        db.create_all()
        print("  Tablas creadas exitosamente")
        
        # Verificar si ya hay datos
        if User.query.count() > 0:
            print("\n⚠️  La base de datos ya tiene datos")
            response = input("¿Deseas eliminar todo y empezar de nuevo? (s/n): ")
            if response.lower() == 's':
                print("  Eliminando datos existentes...")
                db.drop_all()
                db.create_all()
                print("  Base de datos limpia")
            else:
                print("  Operación cancelada")
                return
        
        # Crear administrador
        print("\n✓ Creando usuarios...")
        admin = User(
            username='admin',
            email='admin@tdahplatform.com',
            role='admin'
        )
        admin.set_password('admin123')
        db.session.add(admin)
        print("  - Administrador: admin / admin123")
        
        # Profesores
        teachers = []
        for i in range(1, 4):
            teacher = User(
                username=f'teacher{i}',
                email=f'teacher{i}@demo.com',
                role='teacher'
            )
            teacher.set_password('teacher123')
            db.session.add(teacher)
            teachers.append(teacher)
        
        db.session.flush()
        print("  - 3 Profesores creados: teacher1-3 / teacher123")
        
        # Estudiantes
        student_names = ['carlos', 'lucia', 'miguel', 'sofia', 'diego', 'emma']
        tdah_types = ['inatento', 'hiperactivo', 'combinado']
        
        students = []
        for i, name in enumerate(student_names):
            student_user = User(
                username=name,
                email=f'{name}@estudiante.com',
                role='student'
            )
            student_user.set_password('student123')
            db.session.add(student_user)
            db.session.flush()
            
            student_profile = Student(
                user_id=student_user.id,
                teacher_id=teachers[i % 3].id,
                age=8 + (i % 4),
                tdah_type=tdah_types[i % 3]
            )
            db.session.add(student_profile)
            students.append(student_profile)
        
        db.session.flush()
        print(f"  - {len(student_names)} Estudiantes creados / student123")
        
        # Actividades
        print("\n✓ Creando actividades...")
        activities_data = [
            {
                'title': 'Encuentra las Diferencias AR',
                'description': 'Juego de atención visual con realidad aumentada',
                'activity_type': 'atencion',
                'difficulty_level': 2,
                'instructions': '1. Escanea el entorno\n2. Toca los objetos\n3. Encuentra diferencias',
                'ar_content': {'enabled': True, 'type': 'markerless'}
            },
            {
                'title': 'Secuencia de Colores',
                'description': 'Memoriza y repite secuencias',
                'activity_type': 'memoria',
                'difficulty_level': 1,
                'instructions': '1. Observa\n2. Memoriza\n3. Repite',
                'ar_content': {'enabled': False}
            },
        ]
        
        for i, act_data in enumerate(activities_data):
            student = students[i % len(students)]
            activity = Activity(
                student_id=student.id,
                teacher_id=student.teacher_id,
                **act_data
            )
            db.session.add(activity)
        
        print(f"  - {len(activities_data)} Actividades creadas")
        
        db.session.commit()
        
        print("\n" + "=" * 50)
        print("✅ INICIALIZACIÓN COMPLETADA")
        print("=" * 50)
        print("\n📋 CREDENCIALES:")
        print("  Admin: admin / admin123")
        print("  Profesores: teacher1-3 / teacher123")
        print("  Estudiantes: carlos, lucia, etc. / student123")
        print("\n🌐 Ejecuta: python run.py")
        print("  http://localhost:5000")

if __name__ == '__main__':
    try:
        init_database()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()