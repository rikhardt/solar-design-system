from flask_jwt_extended import JWTManager
from flask_mail import Mail
from .models import User, UserActivity, PasswordReset
from .routes import auth
from .utils import (
    validate_password_strength, 
    generate_password_reset_token,
    send_password_reset_email,
    is_safe_url,
    require_role,
    login_limiter,
    reset_limiter
)

jwt = JWTManager()
mail = Mail()

def init_app(app):
    """Inicializar el módulo de autenticación"""
    jwt.init_app(app)
    mail.init_app(app)
    app.register_blueprint(auth)

    # Configurar handler para tokens expirados
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return {
            'error': 'Token has expired',
            'message': 'Please log in again'
        }, 401

    # Configurar handler para tokens inválidos
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return {
            'error': 'Invalid token',
            'message': 'Token verification failed'
        }, 401

    # Configurar handler para tokens faltantes
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return {
            'error': 'Authorization required',
            'message': 'Token is missing'
        }, 401

__all__ = [
    'jwt',
    'mail',
    'User',
    'UserActivity',
    'PasswordReset',
    'auth',
    'validate_password_strength',
    'generate_password_reset_token',
    'send_password_reset_email',
    'is_safe_url',
    'require_role',
    'login_limiter',
    'reset_limiter'
]
