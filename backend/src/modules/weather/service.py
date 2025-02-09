import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging
import numpy as np
from src import db
from src.modules.weather.models import WeatherData, Location, WeatherSource
from config import Config

logger = logging.getLogger(__name__)

class WeatherService:
    """Servicio mejorado para obtener y gestionar datos meteorológicos de alta resolución"""
    
    def __init__(self):
        self.sources = {
            'solargis': {
                'api_key': Config.SOLARGIS_API_KEY,
                'base_url': 'https://api.solargis.com/v2',
                'resolution': 15  # minutos
            },
            'meteonorm': {
                'api_key': Config.METEONORM_API_KEY,
                'base_url': 'https://api.meteonorm.com/v8',
                'resolution': 15
            },
            'openweather': {
                'api_key': Config.OPENWEATHER_API_KEY,
                'base_url': 'https://api.openweathermap.org/data/2.5',
                'resolution': 60
            }
        }
    
    async def get_high_resolution_data(
        self, 
        latitude: float, 
        longitude: float,
        start_date: datetime,
        end_date: datetime,
        resolution: int = 15
    ) -> List[Dict]:
        """
        Obtiene datos meteorológicos de alta resolución combinando múltiples fuentes
        
        Args:
            latitude: Latitud del sitio
            longitude: Longitud del sitio
            start_date: Fecha inicial
            end_date: Fecha final
            resolution: Resolución temporal en minutos (default 15)
            
        Returns:
            Lista de registros meteorológicos
        """
        results = []
        
        # Intentar primero con Solargis (mayor precisión)
        try:
            solargis_data = await self._get_solargis_data(
                latitude, longitude, start_date, end_date
            )
            if solargis_data:
                results.extend(solargis_data)
        except Exception as e:
            logger.error(f"Error con Solargis API: {str(e)}")
            
        # Si no hay datos suficientes, complementar con Meteonorm
        if not results or len(results) < (end_date - start_date).total_seconds() / (resolution * 60):
            try:
                meteonorm_data = await self._get_meteonorm_data(
                    latitude, longitude, start_date, end_date
                )
                if meteonorm_data:
                    # Combinar datos evitando duplicados
                    self._merge_weather_data(results, meteonorm_data)
            except Exception as e:
                logger.error(f"Error con Meteonorm API: {str(e)}")
        
        # Rellenar huecos con modelo de cielo claro y OpenWeather
        if results:
            self._fill_data_gaps(results, latitude, longitude, resolution)
        
        return results
    
    async def _get_solargis_data(
        self, 
        latitude: float, 
        longitude: float,
        start_date: datetime,
        end_date: datetime
    ) -> List[Dict]:
        """Obtiene datos de Solargis API"""
        if not self.sources['solargis']['api_key']:
            return []
            
        response = await self._make_async_request(
            f"{self.sources['solargis']['base_url']}/timeseries",
            params={
                'lat': latitude,
                'lng': longitude,
                'start': start_date.isoformat(),
                'end': end_date.isoformat(),
                'timestep': '15',
                'key': self.sources['solargis']['api_key']
            }
        )
        
        return self._parse_solargis_response(response)
    
    async def _get_meteonorm_data(
        self, 
        latitude: float, 
        longitude: float,
        start_date: datetime,
        end_date: datetime
    ) -> List[Dict]:
        """Obtiene datos de Meteonorm API"""
        if not self.sources['meteonorm']['api_key']:
            return []
            
        response = await self._make_async_request(
            f"{self.sources['meteonorm']['base_url']}/hourly",
            params={
                'lat': latitude,
                'lon': longitude,
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'api_key': self.sources['meteonorm']['api_key']
            }
        )
        
        return self._parse_meteonorm_response(response)
    
    def _merge_weather_data(self, primary_data: List[Dict], secondary_data: List[Dict]):
        """Combina datos de diferentes fuentes evitando duplicados"""
        timestamp_map = {d['timestamp']: d for d in primary_data}
        
        for data in secondary_data:
            if data['timestamp'] not in timestamp_map:
                primary_data.append(data)
            else:
                # Combinar datos si la fuente secundaria tiene mejor calidad
                if data.get('source_quality', 0) > timestamp_map[data['timestamp']].get('source_quality', 0):
                    timestamp_map[data['timestamp']].update(data)
    
    def _fill_data_gaps(
        self, 
        data: List[Dict], 
        latitude: float, 
        longitude: float, 
        resolution: int
    ):
        """Rellena huecos en los datos usando modelo de cielo claro y OpenWeather"""
        timestamps = sorted(d['timestamp'] for d in data)
        
        for i in range(len(timestamps) - 1):
            gap = timestamps[i + 1] - timestamps[i]
            if gap.total_seconds() > resolution * 60:
                # Generar timestamps intermedios
                current = timestamps[i] + timedelta(minutes=resolution)
                while current < timestamps[i + 1]:
                    # Calcular radiación con modelo de cielo claro
                    radiation = self._calculate_clear_sky_radiation(
                        latitude, longitude, current
                    )
                    
                    # Obtener datos actuales de OpenWeather
                    current_weather = self.get_current_weather(latitude, longitude)
                    
                    # Combinar datos
                    gap_data = {
                        'timestamp': current,
                        'source': 'model_interpolation',
                        **radiation,
                        **(current_weather or {})
                    }
                    
                    data.append(gap_data)
                    current += timedelta(minutes=resolution)
    
    def _calculate_clear_sky_radiation(
        self, 
        latitude: float, 
        longitude: float, 
        timestamp: datetime
    ) -> Dict[str, float]:
        """
        Calcula radiación solar usando el modelo de cielo claro ASHRAE
        
        Args:
            latitude: Latitud del sitio (grados)
            longitude: Longitud del sitio (grados)
            timestamp: Momento del cálculo
            
        Returns:
            Dict con GHI, DNI y DHI calculados
        """
        # Implementación del modelo ASHRAE
        day_of_year = timestamp.timetuple().tm_yday
        solar_time = self._calculate_solar_time(longitude, timestamp)
        declination = 23.45 * np.sin(2 * np.pi * (284 + day_of_year) / 365)
        
        # Ángulo horario
        hour_angle = 15 * (solar_time - 12)
        
        # Altura solar
        sin_altitude = (
            np.sin(np.radians(latitude)) * np.sin(np.radians(declination)) +
            np.cos(np.radians(latitude)) * np.cos(np.radians(declination)) *
            np.cos(np.radians(hour_angle))
        )
        solar_altitude = np.arcsin(sin_altitude)
        
        # Masa de aire
        if sin_altitude > 0:
            air_mass = 1 / sin_altitude
        else:
            return {'ghi': 0, 'dni': 0, 'dhi': 0}
        
        # Constantes del modelo ASHRAE
        A = 1160 + 75 * np.sin(2 * np.pi * (day_of_year - 275) / 365)
        B = 0.174 + 0.035 * np.sin(2 * np.pi * (day_of_year - 100) / 365)
        C = 0.095 + 0.04 * np.sin(2 * np.pi * (day_of_year - 100) / 365)
        
        # Cálculo de componentes
        dni = A * np.exp(-B * air_mass)
        dhi = C * dni
        ghi = dni * sin_altitude + dhi
        
        return {
            'ghi': float(ghi),
            'dni': float(dni),
            'dhi': float(dhi)
        }
    
    def _calculate_solar_time(self, longitude: float, timestamp: datetime) -> float:
        """Calcula la hora solar verdadera"""
        standard_meridian = round(longitude / 15) * 15
        equation_of_time = self._calculate_equation_of_time(timestamp)
        
        local_time = timestamp.hour + timestamp.minute / 60
        time_offset = 4 * (longitude - standard_meridian) + equation_of_time
        
        return local_time + time_offset / 60
    
    def _calculate_equation_of_time(self, timestamp: datetime) -> float:
        """Calcula la ecuación del tiempo en minutos"""
        day_of_year = timestamp.timetuple().tm_yday
        b = 2 * np.pi * (day_of_year - 1) / 365
        
        return 229.18 * (
            0.000075 +
            0.001868 * np.cos(b) -
            0.032077 * np.sin(b) -
            0.014615 * np.cos(2 * b) -
            0.040849 * np.sin(2 * b)
        )
    
    # Mantener métodos existentes para compatibilidad
    def get_current_weather(self, latitude: float, longitude: float) -> Optional[Dict]:
        """Obtiene datos meteorológicos actuales de OpenWeather API"""
        # [Mantener implementación existente]
        pass
    
    def get_historical_data(
        self,
        latitude: float,
        longitude: float,
        start_date: datetime,
        end_date: datetime
    ) -> List[Dict]:
        """Obtiene datos históricos (método heredado)"""
        # [Mantener implementación existente]
        pass
    
    def update_location_averages(self, location: Location):
        """Actualiza promedios climáticos de ubicación"""
        # [Mantener implementación existente]
        pass
