from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_mail import Mail
from config import config

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
mail = Mail()

def create_app(config_name='default'):
    """Función factory para crear la aplicación Flask"""
    app = Flask(__name__)
    
    # Configuración
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    
    # Inicializar extensiones
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    mail.init_app(app)
    CORS(app)
    
    # Registrar blueprints
    from .modules.components import components
    app.register_blueprint(components, url_prefix='/api/components')

    from .modules.auth import auth, init_app as init_auth
    app.register_blueprint(auth, url_prefix='/auth')
    
    from .modules.projects import projects
    app.register_blueprint(projects, url_prefix='/projects')
    
    # Registrar manejadores de error
    @app.errorhandler(400)
    def bad_request(e):
        return {
            'error': 'Bad Request',
            'message': str(e.description)
        }, 400

    @app.errorhandler(404)
    def not_found(e):
        return {
            'error': 'Not Found',
            'message': 'El recurso solicitado no existe'
        }, 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return {
            'error': 'Internal Server Error',
            'message': 'Ha ocurrido un error interno en el servidor'
        }, 500
    
    return app
