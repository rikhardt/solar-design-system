from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from src import db

class User(db.Model):
    """Modelo de usuario para autenticación y autorización"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.String(20), nullable=False, default='user')  # user, admin, engineer
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # Campos de perfil
    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))
    company = db.Column(db.String(128))
    position = db.Column(db.String(64))
    phone = db.Column(db.String(20))
    
    # Preferencias
    preferred_language = db.Column(db.String(5), default='es')
    notifications_enabled = db.Column(db.Boolean, default=True)
    
    # Relaciones
    projects = db.relationship('Project', backref='owner', lazy='dynamic')
    
    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')
    
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def update_last_login(self):
        self.last_login = datetime.utcnow()
        db.session.commit()
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'is_active': self.is_active,
            'profile': {
                'first_name': self.first_name,
                'last_name': self.last_name,
                'company': self.company,
                'position': self.position,
                'phone': self.phone
            },
            'preferences': {
                'language': self.preferred_language,
                'notifications_enabled': self.notifications_enabled
            },
            'created_at': self.created_at.isoformat(),
            'last_login': self.last_login.isoformat() if self.last_login else None
        }
    
    def has_permission(self, permission):
        """Verificar si el usuario tiene un permiso específico"""
        permissions = {
            'user': ['view_own_projects', 'create_project', 'edit_own_project'],
            'engineer': ['view_own_projects', 'create_project', 'edit_own_project',
                        'view_all_projects', 'approve_designs'],
            'admin': ['view_own_projects', 'create_project', 'edit_own_project',
                     'view_all_projects', 'approve_designs', 'manage_users',
                     'manage_components']
        }
        return permission in permissions.get(self.role, [])

class UserActivity(db.Model):
    """Registro de actividades de usuario"""
    __tablename__ = 'user_activities'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    activity_type = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(255))
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    user = db.relationship('User', backref='activities')
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'activity_type': self.activity_type,
            'description': self.description,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'created_at': self.created_at.isoformat()
        }

class PasswordReset(db.Model):
    """Modelo para gestionar restablecimientos de contraseña"""
    __tablename__ = 'password_resets'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    token = db.Column(db.String(100), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)
    used = db.Column(db.Boolean, default=False)
    
    user = db.relationship('User', backref='password_resets')
