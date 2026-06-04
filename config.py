import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Básico
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Base de datos MySQL
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'mysql+pymysql://root@localhost/tdah_platform'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # OpenAI
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    AI_MODEL = os.environ.get('AI_MODEL', 'gpt-4o-mini')
    AI_MAX_TOKENS = int(os.environ.get('AI_MAX_TOKENS', 2000))
    AI_TEMPERATURE = float(os.environ.get('AI_TEMPERATURE', 0.7))
    
    # JWT (legacy - solo si decides usar API)
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-key'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    
    # Whisper
    WHISPER_MODEL = 'base'
    
    # Archivos
    UPLOAD_FOLDER = 'app/static/uploads'
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024
    ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'mp3', 'wav', 'webm'}
    
    # OpenCV
    HEATMAP_COLORMAP = 'COLORMAP_JET'
    VIDEO_FPS = 30
    
    # AR
    AR_MARKER_SIZE = 0.05
    
    # ============================================================
    # ⭐ CONSTANTES DEL ALGORITMO TDAH (centralizadas)
    # ============================================================
    TDAH_MIN_CONFIDENCE = int(os.environ.get('TDAH_MIN_CONFIDENCE', 50))
    TDAH_MIN_TESTS = int(os.environ.get('TDAH_MIN_TESTS', 2))
    TDAH_REEVAL_DAYS = int(os.environ.get('TDAH_REEVAL_DAYS', 30))
    
    # ============================================================
    # ⭐ GOOGLE OAUTH (login con Gmail)
    # ============================================================
    GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')
    GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET')
    GOOGLE_DISCOVERY_URL = (
        "https://accounts.google.com/.well-known/openid-configuration"
    )
    
    # ============================================================
    # ⭐ TWILIO / WHATSAPP (notificaciones a padres)
    # ============================================================
    TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID')
    TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN')
    TWILIO_WHATSAPP_FROM = os.environ.get('TWILIO_WHATSAPP_FROM', 'whatsapp:+14155238886')
    WHATSAPP_ENABLED = os.environ.get('WHATSAPP_ENABLED', 'False').lower() == 'true'
    
    # Sesiones (Flask)
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)


class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    DEBUG = False
    TESTING = False
    SESSION_COOKIE_SECURE = True  # HTTPS only en producción
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://test:test@localhost/tdah_test'


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}