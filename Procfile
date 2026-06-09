release: python scripts/init_db_railway.py
web: gunicorn run:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120
