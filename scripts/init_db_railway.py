"""
scripts/init_db_railway.py — Inicialización de BD para Railway.

El Procfile ejecuta este script como comando `release` antes de
levantar el servidor web. Crea las tablas y hace seed si la BD está vacía.
"""
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, PROJECT_ROOT)


def init_db():
    from app import create_app
    from app.extensions import db

    app = create_app('production')

    with app.app_context():
        print("=" * 60)
        print("  Railway — Inicialización de base de datos")
        print("=" * 60)

        db.create_all()
        print("  Tablas creadas / verificadas.")

        from app.core.models.user import User
        admin_count = User.query.filter_by(role='admin').count()

        if admin_count == 0:
            print("  BD vacía — ejecutando seed de datos demo...")
            _run_seed()
            print("  Seed completado.")
        else:
            print(f"  BD ya tiene datos ({admin_count} admin(s)). Nada que hacer.")

        print("=" * 60)


def _run_seed():
    # Llama a seed_demo.main() simulando los flags --yes (sin prompts interactivos)
    old_argv = sys.argv[:]
    sys.argv = ['seed_demo', '--yes']
    try:
        from scripts.seed_demo import main
        main()
    finally:
        sys.argv = old_argv


def run_seed(app):
    """Punto de entrada para ser llamado desde app/__init__.py con app ya creada."""
    with app.app_context():
        _run_seed()


if __name__ == '__main__':
    init_db()
