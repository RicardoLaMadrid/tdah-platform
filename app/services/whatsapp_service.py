"""
Servicio de envío de WhatsApp via Twilio.
Para producción, requiere cuenta de Twilio y aprobación de WhatsApp Business.
Para desarrollo, usa el Twilio Sandbox.
Requiere: pip install twilio
"""
from flask import current_app

def send_whatsapp_message(to_phone, message):
    """
    Envía un mensaje de WhatsApp a un número.
    
    Args:
        to_phone: número en formato '+591XXXXXXXX' o 'whatsapp:+591XXXXXXXX'
        message: texto a enviar
    
    Returns:
        bool: True si se envió, False si falló o está deshabilitado
    """
    if not current_app.config.get('WHATSAPP_ENABLED', False):
        print(f"📱 [WhatsApp DESHABILITADO] Mensaje no enviado a {to_phone}")
        return False
    
    account_sid = current_app.config.get('TWILIO_ACCOUNT_SID')
    auth_token = current_app.config.get('TWILIO_AUTH_TOKEN')
    from_whatsapp = current_app.config.get('TWILIO_WHATSAPP_FROM')
    
    if not account_sid or not auth_token:
        print("⚠️  Twilio credentials faltantes")
        return False
    
    try:
        from twilio.rest import Client
        client = Client(account_sid, auth_token)
        
        # Formatear número destinatario
        if not to_phone.startswith('whatsapp:'):
            # Limpiar número (quitar espacios, guiones)
            clean = ''.join(c for c in to_phone if c.isdigit() or c == '+')
            if not clean.startswith('+'):
                clean = '+591' + clean  # Default Bolivia, ajusta según país
            to_whatsapp = f'whatsapp:{clean}'
        else:
            to_whatsapp = to_phone
        
        msg = client.messages.create(
            from_=from_whatsapp,
            body=message,
            to=to_whatsapp
        )
        
        print(f"✅ WhatsApp enviado a {to_whatsapp}, SID: {msg.sid}")
        return True
    
    except ImportError:
        print("❌ Twilio no instalado. Ejecuta: pip install twilio")
        return False
    except Exception as e:
        print(f"❌ Error enviando WhatsApp a {to_phone}: {e}")
        return False