from flask import Blueprint, request, jsonify
from typing import Dict, Any
from datetime import datetime
from src.modules.simulation.calculator import SimulationParameters, SolarCalculator
from src.modules.components.models import SolarPanel, Inverter, Battery, MountingSystem
from src.modules.weather.service import WeatherService
from src import db

simulation_bp = Blueprint('simulation', __name__)
calculator = SolarCalculator()
weather_service = WeatherService()

@simulation_bp.route('/simulate', methods=['POST'])
async def simulate_system():
    """
    Endpoint para simular un sistema fotovoltaico completo
    
    Request body:
    {
        "location": {
            "latitude": float,
            "longitude": float,
            "altitude": float,
            "timezone": str,
            "albedo": float
        },
        "components": {
            "panel_id": int,
            "inverter_id": int,
            "battery_id": int (opcional),
            "mounting_id": int (opcional)
        },
        "configuration": {
            "system_type": str,
            "use_bifacial": bool,
            "use_tracking": bool,
            "tracking_type": str (opcional),
            "surface_tilt": float,
            "surface_azimuth": float
        },
        "simulation": {
            "start_date": str (ISO format),
            "end_date": str (ISO format),
            "temporal_resolution": int,
            "ray_tracing": bool
        },
        "economic": {
            "electricity_price": float,
            "discount_rate": float,
            "analysis_period": int
        },
        "load_profile": {
            "data": Dict[str, float] (opcional),
            "peak_demand": float (opcional)
        },
        "constraints": {
            "area_available": float (opcional),
            "budget_limit": float (opcional),
            "grid_connection_limit": float (opcional)
        }
    }
    """
    try:
        data = request.get_json()
        
        # Obtener componentes
        panel = db.session.get(SolarPanel, data['components']['panel_id'])
        if not panel:
            return jsonify({'error': 'Panel no encontrado'}), 404
            
        inverter = db.session.get(Inverter, data['components']['inverter_id'])
        if not inverter:
            return jsonify({'error': 'Inversor no encontrado'}), 404
            
        # Componentes opcionales
        battery = None
        if 'battery_id' in data['components']:
            battery = db.session.get(Battery, data['components']['battery_id'])
            
        mounting = None
        if 'mounting_id' in data['components']:
            mounting = db.session.get(MountingSystem, data['components']['mounting_id'])
        
        # Preparar parámetros de simulación
        params = SimulationParameters(
            # Ubicación
            latitude=data['location']['latitude'],
            longitude=data['location']['longitude'],
            altitude=data['location']['altitude'],
            timezone=data['location']['timezone'],
            albedo=data['location']['albedo'],
            
            # Componentes
            module_parameters={
                **panel.to_dict(),
                'surface_tilt': data['configuration']['surface_tilt'],
                'surface_azimuth': data['configuration']['surface_azimuth']
            },
            inverter_parameters=inverter.to_dict(),
            battery_parameters=battery.to_dict() if battery else None,
            mounting_parameters=mounting.to_dict() if mounting else None,
            
            # Configuración
            system_type=data['configuration']['system_type'],
            use_bifacial=data['configuration']['use_bifacial'],
            use_tracking=data['configuration']['use_tracking'],
            tracking_type=data['configuration'].get('tracking_type'),
            
            # Simulación
            temporal_resolution=data['simulation']['temporal_resolution'],
            ray_tracing=data['simulation']['ray_tracing'],
            
            # Análisis económico
            electricity_price=data['economic']['electricity_price'],
            discount_rate=data['economic']['discount_rate'],
            analysis_period=data['economic']['analysis_period'],
            
            # Perfil de carga
            load_profile=data['load_profile'].get('data'),
            peak_demand=data['load_profile'].get('peak_demand'),
            
            # Restricciones
            area_available=data['constraints'].get('area_available'),
            budget_limit=data['constraints'].get('budget_limit'),
            grid_connection_limit=data['constraints'].get('grid_connection_limit')
        )
        
        # Realizar simulación
        results = calculator.simulate_system(
            params=params,
            start_date=datetime.fromisoformat(data['simulation']['start_date']),
            end_date=datetime.fromisoformat(data['simulation']['end_date'])
        )
        
        return jsonify(results)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@simulation_bp.route('/optimize', methods=['POST'])
