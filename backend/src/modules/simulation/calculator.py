import numpy as np
import pandas as pd
import pvlib
from pvlib.location import Location
from pvlib.pvsystem import PVSystem, Array
from pvlib.temperature import TEMPERATURE_MODEL_PARAMETERS
from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime, timedelta
import math
from dataclasses import dataclass
from scipy.optimize import differential_evolution, minimize_scalar
import trimesh
from shapely.geometry import Polygon, Point
import networkx as nx

@dataclass
class SimulationParameters:
    """Parámetros mejorados para la simulación fotovoltaica"""
    # Ubicación y clima
    latitude: float
    longitude: float
    altitude: float
    timezone: str
    albedo: float
    
    # Componentes
    module_parameters: Dict
    inverter_parameters: Dict
    battery_parameters: Optional[Dict] = None
    mounting_parameters: Optional[Dict] = None
    
    # Configuración del sistema
    system_type: str = "grid-tied"  # grid-tied, off-grid, hybrid
    use_bifacial: bool = False
    use_tracking: bool = False
    tracking_type: Optional[str] = None  # single-axis, dual-axis
    
    # Parámetros de simulación
    temporal_resolution: int = 15  # minutos
    temperature_model: str = 'sapm'
    ac_model: str = 'sandia'
    bifacial_model: str = 'view_factor'
    ray_tracing: bool = False
    losses: Dict = None
    
    # Análisis económico
    electricity_price: float = 0.12  # USD/kWh
    discount_rate: float = 0.06
    analysis_period: int = 25  # años
    inflation_rate: float = 0.02
    
    # Perfiles de carga (para sistemas híbridos/off-grid)
    load_profile: Optional[pd.Series] = None
    peak_demand: Optional[float] = None
    
    # Restricciones
    area_available: Optional[float] = None  # m²
    budget_limit: Optional[float] = None  # USD
    grid_connection_limit: Optional[float] = None  # kW

