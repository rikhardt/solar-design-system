from datetime import datetime
from enum import Enum
from sqlalchemy import Column, Integer, Float, String, DateTime, JSON, ForeignKey, Text, Boolean, Enum as SQLEnum
from src import db

# Enumeraciones
class ModuleTechnology(Enum):
    """Tecnologías de módulos fotovoltaicos"""
    MONO_PERC = "Monocristalino PERC"
    MONO_TOPCON = "Monocristalino TOPCon"
    MONO_HJT = "Monocristalino HJT"
    POLY_PERC = "Policristalino PERC"
    THIN_FILM_CIGS = "Película delgada CIGS"
    THIN_FILM_CDTE = "Película delgada CdTe"
    BIFACIAL = "Bifacial"

class InverterType(Enum):
    """Tipos de inversores"""
    STRING = "String"
    CENTRAL = "Central"
    MICRO = "Micro"
    HYBRID = "Híbrido"
    STORAGE = "Almacenamiento"

class BatteryChemistry(Enum):
    """Tipos de química de baterías"""
    LITHIUM_ION = "Ion de litio"
    LFP = "Litio ferro fosfato"
    LEAD_ACID = "Plomo ácido"
    FLOW = "Flujo"
    SALT = "Sal fundida"

class MountingType(Enum):
    """Tipos de sistemas de montaje"""
    GROUND = "Suelo"
    ROOF_PITCHED = "Techo inclinado"
    ROOF_FLAT = "Techo plano"
    FACADE = "Fachada"
    TRACKER_1AXIS = "Seguidor 1 eje"
    TRACKER_2AXIS = "Seguidor 2 ejes"

# Modelos
class Manufacturer(db.Model):
    """Fabricantes de componentes"""
    __tablename__ = 'manufacturers'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    country = Column(String(50))
    website = Column(String(200))
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'country': self.country,
            'website': self.website,
            'description': self.description
        }

class SolarPanel(db.Model):
    """Paneles solares"""
    __tablename__ = 'solar_panels'
    
    id = Column(Integer, primary_key=True)
    manufacturer_id = Column(Integer, ForeignKey('manufacturers.id'), nullable=False)
    model = Column(String(100), nullable=False)
    technology = Column(SQLEnum(ModuleTechnology), nullable=False)
    
    # Especificaciones eléctricas (STC)
    nominal_power = Column(Float, nullable=False)  # Wp
    voltage_mpp = Column(Float)  # V
    current_mpp = Column(Float)  # A
    voltage_oc = Column(Float)  # V
    current_sc = Column(Float)  # A
    efficiency = Column(Float)  # %
    
    # Coeficientes de temperatura
    temp_coefficient_pmax = Column(Float)  # %/°C
    temp_coefficient_voc = Column(Float)  # %/°C
    temp_coefficient_isc = Column(Float)  # %/°C
    
    # Características físicas
    length = Column(Float)  # mm
    width = Column(Float)  # mm
    thickness = Column(Float)  # mm
    weight = Column(Float)  # kg
    frame_type = Column(String(50))
    
    # Células
    cells_count = Column(Integer)
    cell_type = Column(String(50))
    cell_size = Column(Float)  # mm
    cell_arrangement = Column(String(20))  # ej: "6x10"
    
    # Garantías y certificaciones
    warranty_product = Column(Integer)  # años
    warranty_power_80 = Column(Integer)  # años al 80%
    warranty_power_25y = Column(Float)  # % después de 25 años
    certificates = Column(JSON)  # Lista de certificaciones
    
    created_at = Column(DateTime, default=datetime.utcnow)
    manufacturer = db.relationship('Manufacturer', backref='panels')

    def to_dict(self):
        return {
            'id': self.id,
            'manufacturer': self.manufacturer.to_dict(),
            'model': self.model,
            'technology': self.technology.value,
            'electrical': {
                'nominal_power': self.nominal_power,
                'mpp': {
                    'voltage': self.voltage_mpp,
                    'current': self.current_mpp
                },
                'voc': self.voltage_oc,
                'isc': self.current_sc,
                'efficiency': self.efficiency
            },
            'temperature_coefficients': {
                'pmax': self.temp_coefficient_pmax,
                'voc': self.temp_coefficient_voc,
                'isc': self.temp_coefficient_isc
            },
            'physical': {
                'dimensions': {
                    'length': self.length,
                    'width': self.width,
                    'thickness': self.thickness
                },
                'weight': self.weight,
                'frame': self.frame_type
            },
            'cells': {
                'count': self.cells_count,
                'type': self.cell_type,
                'size': self.cell_size,
                'arrangement': self.cell_arrangement
            },
            'warranty': {
                'product_years': self.warranty_product,
                'power_80_years': self.warranty_power_80,
                'power_25y': self.warranty_power_25y
            },
            'certificates': self.certificates
        }

