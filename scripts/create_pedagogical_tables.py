"""Crea las tablas pedagogical_sessions y session_results.

El proyecto no tiene carpeta migrations/ (flask-migrate esta inicializado
en la app pero nunca se corrio `flask db init`), asi que en vez de generar
un arbol de migraciones completo usamos create_all, que solo crea las
tablas que faltan y no toca las existentes.

    python scripts/create_pedagogical_tables.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import inspect

from app import create_app
from app.extensions import db

TARGET_TABLES = ['pedagogical_sessions', 'session_results']


def main():
    app = create_app(os.environ.get('FLASK_CONFIG', 'development'))
    with app.app_context():
        inspector = inspect(db.engine)
        before = set(inspector.get_table_names())

        faltantes = [t for t in TARGET_TABLES if t not in before]
        if not faltantes:
            print('Las tablas ya existen, no hay nada que crear:', ', '.join(TARGET_TABLES))
            return 0

        print('Tablas a crear:', ', '.join(faltantes))
        db.create_all()

        after = set(inspect(db.engine).get_table_names())
        creadas = sorted(after - before)
        print('Creadas:', ', '.join(creadas) if creadas else '(ninguna)')

        for t in TARGET_TABLES:
            cols = [c['name'] for c in inspect(db.engine).get_columns(t)]
            print(f'  {t}: {len(cols)} columnas -> {", ".join(cols)}')

    return 0


if __name__ == '__main__':
    raise SystemExit(main())
