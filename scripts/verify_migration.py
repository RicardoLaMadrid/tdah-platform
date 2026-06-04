"""
scripts/verify_migration.py

Verifica que la migración de datos padre→tutor fue correcta.
Ejecutar DESPUÉS de migrate_parents_to_students.py.

Uso:
    python scripts/verify_migration.py
"""
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from app.extensions import db
from app.core.models.student import Student
from app.core.models.user import User

SEP = "=" * 60

def run():
    app = create_app('development')
    with app.app_context():
        print(f"\n{SEP}")
        print("VERIFICACIÓN POST-MIGRACIÓN")
        print(SEP)

        # ── Conteos generales ────────────────────────────────────────
        total_students  = Student.query.count()
        # Criterio: tutor_phone (los padres demo no tenían full_name cargado)
        with_tutor      = Student.query.filter(Student.tutor_phone.isnot(None)).count()
        without_tutor   = total_students - with_tutor

        # Intentar contar parents (tabla puede ya no existir)
        try:
            parent_count = db.session.execute(
                db.text("SELECT COUNT(*) FROM parents")
            ).scalar()
        except Exception:
            parent_count = "tabla 'parents' no existe"

        try:
            parent_student_count = db.session.execute(
                db.text("SELECT COUNT(*) FROM parent_student")
            ).scalar()
        except Exception:
            parent_student_count = "tabla 'parent_student' no existe"

        try:
            parent_users = db.session.execute(
                db.text("SELECT COUNT(*) FROM users WHERE role='parent'")
            ).scalar()
        except Exception:
            parent_users = "rol 'parent' no existe"

        print(f"\n{'Tabla':30} {'Filas':>8}")
        print("-" * 40)
        print(f"{'students (total)':30} {total_students:>8}")
        print(f"{'students con tutor_full_name':30} {with_tutor:>8}")
        print(f"{'students SIN tutor (huérfanos)':30} {without_tutor:>8}")
        print(f"{'parents':30} {str(parent_count):>8}")
        print(f"{'parent_student':30} {str(parent_student_count):>8}")
        print(f"{'users con role=parent':30} {str(parent_users):>8}")

        # ── Estudiantes huérfanos ────────────────────────────────────
        orphans = Student.query.filter(Student.tutor_phone.is_(None)).all()
        if orphans:
            print(f"\nESTUDIANTES SIN TUTOR ({len(orphans)}):")
            print("-" * 40)
            for s in orphans:
                name = s.full_name or (s.user.username if s.user else f"id={s.id}")
                print(f"  ✗  {name} (student.id={s.id})")
        else:
            print("\n Todos los estudiantes tienen tutor asignado.")

        # ── Sample de 3 students con datos tutor ────────────────────
        samples = Student.query.filter(Student.tutor_phone.isnot(None)).limit(3).all()
        if samples:
            print(f"\nMUESTRA DE MIGRACIÓN (primeros {len(samples)} alumnos con tutor):")
            print("-" * 40)
            for s in samples:
                print(f"  Alumno  : {s.full_name or s.user.username}")
                print(f"  Tutor   : {s.tutor_full_name} ({s.tutor_relationship})")
                print(f"  Teléfono: {s.tutor_phone}")
                print(f"  Email   : {s.tutor_email}")
                print(f"  WhatsApp: {'Habilitado' if s.tutor_whatsapp_enabled else 'Deshabilitado'}")
                if s.tutor_secondary_name:
                    print(f"  Tutor 2 : {s.tutor_secondary_name} — {s.tutor_secondary_phone}")
                print()

        # ── Integridad del servidor ──────────────────────────────────
        print(f"\n{'INTEGRIDAD':30}")
        print("-" * 40)
        total_users    = User.query.count()
        total_admins   = User.query.filter_by(role='admin').count()
        total_teachers = User.query.filter_by(role='teacher').count()
        total_stud_u   = User.query.filter_by(role='student').count()
        print(f"  users totales   : {total_users}")
        print(f"  admins          : {total_admins}")
        print(f"  teachers        : {total_teachers}")
        print(f"  students (users): {total_stud_u}")
        print()

        if without_tutor == 0:
            print("RESULTADO: Migración EXITOSA — sin estudiantes huérfanos.")
        else:
            print(f"ADVERTENCIA: {without_tutor} estudiante(s) sin tutor asignado.")
            print("  Revisar la lista de huérfanos y asignar tutor manualmente.")

        print(f"\n{SEP}\n")

if __name__ == '__main__':
    run()