class Inverter(db.Model):
    """Inversores solares"""
    __tablename__ = 'inverters'
    
    id = Column(Integer, primary_key=True)
    manufacturer_id = Column(Integer, ForeignKey('manufacturers.id'), nullable=False)
    model = Column(String(100), nullable=False)
    type = Column(SQLEnum(InverterType), nullable=False)
    
    # Entrada DC
    max_power_dc = Column(Float)  # W
    max_voltage_dc = Column(Float)  # V
    mppt_voltage_min = Column(Float)  # V
    mppt_voltage_max = Column(Float)  # V
    max_current_dc = Column(Float)  # A
    mppt_count = Column(Integer)
    
    # Salida AC
    nominal_power_ac = Column(Float)  # W
    max_power_ac = Column(Float)  # W
    nominal_voltage_ac = Column(Float)  # V
    nominal_frequency = Column(Float)  # Hz
    max_current_ac = Column(Float)  # A
    thdi = Column(Float)  # %
    
    # Eficiencia
    max_efficiency = Column(Float)  # %
    euro_efficiency = Column(Float)  # %
    mppt_efficiency = Column(Float)  # %
    
    # Protecciones
    dc_reverse_polarity = Column(Boolean)
    dc_switch = Column(Boolean)
    dc_surge_protection = Column(Boolean)
    ac_surge_protection = Column(Boolean)
    ground_fault_monitoring = Column(Boolean)
    
    # Características físicas
    ip_rating = Column(String(10))
    cooling = Column(String(50))
    noise_level = Column(Float)  # dB
    width = Column(Float)  # mm
    height = Column(Float)  # mm
    depth = Column(Float)  # mm
    weight = Column(Float)  # kg
    
    # Condiciones ambientales
    temp_min = Column(Float)  # °C
    temp_max = Column(Float)  # °C
    humidity_max = Column(Float)  # %
    altitude_max = Column(Float)  # m
    
    created_at = Column(DateTime, default=datetime.utcnow)
    manufacturer = db.relationship('Manufacturer', backref='inverters')

    def to_dict(self):
        return {
            'id': self.id,
            'manufacturer': self.manufacturer.to_dict(),
            'model': self.model,
            'type': self.type.value,
            'dc_input': {
                'max_power': self.max_power_dc,
                'max_voltage': self.max_voltage_dc,
                'mppt_range': {
                    'min': self.mppt_voltage_min,
                    'max': self.mppt_voltage_max
                },
                'max_current': self.max_current_dc,
                'mppt_count': self.mppt_count
            },
            'ac_output': {
                'nominal_power': self.nominal_power_ac,
                'max_power': self.max_power_ac,
                'nominal_voltage': self.nominal_voltage_ac,
                'frequency': self.nominal_frequency,
                'max_current': self.max_current_ac,
                'thdi': self.thdi
            },
            'efficiency': {
                'maximum': self.max_efficiency,
                'euro': self.euro_efficiency,
                'mppt': self.mppt_efficiency
            },
            'protection': {
                'dc_reverse_polarity': self.dc_reverse_polarity,
                'dc_switch': self.dc_switch,
                'dc_surge': self.dc_surge_protection,
                'ac_surge': self.ac_surge_protection,
                'ground_fault': self.ground_fault_monitoring
            },
            'physical': {
                'ip_rating': self.ip_rating,
                'cooling': self.cooling,
                'noise_level': self.noise_level,
                'dimensions': {
                    'width': self.width,
                    'height': self.height,
                    'depth': self.depth
                },
                'weight': self.weight
            },
            'environmental': {
                'temperature': {
                    'min': self.temp_min,
                    'max': self.temp_max
                },
                'humidity_max': self.humidity_max,
                'altitude_max': self.altitude_max
            }
        }

