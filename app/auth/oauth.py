"""
Login con Google OAuth
Requiere: pip install Authlib
Variables de entorno: GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET
"""
from flask import Blueprint, redirect, url_for, flash, current_app, session
from flask_login import login_user, current_user
from authlib.integrations.flask_client import OAuth
from app.extensions import db
from app.models.user import User

oauth_bp = Blueprint('oauth', __name__, url_prefix='/oauth')
oauth = OAuth()


def init_oauth(app):
    """Inicializa OAuth con la app de Flask"""
    oauth.init_app(app)
    
    client_id = app.config.get('GOOGLE_CLIENT_ID')
    client_secret = app.config.get('GOOGLE_CLIENT_SECRET')
    
    if not client_id or not client_secret:
        print("⚠️  Google OAuth no configurado (faltan GOOGLE_CLIENT_ID/SECRET)")
        return
    
    oauth.register(
        name='google',
        client_id=client_id,
        client_secret=client_secret,
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
        client_kwargs={'scope': 'openid email profile'}
    )
    print("✅ Google OAuth configurado")


@oauth_bp.route('/google/login')
def google_login():
    """Inicia el flow de login con Google"""
    if current_user.is_authenticated:
        return redirect(url_for('auth.dashboard'))
    
    if not oauth.google:
        flash('Login con Google no está disponible. Contacta al administrador.', 'warning')
        return redirect(url_for('auth.login'))
    
    redirect_uri = url_for('oauth.google_callback', _external=True)
    return oauth.google.authorize_redirect(redirect_uri)


@oauth_bp.route('/google/callback')
def google_callback():
    """Callback después de que Google autoriza"""
    try:
        token = oauth.google.authorize_access_token()
        userinfo = token.get('userinfo')
        
        if not userinfo:
            flash('No se pudo obtener tu información de Google.', 'danger')
            return redirect(url_for('auth.login'))
        
        email = userinfo.get('email')
        name = userinfo.get('name', email.split('@')[0])
        
        if not email:
            flash('Google no proporcionó un email válido.', 'danger')
            return redirect(url_for('auth.login'))
        
        # Buscar usuario por email
        user = User.query.filter_by(email=email).first()
        
        if not user:
            # ⭐ Política: NO crear cuentas automáticamente desde Google
            # El admin debe haber creado al usuario previamente con ese email
            flash(
                f'No existe una cuenta para {email}. '
                'Pide al administrador que te cree una cuenta primero, luego podrás iniciar sesión con Google.',
                'warning'
            )
            return redirect(url_for('auth.login'))
        
        # Login exitoso
        login_user(user, remember=True)
        flash(f'¡Bienvenido, {user.username}! (vía Google)', 'success')
        return redirect(url_for('auth.dashboard'))
    
    except Exception as e:
        print(f"❌ Error en Google OAuth: {e}")
        import traceback
        traceback.print_exc()
        flash('Hubo un error al iniciar sesión con Google.', 'danger')
        return redirect(url_for('auth.login'))