from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import (
    create_access_token, create_refresh_token, get_jwt_identity,
    jwt_required, get_jwt
)
from src import db
from .models import User, UserActivity, PasswordReset
from .utils import (
    send_password_reset_email, generate_password_reset_token,
    validate_password_strength
)

auth = Blueprint('auth', __name__, url_prefix='/api/auth')

def log_activity(user_id, activity_type, description=None):
    """Registrar actividad del usuario"""
    activity = UserActivity(
        user_id=user_id,
        activity_type=activity_type,
        description=description,
        ip_address=request.remote_addr,
        user_agent=request.user_agent.string
    )
    db.session.add(activity)
    db.session.commit()

@auth.route('/register', methods=['POST'])
def register():
    """Registrar un nuevo usuario"""
    data = request.get_json()
    
    # Validar campos requeridos
    required_fields = ['username', 'email', 'password']
    for field in required_fields:
        if field not in data:
            return jsonify({
                'error': 'Missing required field',
                'field': field
            }), 400
    
    # Verificar si el usuario ya existe
    if User.query.filter_by(username=data['username']).first():
        return jsonify({
            'error': 'Username already exists'
        }), 400
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify({
            'error': 'Email already registered'
        }), 400
    
    # Validar fortaleza de la contraseña
    if not validate_password_strength(data['password']):
        return jsonify({
            'error': 'Password does not meet security requirements'
        }), 400
    
    # Crear nuevo usuario
    user = User(
        username=data['username'],
        email=data['email'],
        role='user'  # Rol por defecto
    )
    user.password = data['password']  # Esto utilizará el setter que hace el hash
    
    # Campos opcionales de perfil
    optional_fields = ['first_name', 'last_name', 'company', 'position', 'phone']
    for field in optional_fields:
        if field in data:
            setattr(user, field, data[field])
    
    db.session.add(user)
    db.session.commit()
    
    log_activity(user.id, 'REGISTER', 'User registration successful')
    
    return jsonify({
        'message': 'User registered successfully',
        'user': user.to_dict()
    }), 201

@auth.route('/login', methods=['POST'])
def login():
    """Iniciar sesión"""
    data = request.get_json()
    
    if not data.get('username') or not data.get('password'):
        return jsonify({
            'error': 'Missing username or password'
        }), 400
    
    user = User.query.filter_by(username=data['username']).first()
    
    if user and user.verify_password(data['password']):
        if not user.is_active:
            return jsonify({
                'error': 'Account is deactivated'
            }), 403
        
        # Generar tokens
        access_token = create_access_token(
            identity=user.id,
            additional_claims={'role': user.role}
        )
        refresh_token = create_refresh_token(identity=user.id)
        
        # Actualizar último login
        user.update_last_login()
        
        log_activity(user.id, 'LOGIN', 'User login successful')
        
        return jsonify({
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': user.to_dict()
        }), 200
    
    return jsonify({
        'error': 'Invalid username or password'
    }), 401

@auth.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Renovar token de acceso usando refresh token"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user or not user.is_active:
        return jsonify({
            'error': 'User not found or inactive'
        }), 401
    
    access_token = create_access_token(
        identity=current_user_id,
        additional_claims={'role': user.role}
    )
    
    return jsonify({
        'access_token': access_token
    }), 200

@auth.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """Obtener perfil del usuario actual"""
    current_user_id = get_jwt_identity()
    user = User.query.get_or_404(current_user_id)
    
    return jsonify(user.to_dict()), 200

@auth.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """Actualizar perfil del usuario"""
    current_user_id = get_jwt_identity()
    user = User.query.get_or_404(current_user_id)
    data = request.get_json()
    
    updatable_fields = [
        'first_name', 'last_name', 'company', 'position', 'phone',
        'preferred_language', 'notifications_enabled'
    ]
    
    for field in updatable_fields:
        if field in data:
            setattr(user, field, data[field])
    
    db.session.commit()
    log_activity(user.id, 'PROFILE_UPDATE', 'User profile updated')
    
    return jsonify(user.to_dict()), 200