class SolarCalculator:
    """Calculadora avanzada para simulación de sistemas fotovoltaicos"""
    
    def __init__(self):
        self.temperature_models = TEMPERATURE_MODEL_PARAMETERS
        
    def simulate_system(self, params: SimulationParameters, 
                       start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """
        Realiza la simulación completa del sistema fotovoltaico
        
        Args:
            params: Parámetros de simulación
            start_date: Fecha inicial
            end_date: Fecha final
            
        Returns:
            Dict con resultados de simulación
        """
        # Crear ubicación
        location = Location(
            latitude=params.latitude,
            longitude=params.longitude,
            tz=params.timezone,
            altitude=params.altitude
        )
        
        # Generar índice de tiempo con resolución especificada
        times = pd.date_range(
            start=start_date,
            end=end_date,
            freq=f'{params.temporal_resolution}min'
        )
        
        # Obtener datos meteorológicos
        weather_data = self.get_weather_data(location, start_date, end_date)
        
        # Calcular posición solar
        solar_position = location.get_solarposition(times)
        
        # Aplicar seguimiento si está habilitado
        if params.use_tracking:
            tracking_angles = pd.DataFrame(index=times)
            for time in times:
                angles = self._optimize_tracking_angle(
                    solar_position.loc[time],
                    params.tracking_type
                )
                if isinstance(angles, dict):
                    tracking_angles.loc[time, 'surface_tilt'] = angles['tilt']
                    tracking_angles.loc[time, 'surface_azimuth'] = angles['azimuth']
                else:
                    tracking_angles.loc[time, 'surface_tilt'] = angles
                    tracking_angles.loc[time, 'surface_azimuth'] = 180
        else:
            tracking_angles = pd.DataFrame({
                'surface_tilt': [params.module_parameters['surface_tilt']] * len(times),
                'surface_azimuth': [params.module_parameters['surface_azimuth']] * len(times)
            }, index=times)
        
        # Calcular irradiancia en plano del array
        poa_irradiance = pd.DataFrame(index=times)
        for time in times:
            poa = pvlib.irradiance.get_total_irradiance(
                surface_tilt=tracking_angles.loc[time, 'surface_tilt'],
                surface_azimuth=tracking_angles.loc[time, 'surface_azimuth'],
                solar_zenith=solar_position.loc[time, 'apparent_zenith'],
                solar_azimuth=solar_position.loc[time, 'azimuth'],
                dni=weather_data.loc[time, 'dni'],
                ghi=weather_data.loc[time, 'ghi'],
                dhi=weather_data.loc[time, 'dhi'],
                albedo=params.albedo,
                model='haydavies'
            )
            poa_irradiance.loc[time] = poa
        
        # Calcular efectos bifaciales si aplica
        if params.use_bifacial:
            bifacial_gain = self.calculate_bifacial_gain(
                front_irradiance=poa_irradiance['poa_global'],
                mounting_height=params.mounting_parameters['height'],
                ground_albedo=params.albedo,
                module_parameters=params.module_parameters
            )
            poa_irradiance['poa_global'] += bifacial_gain
        
        # Aplicar ray-tracing para sombras y reflejos si está habilitado
        if params.ray_tracing and 'geometry' in params.mounting_parameters:
            shading_factors = self.calculate_3d_shading(
                geometry=params.mounting_parameters['geometry'],
                sun_positions=solar_position,
                module_geometry=params.mounting_parameters['module_mesh']
            )
            
            reflected_irradiance = self.calculate_reflections(
                geometry=params.mounting_parameters['geometry'],
                sun_positions=solar_position,
                irradiance=poa_irradiance['poa_global'],
                module_geometry=params.mounting_parameters['module_mesh']
            )
            
            poa_irradiance['poa_global'] *= shading_factors
            poa_irradiance['poa_global'] += reflected_irradiance
        
        # Calcular temperatura de celda
        cell_temperature = self.calculate_cell_temperature(
            poa_global=poa_irradiance['poa_global'],
            temp_air=weather_data['temp_air'],
            wind_speed=weather_data['wind_speed'],
            model=params.temperature_model
        )
        
        # Calcular potencia DC
        dc_output = self.calculate_dc_power(
            effective_irradiance=poa_irradiance['poa_global'],
            cell_temperature=cell_temperature,
            module_parameters=params.module_parameters
        )
        
        # Aplicar pérdidas del sistema
        if params.losses:
            dc_output = self.calculate_system_losses(dc_output, params.losses)
        
        # Calcular potencia AC
        ac_output = self.calculate_ac_power(
            dc_power=dc_output,
            dc_voltage=dc_output * 0.5,  # Simplificación del voltaje DC
            inverter_parameters=params.inverter_parameters
        )
        
        # Simulación de batería para sistemas híbridos/off-grid
        battery_results = None
        if params.system_type in ['hybrid', 'off-grid'] and params.battery_parameters:
            battery_results = self.simulate_battery_system(
                params.battery_parameters,
                ac_output,
                params.load_profile
            )
            
            # Ajustar producción según operación de la batería
            if battery_results:
                ac_output = ac_output - battery_results['battery_power']
        
        # Calcular métricas de rendimiento
        annual_production = ac_output.sum()
        specific_yield = annual_production / params.module_parameters['Pmp0']
        performance_ratio = annual_production / (poa_irradiance['poa_global'].sum() * 
                                               params.module_parameters['A'] * 
                                               params.module_parameters['eta_m'])
        
        results = {
            'hourly_production': ac_output.to_dict(),
            'monthly_production': ac_output.resample('M').sum().to_dict(),
            'annual_production': float(annual_production),
            'specific_yield': float(specific_yield),
            'performance_ratio': float(performance_ratio),
            'capacity_factor': float(annual_production / (8760 * params.module_parameters['Pmp0']))
        }
        
        # Añadir resultados de batería si aplica
        if battery_results:
            results.update({
                'battery_soc': battery_results['soc'].to_dict(),
                'battery_power': battery_results['battery_power'].to_dict(),
                'grid_power': battery_results['grid_power'].to_dict(),
                'self_consumption_ratio': battery_results['self_consumption_ratio'],
                'autarky_ratio': battery_results['autarky_ratio']
            })
            
        # Añadir métricas de sombreado si aplica
        if params.ray_tracing:
            results.update({
                'shading_loss_annual': 1 - shading_factors.mean(),
                'shading_factors': shading_factors.to_dict(),
                'reflected_irradiance': reflected_irradiance.to_dict()
            })
            
        # Calcular métricas económicas
        economic_results = self.calculate_economic_metrics(
            annual_production=annual_production,
            system_cost=params.module_parameters['cost'] * params.module_parameters['count'] +
                       params.inverter_parameters['cost'] * params.inverter_parameters['count'],
            electricity_price=params.electricity_price,
            operation_maintenance_cost=annual_production * 0.01,  # 1% de producción
            discount_rate=params.discount_rate,
            electricity_price_increase=params.inflation_rate,
            analysis_period=params.analysis_period
        )
        results.update(economic_results)
        
        return results
    
    # [Resto de los métodos previos se mantienen igual]
