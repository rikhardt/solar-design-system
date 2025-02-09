import re
import uuid
from datetime import datetime
from flask import current_app, render_template
from flask_mail import Message
from src import mail

def validate_password_strength(password):
    """
    Validar que la contraseña cumpla con los requisitos mínimos de seguridad:
    - Al menos 8 caracteres
    - Al menos una letra mayúscula
    - Al menos una letra minúscula
    - Al menos un número
    - Al menos un carácter especial
    """
    if len(password) < 8:
        return False
    
    if not re.search(r"[A-Z]", password):
        return False
    
    if not re.search(r"[a-z]", password):
        return False
    
    if not re.search(r"\d", password):
        return False
    
    if not re.search(r"[ !@#$%&'()*+,-./[\\\]^_`{|}~"+r'"]', password):
        return False
    
    return True

def generate_password_reset_token():
    """Generar token único para restablecimiento de contraseña"""
    return str(uuid.uuid4())

def send_password_reset_email(email, token):
    """
    Enviar correo electrónico con link para restablecer contraseña
    
    Args:
        email (str): Correo electrónico del usuario
        token (str): Token de restablecimiento generado
    """
    reset_url = f"{current_app.config['FRONTEND_URL']}/reset-password?token={token}"
    
    msg = Message(
        'Restablecimiento de Contraseña - Solar Design System',
        sender=current_app.config['MAIL_DEFAULT_SENDER'],
        recipients=[email]
    )
    
    msg.html = render_template(
        'email/reset_password.html',
        reset_url=reset_url,
        expiry_hours=24
    )
    
    mail.send(msg)

def is_safe_url(target):
    """
    Validar que una URL de redirección es segura
    
    Args:
        target (str): URL a validar
        
    Returns:
        bool: True si la URL es segura, False en caso contrario
    """
    from urllib.parse import urlparse, urljoin
    from flask import request
    
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and \
           ref_url.netloc == test_url.netloc

class RateLimiter:
    """
    Limitador de tasa simple basado en memoria
    Usado para prevenir ataques de fuerza bruta en endpoints sensibles
    """
    def __init__(self, max_attempts=5, window_seconds=300):
        self.max_attempts = max_attempts
        self.window_seconds = window_seconds
        self._attempts = {}
    
    def is_allowed(self, key):
        """
        Verificar si una operación está permitida para una clave dada
        
        Args:
            key (str): Identificador único (ej: IP + endpoint)
            
        Returns:
            bool: True si la operación está permitida, False en caso contrario
        """
        now = datetime.utcnow()
        
        # Limpiar intentos antiguos
        self._cleanup(now)
        
        # Obtener intentos para la clave
        attempts = self._attempts.get(key, [])
        
        # Verificar número de intentos en la ventana de tiempo
        recent_attempts = [
            ts for ts in attempts
            if (now - ts).total_seconds() < self.window_seconds
        ]
        
        if len(recent_attempts) >= self.max_attempts:
            return False
        
        # Registrar nuevo intento
        recent_attempts.append(now)
        self._attempts[key] = recent_attempts
        
        return True
    
    def _cleanup(self, now):
        """Eliminar intentos antiguos para liberar memoria"""
        for key in list(self._attempts.keys()):
            attempts = self._attempts[key]
            valid_attempts = [
                ts for ts in attempts
                if (now - ts).total_seconds() < self.window_seconds
            ]
            
            if valid_attempts:
                self._attempts[key] = valid_attempts
            else:
                del self._attempts[key]

# Instancia global del limitador de tasa
login_limiter = RateLimiter(max_attempts=5, window_seconds=300)  # 5 intentos cada 5 minutos
reset_limiter = RateLimiter(max_attempts=3, window_seconds=3600)  # 3 intentos cada hora

def require_role(role):
    """
    Decorador para requerir un rol específico en una ruta
    
    Args:
        role (str): Rol requerido ('admin', 'engineer', 'user')
        
    Returns:
        function: Decorador que verifica el rol del usuario
    """
    from functools import wraps
    from flask_jwt_extended import get_jwt
    from flask import jsonify
    
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            claims = get_jwt()
            if claims.get('role') != role:
                return jsonify({
                    'error': f'{role.capitalize()} privileges required'
                }), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator
