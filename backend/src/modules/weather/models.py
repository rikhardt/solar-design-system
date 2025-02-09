from datetime import datetime
from sqlalchemy import Column, Integer, Float, String, DateTime, Index
from src.database import Base

class WeatherData(Base):
    """Modelo para almacenar datos meteorológicos"""
    __tablename__ = 'weather_data'
    
    id = Column(Integer, primary_key=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    timestamp = Column(DateTime, nullable=False)
    
    # Datos meteorológicos básicos
    temperature = Column(Float)  # °C
    humidity = Column(Float)     # %
    pressure = Column(Float)     # hPa
    cloud_cover = Column(Float)  # %
    wind_speed = Column(Float)   # m/s
    wind_direction = Column(Float)  # grados
    
    # Datos de radiación solar
    ghi = Column(Float)  # Irradiancia Global Horizontal (W/m²)
    dni = Column(Float)  # Irradiancia Directa Normal (W/m²)
    dhi = Column(Float)  # Irradiancia Difusa Horizontal (W/m²)
    
    # Metadatos
    source = Column(String(50))  # Fuente de datos (PVGIS, Solargis, OpenWeather)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Índices para optimizar búsquedas
    __table_args__ = (
        Index('idx_location_time', latitude, longitude, timestamp),
        Index('idx_timestamp', timestamp),
    )
    
    def to_dict(self):
        """Convierte el modelo a diccionario"""
        return {
            'id': self.id,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'timestamp': self.timestamp.isoformat(),
            'temperature': self.temperature,
            'humidity': self.humidity,
            'pressure': self.pressure,
            'cloud_cover': self.cloud_cover,
            'wind_speed': self.wind_speed,
            'wind_direction': self.wind_direction,
            'ghi': self.ghi,
            'dni': self.dni,
            'dhi': self.dhi,
            'source': self.source,
            'created_at': self.created_at.isoformat()
        }

class Location(Base):
    """Modelo para almacenar información climática por ubicación"""
    __tablename__ = 'locations'
    
    id = Column(Integer, primary_key=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    
    # Promedios climáticos
    avg_temperature = Column(Float)  # °C
    avg_humidity = Column(Float)     # %
    avg_ghi = Column(Float)         # kWh/m²/día
    avg_dni = Column(Float)         # kWh/m²/día
    avg_dhi = Column(Float)         # kWh/m²/día
    
    # Datos adicionales
    elevation = Column(Float)        # metros sobre nivel del mar
    terrain_type = Column(String(50))  # tipo de terreno
    albedo = Column(Float)          # reflectividad del suelo
    
    # Metadatos
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Índices
    __table_args__ = (
        Index('idx_location', latitude, longitude, unique=True),
    )
    
    def to_dict(self):
        """Convierte el modelo a diccionario"""
        return {
            'id': self.id,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'avg_temperature': self.avg_temperature,
            'avg_humidity': self.avg_humidity,
            'avg_ghi': self.avg_ghi,
            'avg_dni': self.avg_dni,
            'avg_dhi': self.avg_dhi,
            'elevation': self.elevation,
            'terrain_type': self.terrain_type,
            'albedo': self.albedo,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class WeatherForecast(Base):
    """Modelo para almacenar pronósticos meteorológicos"""
    __tablename__ = 'weather_forecasts'
    
    id = Column(Integer, primary_key=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    forecast_time = Column(DateTime, nullable=False)  # Tiempo para el que se hace el pronóstico
    prediction_time = Column(DateTime, nullable=False)  # Tiempo en que se hizo el pronóstico
    
    # Datos pronosticados
    temperature = Column(Float)
    humidity = Column(Float)
    cloud_cover = Column(Float)
    wind_speed = Column(Float)
    wind_direction = Column(Float)
    precipitation_probability = Column(Float)
    
    # Pronóstico de radiación solar
    ghi_forecast = Column(Float)
    dni_forecast = Column(Float)
    dhi_forecast = Column(Float)
    
    # Metadatos
    source = Column(String(50))
    confidence = Column(Float)  # Nivel de confianza del pronóstico (0-1)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Índices
    __table_args__ = (
        Index('idx_forecast_location_time', latitude, longitude, forecast_time),
        Index('idx_prediction_time', prediction_time),
    )
    
    def to_dict(self):
        """Convierte el modelo a diccionario"""
        return {
            'id': self.id,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'forecast_time': self.forecast_time.isoformat(),
            'prediction_time': self.prediction_time.isoformat(),
            'temperature': self.temperature,
            'humidity': self.humidity,
            'cloud_cover': self.cloud_cover,
            'wind_speed': self.wind_speed,
            'wind_direction': self.wind_direction,
            'precipitation_probability': self.precipitation_probability,
            'ghi_forecast': self.ghi_forecast,
            'dni_forecast': self.dni_forecast,
            'dhi_forecast': self.dhi_forecast,
            'source': self.source,
            'confidence': self.confidence,
            'created_at': self.created_at.isoformat()
        }
