import os
from datetime import timedelta
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    """Configuración base"""
    # Seguridad
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-muy-secreta-123'
    
    # Base de datos
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # CORS
    CORS_ORIGIN_WHITELIST = ['http://localhost:3000']  # Frontend React
    
    # Configuración de la API
    API_TITLE = 'Solar Design System API'
    API_VERSION = 'v1'
    FRONTEND_URL = os.environ.get('FRONTEND_URL', 'http://localhost:3000')
    
    # Límites de tamaño para uploads
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    
    # Configuración de JWT
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'dev-jwt-key-123')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    
    # Configuración de correo electrónico
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() == 'true'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', 'noreply@solardesign.com')
    
    # Configuración de rate limiting
    RATELIMIT_DEFAULT = "200 per day;50 per hour"
    RATELIMIT_STRATEGY = "fixed-window"
    RATELIMIT_STORAGE_URL = "memory://"
    
    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    """Configuración de desarrollo"""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'solar_design_dev.db')
    
    # Configuración de CORS más permisiva para desarrollo
    CORS_ORIGIN_WHITELIST = ['*']

class TestingConfig(Config):
    """Configuración de pruebas"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'solar_design_test.db')
    
    # Desactivar CSRF para pruebas
    WTF_CSRF_ENABLED = False

class ProductionConfig(Config):
    """Configuración de producción"""
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'solar_design.db')
    
    # Configuraciones de seguridad adicionales
    @staticmethod
    def init_app(app):
        Config.init_app(app)
        
        # Registro de errores en producción
        import logging
        from logging.handlers import RotatingFileHandler
        
        if not os.path.exists('logs'):
            os.mkdir('logs')
        
        file_handler = RotatingFileHandler(
            'logs/solar_design.log',
            maxBytes=10240,
            backupCount=10
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s '
            '[in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('Solar Design System startup')

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