class Battery(db.Model):
    """Sistemas de almacenamiento"""
    __tablename__ = 'batteries'
    
    id = Column(Integer, primary_key=True)
    manufacturer_id = Column(Integer, ForeignKey('manufacturers.id'), nullable=False)
    model = Column(String(100), nullable=False)
    chemistry = Column(SQLEnum(BatteryChemistry), nullable=False)
    
    # Especificaciones eléctricas
    nominal_voltage = Column(Float)  # V
    nominal_capacity = Column(Float)  # Ah
    usable_capacity = Column(Float)  # Ah
    nominal_energy = Column(Float)  # kWh
    usable_energy = Column(Float)  # kWh
    round_trip_efficiency = Column(Float)  # %
    
    # Potencia y corriente
    max_charge_power = Column(Float)  # kW
    max_discharge_power = Column(Float)  # kW
    max_charge_current = Column(Float)  # A
    max_discharge_current = Column(Float)  # A
    
    # Ciclo de vida
    cycle_life = Column(Integer)  # ciclos
    dod = Column(Float)  # % Profundidad de descarga
    calendar_life = Column(Integer)  # años
    warranty_years = Column(Integer)
    warranty_cycles = Column(Integer)
    
    # Características físicas
    width = Column(Float)  # mm
    height = Column(Float)  # mm
    depth = Column(Float)  # mm
    weight = Column(Float)  # kg
    ip_rating = Column(String(10))
    
    # Condiciones ambientales
    temp_min = Column(Float)  # °C
    temp_max = Column(Float)  # °C
    humidity_max = Column(Float)  # %
    altitude_max = Column(Float)  # m
    
    # Sistema de gestión
    bms_included = Column(Boolean)
    monitoring = Column(String(100))
    communication = Column(JSON)  # Protocolos de comunicación
    
    created_at = Column(DateTime, default=datetime.utcnow)
    manufacturer = db.relationship('Manufacturer', backref='batteries')

    def to_dict(self):
        return {
            'id': self.id,
            'manufacturer': self.manufacturer.to_dict(),
            'model': self.model,
            'chemistry': self.chemistry.value,
            'electrical': {
                'nominal_voltage': self.nominal_voltage,
                'capacity': {
                    'nominal': self.nominal_capacity,
                    'usable': self.usable_capacity
                },
                'energy': {
                    'nominal': self.nominal_energy,
                    'usable': self.usable_energy
                },
                'round_trip_efficiency': self.round_trip_efficiency
            },
            'power': {
                'charge': {
                    'max_power': self.max_charge_power,
                    'max_current': self.max_charge_current
                },
                'discharge': {
                    'max_power': self.max_discharge_power,
                    'max_current': self.max_discharge_current
                }
            },
            'lifetime': {
                'cycles': self.cycle_life,
                'dod': self.dod,
                'calendar_years': self.calendar_life,
                'warranty': {
                    'years': self.warranty_years,
                    'cycles': self.warranty_cycles
                }
            },
            'physical': {
                'dimensions': {
                    'width': self.width,
                    'height': self.height,
                    'depth': self.depth
                },
                'weight': self.weight,
                'ip_rating': self.ip_rating
            },
            'environmental': {
                'temperature': {
                    'min': self.temp_min,
                    'max': self.temp_max
                },
                'humidity_max': self.humidity_max,
                'altitude_max': self.altitude_max
            },
            'management': {
                'bms_included': self.bms_included,
                'monitoring': self.monitoring,
                'communication': self.communication
            }
        }