@auth.route('/password/change', methods=['POST'])
@jwt_required()
def change_password():
    """Cambiar contraseña del usuario"""
    current_user_id = get_jwt_identity()
    user = User.query.get_or_404(current_user_id)
    data = request.get_json()
    
    if not data.get('current_password') or not data.get('new_password'):
        return jsonify({
            'error': 'Missing current or new password'
        }), 400
    
    if not user.verify_password(data['current_password']):
        return jsonify({
            'error': 'Current password is incorrect'
        }), 401
    
    if not validate_password_strength(data['new_password']):
        return jsonify({
            'error': 'New password does not meet security requirements'
        }), 400
    
    user.password = data['new_password']
    db.session.commit()
    
    log_activity(user.id, 'PASSWORD_CHANGE', 'User password changed')
    
    return jsonify({
        'message': 'Password updated successfully'
    }), 200

@auth.route('/password/reset/request', methods=['POST'])
def request_password_reset():
    """Solicitar restablecimiento de contraseña"""
    data = request.get_json()
    
    if not data.get('email'):
        return jsonify({
            'error': 'Email is required'
        }), 400
    
    user = User.query.filter_by(email=data['email']).first()
    
    if user:
        token = generate_password_reset_token()
        reset = PasswordReset(
            user_id=user.id,
            token=token,
            expires_at=datetime.utcnow() + timedelta(hours=24)
        )
        
        db.session.add(reset)
        db.session.commit()
        
        send_password_reset_email(user.email, token)
        log_activity(user.id, 'PASSWORD_RESET_REQUEST', 'Password reset requested')
    
    # Siempre devolver 200 para no revelar si el email existe
    return jsonify({
        'message': 'If the email exists, a password reset link has been sent'
    }), 200

@auth.route('/password/reset/verify', methods=['POST'])
def reset_password():
    """Restablecer contraseña usando token"""
    data = request.get_json()
    
    if not data.get('token') or not data.get('new_password'):
        return jsonify({
            'error': 'Token and new password are required'
        }), 400
    
    reset = PasswordReset.query.filter_by(
        token=data['token'],
        used=False
    ).first()
    
    if not reset or reset.expires_at < datetime.utcnow():
        return jsonify({
            'error': 'Invalid or expired token'
        }), 400
    
    if not validate_password_strength(data['new_password']):
        return jsonify({
            'error': 'Password does not meet security requirements'
        }), 400
    
    user = User.query.get(reset.user_id)
    user.password = data['new_password']
    reset.used = True
    
    db.session.commit()
    log_activity(user.id, 'PASSWORD_RESET', 'Password reset completed')
    
    return jsonify({
        'message': 'Password has been reset successfully'
    }), 200

# Endpoints de administración (solo para admins)

@auth.route('/users', methods=['GET'])
@jwt_required()
def list_users():
    """Listar usuarios (requiere rol de admin)"""
    claims = get_jwt()
    if claims.get('role') != 'admin':
        return jsonify({
            'error': 'Admin privileges required'
        }), 403
    
    users = User.query.all()
    return jsonify([user.to_dict() for user in users]), 200

@auth.route('/users/<int:id>', methods=['GET'])
@jwt_required()
def get_user(id):
    """Obtener detalles de un usuario (requiere rol de admin)"""
    claims = get_jwt()
    if claims.get('role') != 'admin':
        return jsonify({
            'error': 'Admin privileges required'
        }), 403
    
    user = User.query.get_or_404(id)
    return jsonify(user.to_dict()), 200

@auth.route('/users/<int:id>', methods=['PUT'])
@jwt_required()
def update_user(id):
    """Actualizar usuario (requiere rol de admin)"""
    claims = get_jwt()
    if claims.get('role') != 'admin':
        return jsonify({
            'error': 'Admin privileges required'
        }), 403
    
    user = User.query.get_or_404(id)
    data = request.get_json()
    
    updatable_fields = ['role', 'is_active']
    for field in updatable_fields:
        if field in data:
            setattr(user, field, data[field])
    
    db.session.commit()
    log_activity(
        get_jwt_identity(),
        'USER_UPDATE',
        f'Admin updated user {user.username}'
    )
    
    return jsonify(user.to_dict()), 200

@auth.route('/users/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_user(id):
    """Eliminar usuario (requiere rol de admin)"""
    claims = get_jwt()
    if claims.get('role') != 'admin':
        return jsonify({
            'error': 'Admin privileges required'
        }), 403
    
    user = User.query.get_or_404(id)
    username = user.username
    
    db.session.delete(user)
    db.session.commit()
    
    log_activity(
        get_jwt_identity(),
        'USER_DELETE',
        f'Admin deleted user {username}'
    )
    
    return '', 204
