from datetime import datetime
from src import db

class Project(db.Model):
    """Modelo para proyectos fotovoltaicos"""
    __tablename__ = 'projects'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    location = db.Column(db.JSON)  # {lat, lon, address, city, country}
    system_size = db.Column(db.Float)  # kWp
    type = db.Column(db.String(50))  # residencial, comercial, industrial, utility
    status = db.Column(db.String(20), default='draft')  # draft, active, completed
    
    # Relaciones con componentes
    panels = db.Column(db.JSON)  # Lista de IDs de paneles y cantidades
    inverters = db.Column(db.JSON)  # Lista de IDs de inversores y cantidades
    batteries = db.Column(db.JSON)  # Lista de IDs de baterías y cantidades
    mounting = db.Column(db.JSON)  # Configuración de montaje
    
    # Fechas
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    estimated_completion = db.Column(db.DateTime)
    
    # Relaciones
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'location': self.location,
            'system_size': self.system_size,
            'type': self.type,
            'status': self.status,
            'components': {
                'panels': self.panels,
                'inverters': self.inverters,
                'batteries': self.batteries,
                'mounting': self.mounting
            },
            'dates': {
                'created': self.created_at.isoformat(),
                'updated': self.updated_at.isoformat(),
                'estimated_completion': self.estimated_completion.isoformat() if self.estimated_completion else None
            },
            'owner_id': self.owner_id
        }