class MountingStructure(db.Model):
    """Estructuras de montaje"""
    __tablename__ = 'mounting_structures'
    
    id = Column(Integer, primary_key=True)
    manufacturer_id = Column(Integer, ForeignKey('manufacturers.id'), nullable=False)
    model = Column(String(100), nullable=False)
    type = Column(SQLEnum(MountingType), nullable=False)
    
    # Características mecánicas
    material = Column(String(50))  # Aluminio, acero galvanizado, etc.
    coating = Column(String(50))  # Tipo de recubrimiento
    wind_speed_max = Column(Float)  # km/h
    snow_load_max = Column(Float)  # kN/m²
    
    # Configuración de montaje
    tilt_angle_min = Column(Float)  # grados
    tilt_angle_max = Column(Float)  # grados
    adjustable_tilt = Column(Boolean, default=False)
    rail_spacing_min = Column(Float)  # mm
    rail_spacing_max = Column(Float)  # mm
    
    # Seguimiento solar (si aplica)
    tracking_type = Column(String(50))  # Ninguno, 1 eje, 2 ejes
    tracking_range = Column(JSON)  # {horizontal: float, vertical: float}
    backtracking = Column(Boolean, default=False)
    motor_type = Column(String(50))
    
    # Compatibilidad
    module_compatibility = Column(JSON)  # Lista de tipos/tamaños de módulos compatibles
    roof_types = Column(JSON)  # Lista de tipos de techo compatibles
    
    # Instalación
    tools_required = Column(JSON)  # Lista de herramientas necesarias
    grounding_method = Column(String(100))
    wire_management = Column(Boolean, default=True)
    estimated_install_time = Column(Float)  # horas por kW
    
    # Certificaciones y garantías
    wind_certifications = Column(JSON)
    structural_certifications = Column(JSON)
    warranty_structure = Column(Integer)  # años
    warranty_coating = Column(Integer)  # años
    
    # Documentación
    datasheet_url = Column(String(200))
    installation_manual_url = Column(String(200))
    
    created_at = Column(DateTime, default=datetime.utcnow)
    manufacturer = db.relationship('Manufacturer', backref='mounting_structures')

    def to_dict(self):
        return {
            'id': self.id,
            'manufacturer': self.manufacturer.to_dict(),
            'model': self.model,
            'type': self.type.value,
            'mechanical': {
                'material': self.material,
                'coating': self.coating,
                'wind_speed_max': self.wind_speed_max,
                'snow_load_max': self.snow_load_max
            },
            'mounting': {
                'tilt_angle': {
                    'min': self.tilt_angle_min,
                    'max': self.tilt_angle_max,
                    'adjustable': self.adjustable_tilt
                },
                'rail_spacing': {
                    'min': self.rail_spacing_min,
                    'max': self.rail_spacing_max
                }
            },
            'tracking': {
                'type': self.tracking_type,
                'range': self.tracking_range,
                'backtracking': self.backtracking,
                'motor_type': self.motor_type
            },
            'compatibility': {
                'modules': self.module_compatibility,
                'roof_types': self.roof_types
            },
            'installation': {
                'tools_required': self.tools_required,
                'grounding_method': self.grounding_method,
                'wire_management': self.wire_management,
                'estimated_install_time': self.estimated_install_time
            },
            'certifications': {
                'wind': self.wind_certifications,
                'structural': self.structural_certifications
            },
            'warranty': {
                'structure_years': self.warranty_structure,
                'coating_years': self.warranty_coating
            },
            'documentation': {
                'datasheet': self.datasheet_url,
                'installation_manual': self.installation_manual_url
            }
        }

class ShadowAnalysis(db.Model):
    """Análisis de sombras para sistemas fotovoltaicos"""
    __tablename__ = 'shadow_analyses'
    
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, nullable=False)
    annual_shading_loss = Column(Float)  # % pérdida anual por sombras
    monthly_shading_losses = Column(JSON)  # {mes: % pérdida}
    hourly_shading_factors = Column(JSON)  # Matriz de factores de sombreado por hora/mes
    obstacles = Column(JSON)  # Lista de obstáculos {tipo, dimensiones, posición}
    horizon_profile = Column(JSON)  # Perfil del horizonte {azimuth: elevación}
    shadow_maps = Column(JSON)  # Mapas de sombras por mes/hora
    sun_path_diagram = Column(JSON)  # Diagrama de trayectoria solar con obstáculos
    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'project_id': self.project_id,
            'annual_shading_loss': self.annual_shading_loss,
            'monthly_shading_losses': self.monthly_shading_losses,
            'hourly_shading_factors': self.hourly_shading_factors,
            'obstacles': self.obstacles,
            'horizon_profile': self.horizon_profile,
            'shadow_maps': self.shadow_maps,
            'sun_path_diagram': self.sun_path_diagram,
            'created_at': self.created_at.isoformat()
        }
