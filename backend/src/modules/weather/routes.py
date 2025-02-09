from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
from src.modules.weather.service import WeatherService
from src.modules.weather.models import Location, WeatherData
from src import db

bp = Blueprint('weather', __name__)
weather_service = WeatherService()

@bp.route('/current', methods=['GET'])
def get_current_weather():
    """Obtiene datos meteorológicos actuales para una ubicación"""
    try:
        latitude = float(request.args.get('latitude'))
        longitude = float(request.args.get('longitude'))
    except (TypeError, ValueError):
        return jsonify({
            'error': 'Se requieren latitud y longitud válidas como parámetros'
        }), 400
    
    weather_data = weather_service.get_current_weather(latitude, longitude)
    if weather_data:
        return jsonify(weather_data)
    else:
        return jsonify({
            'error': 'No se pudieron obtener los datos meteorológicos'
        }), 500

@bp.route('/historical', methods=['GET'])
def get_historical_weather():
    """Obtiene datos meteorológicos históricos para un período"""
    try:
        latitude = float(request.args.get('latitude'))
        longitude = float(request.args.get('longitude'))
        start_date = datetime.fromisoformat(request.args.get('start_date'))
        end_date = datetime.fromisoformat(request.args.get('end_date'))
    except (TypeError, ValueError):
        return jsonify({
            'error': 'Parámetros inválidos. Se requieren latitud, longitud, ' +
                    'start_date y end_date (formato ISO)'
        }), 400
    
    # Limitar el período a un máximo de 7 días
    if end_date - start_date > timedelta(days=7):
        return jsonify({
            'error': 'El período máximo permitido es de 7 días'
        }), 400
    
    data = weather_service.get_historical_data(
        latitude, longitude, start_date, end_date
    )
    return jsonify(data)

@bp.route('/locations', methods=['POST'])
def create_location():
    """Registra una nueva ubicación para seguimiento"""
    data = request.get_json()
    
    # Validación básica
    required_fields = ['latitude', 'longitude']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Campo requerido: {field}'}), 400
    
    location = Location(
        name=data.get('name'),
        latitude=data['latitude'],
        longitude=data['longitude'],
        elevation=data.get('elevation'),
        country=data.get('country'),
        timezone=data.get('timezone')
    )
    
    db.session.add(location)
    db.session.commit()
    
    # Iniciar recopilación de datos meteorológicos
    weather_service.update_location_averages(location)
    
    return jsonify(location.to_dict()), 201

@bp.route('/locations/<int:id>', methods=['GET'])
def get_location(id):
    """Obtiene detalles de una ubicación registrada"""
    location = Location.query.get_or_404(id)
    return jsonify(location.to_dict())

@bp.route('/locations', methods=['GET'])
def list_locations():
    """Lista todas las ubicaciones registradas"""
    locations = Location.query.all()
    return jsonify([loc.to_dict() for loc in locations])

@bp.route('/locations/<int:id>/weather', methods=['GET'])
def get_location_weather(id):
    """Obtiene datos meteorológicos para una ubicación registrada"""
    location = Location.query.get_or_404(id)
    
    # Por defecto, obtener datos de las últimas 24 horas
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(hours=24)
    
    # Permitir personalizar el período
    if 'start_date' in request.args and 'end_date' in request.args:
        try:
            start_date = datetime.fromisoformat(request.args.get('start_date'))
            end_date = datetime.fromisoformat(request.args.get('end_date'))
        except ValueError:
            return jsonify({
                'error': 'Formato de fecha inválido. Use formato ISO'
            }), 400
    
    data = weather_service.get_historical_data(
        location.latitude, location.longitude,
        start_date, end_date
    )
    return jsonify(data)

@bp.route('/locations/<int:id>/update-averages', methods=['POST'])
def update_location_averages(id):
    """Actualiza los promedios climáticos de una ubicación"""
    location = Location.query.get_or_404(id)
    weather_service.update_location_averages(location)
    return jsonify(location.to_dict())
