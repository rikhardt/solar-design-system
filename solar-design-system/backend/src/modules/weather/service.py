import requests
import pandas as pd
import pvlib
from pvlib.location import Location
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union
import logging
from src.database import db_session
from src.modules.weather.models import WeatherData, Location as LocationModel
from config import Config

logger = logging.getLogger(__name__)

class WeatherService:
    """Servicio avanzado para obtener y gestionar datos meteorológicos"""
    
    def __init__(self):
        self.openweather_api_key = Config.WEATHER_API_KEY
        self.solargis_api_key = Config.SOLARGIS_API_KEY
        
        if not self.openweather_api_key:
            logger.warning("WEATHER_API_KEY no configurada")
        if not self.solargis_api_key:
            logger.warning("SOLARGIS_API_KEY no configurada")
    
    def get_weather_data(self, latitude: float, longitude: float,
                        start_date: datetime, end_date: datetime,
                        source: str = 'pvgis') -> pd.DataFrame:
        """
        Obtiene datos meteorológicos de la fuente especificada.
        
        Args:
            latitude: Latitud del sitio
            longitude: Longitud del sitio
            start_date: Fecha inicial
            end_date: Fecha final
            source: Fuente de datos ('pvgis', 'solargis', 'openweather')
            
        Returns:
            DataFrame con datos meteorológicos
        """
        if source == 'pvgis':
            return self._get_pvgis_data(latitude, longitude, start_date, end_date)
        elif source == 'solargis':
            return self._get_solargis_data(latitude, longitude, start_date, end_date)
        elif source == 'openweather':
            return self._get_openweather_data(latitude, longitude, start_date, end_date)
        else:
            raise ValueError(f"Fuente de datos no soportada: {source}")
    
    def _get_pvgis_data(self, latitude: float, longitude: float,
                        start_date: datetime, end_date: datetime) -> pd.DataFrame:
        """Obtiene datos de PVGIS"""
        try:
            # Obtener datos TMY
            data, _, _ = pvlib.iotools.get_pvgis_tmy(
                latitude=latitude,
                longitude=longitude,
                map_variables=True
            )
            
            # Filtrar por fechas
            data = data[(data.index >= start_date) & (data.index <= end_date)]
            
            # Guardar en base de datos local
            self._save_weather_data(data, latitude, longitude, 'PVGIS')
            
            return data
            
        except Exception as e:
            logger.error(f"Error al obtener datos de PVGIS: {str(e)}")
            return pd.DataFrame()
    
    def _get_solargis_data(self, latitude: float, longitude: float,
                          start_date: datetime, end_date: datetime) -> pd.DataFrame:
        """Obtiene datos de Solargis API"""
        if not self.solargis_api_key:
            raise ValueError("SOLARGIS_API_KEY no configurada")
            
        try:
            response = requests.get(
                'https://api.solargis.com/climate/v1/timeseries',
                params={
                    'lat': latitude,
                    'lng': longitude,
                    'start': start_date.isoformat(),
                    'end': end_date.isoformat(),
                    'timestep': 'hourly',
                    'parameters': 'GHI,DNI,DHI,TEMP,RH,WS,WD,AP',
                    'key': self.solargis_api_key
                }
            )
            response.raise_for_status()
            
            # Convertir respuesta a DataFrame
            data = pd.DataFrame(response.json()['data'])
            data['timestamp'] = pd.to_datetime(data['timestamp'])
            data.set_index('timestamp', inplace=True)
            
            # Guardar en base de datos local
            self._save_weather_data(data, latitude, longitude, 'Solargis')
            
            return data
            
        except Exception as e:
            logger.error(f"Error al obtener datos de Solargis: {str(e)}")
            return pd.DataFrame()
    
    def _get_openweather_data(self, latitude: float, longitude: float,
                             start_date: datetime, end_date: datetime) -> pd.DataFrame:
        """Obtiene datos de OpenWeather API"""
        if not self.openweather_api_key:
            raise ValueError("WEATHER_API_KEY no configurada")
            
        try:
            # Primero buscar en base de datos local
            local_data = WeatherData.query.filter(
                WeatherData.latitude == latitude,
                WeatherData.longitude == longitude,
                WeatherData.timestamp.between(start_date, end_date)
            ).order_by(WeatherData.timestamp).all()
            
            if local_data:
                return pd.DataFrame([d.to_dict() for d in local_data])
            
            # Si no hay datos locales, obtener de la API
            data_list = []
            current_date = start_date
            
            while current_date <= end_date:
                response = requests.get(
                    'https://api.openweathermap.org/data/2.5/onecall/timemachine',
                    params={
                        'lat': latitude,
                        'lon': longitude,
                        'appid': self.openweather_api_key,
                        'units': 'metric',
                        'dt': int(current_date.timestamp())
                    }
                )
                response.raise_for_status()
                
                hourly_data = response.json().get('hourly', [])
                for hour_data in hourly_data:
                    timestamp = datetime.fromtimestamp(hour_data['dt'])
                    if start_date <= timestamp <= end_date:
                        weather_data = WeatherData(
                            latitude=latitude,
                            longitude=longitude,
                            timestamp=timestamp,
                            temperature=hour_data['temp'],
                            humidity=hour_data['humidity'],
                            pressure=hour_data['pressure'],
                            cloud_cover=hour_data['clouds'],
                            wind_speed=hour_data['wind_speed'],
                            wind_direction=hour_data.get('wind_deg'),
                            source='OpenWeather'
                        )
                        
                        # Calcular radiación solar usando pvlib
                        location = Location(latitude, longitude, 'UTC')
                        solar_position = location.get_solarposition(pd.DatetimeIndex([timestamp]))
                        clearsky = location.get_clearsky(pd.DatetimeIndex([timestamp]))
                        
                        # Ajustar por nubosidad
                        cloud_factor = 1 - (hour_data['clouds'] / 100) * 0.75
                        weather_data.ghi = float(clearsky['ghi'][0] * cloud_factor)
                        weather_data.dni = float(clearsky['dni'][0] * cloud_factor)
                        weather_data.dhi = float(clearsky['dhi'][0] * cloud_factor)
                        
                        db_session.add(weather_data)
                        data_list.append(weather_data.to_dict())
                
                current_date += timedelta(days=1)
            
            db_session.commit()
            return pd.DataFrame(data_list)
            
        except Exception as e:
            logger.error(f"Error al obtener datos de OpenWeather: {str(e)}")
            return pd.DataFrame()
    
    def _save_weather_data(self, data: pd.DataFrame, latitude: float,
                          longitude: float, source: str):
        """Guarda datos meteorológicos en la base de datos local"""
        for timestamp, row in data.iterrows():
            weather_data = WeatherData(
                latitude=latitude,
                longitude=longitude,
                timestamp=timestamp,
                temperature=row.get('temp_air', row.get('TEMP')),
                humidity=row.get('relative_humidity', row.get('RH')),
                pressure=row.get('pressure', row.get('AP')),
                wind_speed=row.get('wind_speed', row.get('WS')),
                wind_direction=row.get('wind_direction', row.get('WD')),
                ghi=row.get('ghi', row.get('GHI')),
                dni=row.get('dni', row.get('DNI')),
                dhi=row.get('dhi', row.get('DHI')),
                source=source
            )
            db_session.add(weather_data)
        
        db_session.commit()
    
    def get_location_climate(self, latitude: float, longitude: float) -> Dict[str, float]:
        """
        Obtiene datos climáticos promedio para una ubicación
        
        Args:
            latitude: Latitud del sitio
            longitude: Longitud del sitio
            
        Returns:
            Dict con promedios climáticos
        """
        location = LocationModel.query.filter_by(
            latitude=latitude,
            longitude=longitude
        ).first()
        
        if location and location.updated_at > datetime.utcnow() - timedelta(days=30):
            return {
                'avg_temperature': location.avg_temperature,
                'avg_humidity': location.avg_humidity,
                'avg_ghi': location.avg_ghi,
                'avg_dni': location.avg_dni,
                'avg_dhi': location.avg_dhi
            }
        
        # Si no hay datos o están desactualizados, obtener nuevos
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=365)
        
        data = self.get_weather_data(latitude, longitude, start_date, end_date)
        
        if data.empty:
            return {}
        
        # Calcular promedios
        averages = {
            'avg_temperature': data['temperature'].mean() if 'temperature' in data else None,
            'avg_humidity': data['humidity'].mean() if 'humidity' in data else None,
            'avg_ghi': data['ghi'].mean() if 'ghi' in data else None,
            'avg_dni': data['dni'].mean() if 'dni' in data else None,
            'avg_dhi': data['dhi'].mean() if 'dhi' in data else None
        }
        
        # Actualizar o crear registro de ubicación
        if not location:
            location = LocationModel(
                latitude=latitude,
                longitude=longitude
            )
        
        location.avg_temperature = averages['avg_temperature']
        location.avg_humidity = averages['avg_humidity']
        location.avg_ghi = averages['avg_ghi']
        location.avg_dni = averages['avg_dni']
        location.avg_dhi = averages['avg_dhi']
        location.updated_at = datetime.utcnow()
        
        db_session.add(location)
        db_session.commit()
        
        return averages
