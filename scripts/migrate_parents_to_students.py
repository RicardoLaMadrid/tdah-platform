"""
scripts/migrate_parents_to_students.py

Migra los datos de padres/tutores desde las tablas `parents` / `parent_student`
hacia los nuevos campos tutor_* del modelo Student.

Uso:
    cd tdah-platform
    python scripts/migrate_parents_to_students.py
"""
import os
import sys

# Agregar raíz del proyecto al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from app.extensions import db
from app.core.models.student import Student
from app.core.models.parent import Parent, ParentStudent


def run_migration():
    app = create_app('development')

    with app.app_context():
        links = ParentStudent.query.all()

        if not links:
            print("\nNo hay vínculos padre-alumno en la base de datos.")
            print("La migración no tiene nada que hacer.")
            return

        # ── Previsualización ──────────────────────────────────────────
        print("\n" + "="*60)
        print("MIGRACIÓN: datos de tutores → tabla students")
        print("="*60)
        print(f"\nVínculos encontrados: {len(links)}\n")

        rows = []
        for link in links:
            student = db.session.get(Student, link.student_id)
            parent  = db.session.get(Parent,  link.parent_id)

            if not student or not parent:
                print(f"  OMITIDO: link id={link.id} (student o parent no encontrado)")
                continue

            rows.append({
                'link': link,
                'student': student,
                'parent': parent,
            })

            print(f"  Alumno  : {student.full_name or student.user.username}")
            print(f"  Tutor   : {parent.full_name} | {link.relationship}")
            print(f"  Teléfono: {parent.phone}")
            print(f"  WhatsApp: {'Sí' if parent.whatsapp_enabled else 'No'}")
            print()

        print(f"Total a migrar: {len(rows)} vínculo(s)\n")
        print("NOTA: el tutor PRINCIPAL (primer vínculo) ocupa tutor_*.")
        print("      El tutor SECUNDARIO (si hay) ocupa tutor_secondary_*.")

        # ── Confirmación ─────────────────────────────────────────────
        confirm = input("\nEscribe SI para continuar con la migración: ").strip()
        if confirm != "SI":
            print("Migración cancelada.")
            return

        # ── Ejecutar ─────────────────────────────────────────────────
        migrated = 0
        student_seen = {}

        for row in rows:
            student = row['student']
            parent  = row['parent']
            link    = row['link']

            is_primary = student.id not in student_seen

            if is_primary:
                student.tutor_full_name       = parent.full_name
                student.tutor_relationship    = link.relationship
                student.tutor_phone           = parent.phone
                student.tutor_whatsapp_enabled = parent.whatsapp_enabled
                if parent.user:
                    student.tutor_email = parent.user.email
                student_seen[student.id] = True
            else:
                # Tutor secundario
                student.tutor_secondary_name  = parent.full_name
                student.tutor_secondary_phone = parent.phone

            migrated += 1

        db.session.commit()

        print(f"\n✓ Migración completada. {migrated} registro(s) actualizados.")
        print("\nPróximos pasos manuales en phpMyAdmin:")
        print("  1. Verificar columnas tutor_* en tabla students")
        print("  2. DROP TABLE parent_student")
        print("  3. DROP TABLE parents")
        print("  4. En tabla users: DELETE FROM users WHERE role='parent'")
        print("  (Hacer backup antes de borrar tablas)\n")


if __name__ == '__main__':
    run_migration()
