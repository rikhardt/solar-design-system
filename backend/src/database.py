from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def init_db(app):
    """Inicializa la base de datos con la aplicación Flask"""
    db.init_app(app)
    
    with app.app_context():
        # Importar todos los modelos aquí para asegurar que SQLAlchemy los conozca
        from src.modules.components.models import ShadowAnalysis
        
        # Crear todas las tablas
        db.create_all()
