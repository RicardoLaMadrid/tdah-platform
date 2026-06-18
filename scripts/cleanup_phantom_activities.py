"""
Script para limpiar actividades fantasma creadas durante testing.
Identifica actividades con campos vacíos o títulos conocidos de prueba.
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.extensions import db
from app.core.models.activity import Activity


PHANTOM_TITLES = [
    'Cazadores de Palabras Ocultas',
]


def cleanup(yes=False):
    app = create_app()
    with app.app_context():
        candidates = Activity.query.filter(
            db.or_(
                Activity.title == '',
                Activity.title.is_(None),
                Activity.title.in_(PHANTOM_TITLES),
                Activity.description == '',
                Activity.instructions == '',
            )
        ).all()

        print(f"Encontradas {len(candidates)} actividades fantasma:")
        for a in candidates:
            label = (a.title[:50] if a.title else '(vacio)')
            fecha = a.created_at.strftime('%Y-%m-%d %H:%M') if a.created_at else 'sin fecha'
            print(f"  - ID {a.id}: '{label}' -- {fecha}")

        if not candidates:
            print("Nada que limpiar.")
            return

        if not yes:
            confirm = input(f"\nBorrar las {len(candidates)} actividades? (s/N): ")
            yes = confirm.strip().lower() == 's'

        if yes:
            for a in candidates:
                db.session.delete(a)
            db.session.commit()
            print(f"OK: {len(candidates)} actividades fantasma eliminadas.")
        else:
            print("Cancelado.")


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--yes', '-y', action='store_true', help='Confirmar sin prompt')
    args = parser.parse_args()
    cleanup(yes=args.yes)