async def optimize_system():
    """
    Endpoint para optimizar la configuración del sistema
    
    Request body:
    {
        "location": {...},  # Igual que /simulate
        "components": {
            "available_panels": [int],
            "available_inverters": [int],
            "available_batteries": [int],
            "available_mountings": [int]
        },
        "constraints": {...},  # Igual que /simulate
        "optimization": {
            "objective": str,  # "npv", "lcoe", "production"
            "max_iterations": int,
            "population_size": int
        }
    }
    """
    try:
        data = request.get_json()
        
        # Obtener componentes disponibles
        panels = db.session.query(SolarPanel).filter(
            SolarPanel.id.in_(data['components']['available_panels'])
        ).all()
        
        inverters = db.session.query(Inverter).filter(
            Inverter.id.in_(data['components']['available_inverters'])
        ).all()
        
        batteries = []
        if 'available_batteries' in data['components']:
            batteries = db.session.query(Battery).filter(
                Battery.id.in_(data['components']['available_batteries'])
            ).all()
            
        mountings = []
        if 'available_mountings' in data['components']:
            mountings = db.session.query(MountingSystem).filter(
                MountingSystem.id.in_(data['components']['available_mountings'])
            ).all()
        
        # Definir restricciones
        constraints = {
            'max_modules': int(data['constraints'].get('area_available', 1000) / 2),  # 2m² por módulo aprox
            'max_inverters': 10,  # límite arbitrario
            'module_cost': min(p.to_dict()['cost'] for p in panels),
            'inverter_cost': min(i.to_dict()['cost'] for i in inverters),
            'electricity_price': data['economic']['electricity_price'],
            'operation_maintenance_cost': 10  # USD/kWp/año
        }
        
        # Buscar mejor configuración para cada combinación de componentes
        best_result = None
        best_npv = float('-inf')
        
        for panel in panels:
            for inverter in inverters:
                # Crear parámetros base
                params = SimulationParameters(
                    latitude=data['location']['latitude'],
                    longitude=data['location']['longitude'],
                    altitude=data['location']['altitude'],
                    timezone=data['location']['timezone'],
                    albedo=data['location']['albedo'],
                    module_parameters=panel.to_dict(),
                    inverter_parameters=inverter.to_dict()
                )
                
                # Optimizar configuración
                result = calculator.optimize_system_configuration(params, constraints)
                
                if result['optimal_npv'] > best_npv:
                    best_npv = result['optimal_npv']
                    best_result = {
                        'panel': panel.to_dict(),
                        'inverter': inverter.to_dict(),
                        'configuration': result
                    }
        
        return jsonify(best_result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@simulation_bp.route('/validate', methods=['POST'])
async def validate_system():
    """
    Endpoint para validar la viabilidad de un diseño
    
    Request body:
    {
        "design": {...}  # Igual que /simulate
    }
    """
    try:
        data = request.get_json()
        design = data['design']
        
        # Lista para almacenar problemas encontrados
        issues = []
        
        # 1. Validar compatibilidad de voltajes
        panel = db.session.get(SolarPanel, design['components']['panel_id'])
        inverter = db.session.get(Inverter, design['components']['inverter_id'])
        
        max_panels_series = int(inverter.max_dc_voltage / panel.voc_stc)
        min_panels_series = int(np.ceil(inverter.mppt_min_voltage / panel.vmp_stc))
        
        if design['configuration']['panels_in_series'] > max_panels_series:
            issues.append({
                'type': 'voltage_error',
                'message': f'Demasiados paneles en serie. Máximo: {max_panels_series}'
            })
            
        if design['configuration']['panels_in_series'] < min_panels_series:
            issues.append({
                'type': 'voltage_error',
                'message': f'Insuficientes paneles en serie. Mínimo: {min_panels_series}'
            })
            
        # 2. Validar ratio DC/AC
        dc_power = panel.power_stc * design['configuration']['total_panels']
        ac_power = inverter.nominal_ac_power * design['configuration']['inverter_count']
        dc_ac_ratio = dc_power / ac_power
        
        if dc_ac_ratio > 1.5:
            issues.append({
                'type': 'power_ratio_warning',
                'message': f'Ratio DC/AC alto: {dc_ac_ratio:.2f}'
            })
            
        # 3. Validar carga mecánica si hay estructura
        if 'mounting_id' in design['components']:
            mounting = db.session.get(MountingSystem, design['components']['mounting_id'])
            total_weight = panel.weight * design['configuration']['total_panels']
            
            if total_weight > mounting.max_load:
                issues.append({
                    'type': 'mechanical_error',
                    'message': 'Peso total excede límite de estructura'
                })
        
        # 4. Validar restricciones del sitio
        if 'area_available' in design['constraints']:
            required_area = panel.length * panel.width * design['configuration']['total_panels'] / 1e6  # m²
            if required_area > design['constraints']['area_available']:
                issues.append({
                    'type': 'space_error',
                    'message': 'Área requerida excede espacio disponible'
                })
        
        # 5. Validar sistema de almacenamiento
        if 'battery_id' in design['components']:
            battery = db.session.get(Battery, design['components']['battery_id'])
            
            if design['configuration']['system_type'] == 'hybrid':
                if not inverter.is_hybrid:
                    issues.append({
                        'type': 'compatibility_error',
                        'message': 'Inversor no es compatible con baterías'
                    })
                    
                if battery.nominal_voltage not in inverter.battery_voltage_range:
                    issues.append({
                        'type': 'voltage_error',
                        'message': 'Voltaje de batería incompatible con inversor'
                    })
        
        return jsonify({
            'valid': len(issues) == 0,
            'issues': issues
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
