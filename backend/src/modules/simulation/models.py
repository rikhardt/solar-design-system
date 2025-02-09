from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, JSON, Text, Boolean
from sqlalchemy.orm import relationship
from src.database import Base
from src.modules.components.models import SolarPanel, Inverter, Battery, MountingStructure

class Project(Base):
    """Modelo para proyectos fotovoltaicos"""
    __tablename__ = 'projects'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Ubicación y condiciones del sitio
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    altitude = Column(Float)
    terrain_type = Column(String(50))  # plano, inclinado, irregular
    albedo = Column(Float, default=0.2)  # reflectividad del suelo
    
    # Relaciones con componentes
    panel_id = Column(Integer, ForeignKey('solar_panels.id'))
    inverter_id = Column(Integer, ForeignKey('inverters.id'))
    battery_id = Column(Integer, ForeignKey('batteries.id'))
    structure_id = Column(Integer, ForeignKey('mounting_structures.id'))
    
    panel = relationship("SolarPanel")
    inverter = relationship("Inverter")
    battery = relationship("Battery")
    structure = relationship("MountingStructure")
    
    # Configuración del sistema
    system_type = Column(String(50))  # grid-tied, off-grid, híbrido
    system_capacity = Column(Float)  # kWp
    module_count = Column(Integer)
    inverter_count = Column(Integer)
    battery_count = Column(Integer)
    
    # Parámetros de diseño
    tilt_angle = Column(Float)  # grados
    azimuth_angle = Column(Float)  # grados
    ground_coverage_ratio = Column(Float)
    row_spacing = Column(Float)  # metros
    use_tracking = Column(Boolean, default=False)
    tracking_type = Column(String(50))  # single-axis, dual-axis
    
    # Configuración de consumo
    load_profile = Column(JSON)  # perfil de consumo horario
    annual_consumption = Column(Float)  # kWh/año
    peak_demand = Column(Float)  # kW
    
    # Restricciones
    area_available = Column(Float)  # m²
    budget_limit = Column(Float)  # USD
    grid_connection_limit = Column(Float)  # kW
    
    # Resultados de simulación (relación uno a muchos)
    simulation_results = relationship("SimulationResult", back_populates="project")
    shadow_analysis = relationship("ShadowAnalysis", back_populates="project")

class SimulationResult(Base):
    """Modelo para resultados de simulación"""
    __tablename__ = 'simulation_results'
    
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey('projects.id'))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Producción energética
    annual_production = Column(Float)  # kWh/año
    monthly_production = Column(JSON)  # kWh/mes
    hourly_production = Column(JSON)  # kWh/hora
    specific_yield = Column(Float)  # kWh/kWp
    performance_ratio = Column(Float)
    capacity_factor = Column(Float)
    
    # Pérdidas detalladas
    losses = Column(JSON)  # {
                         #   "soiling": float,
                         #   "shading": float,
                         #   "reflection": float,
                         #   "spectral": float,
                         #   "temperature": float,
                         #   "mismatch": float,
                         #   "wiring": float,
                         #   "inverter": float,
                         #   "availability": float
                         # }
    
    # Análisis económico
    total_cost = Column(Float)  # USD
    component_costs = Column(JSON)  # Desglose de costos
    operation_maintenance_cost = Column(Float)  # USD/año
    lcoe = Column(Float)  # USD/kWh
    payback_period = Column(Float)  # años
    internal_rate_return = Column(Float)  # %
    net_present_value = Column(Float)  # USD
    
    # Impacto ambiental
    co2_avoided = Column(Float)  # toneladas/año
    environmental_benefits = Column(JSON)  # Otros beneficios ambientales
    
    project = relationship("Project", back_populates="simulation_results")

class ShadowAnalysis(Base):
    """Modelo para análisis de sombras"""
    __tablename__ = 'shadow_analysis'
    
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey('projects.id'))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Análisis de sombras
    annual_shading_loss = Column(Float)  # %
    monthly_shading_losses = Column(JSON)  # % por mes
    hourly_shading_factors = Column(JSON)  # Factores de sombreado por hora
    
    # Obstáculos
    obstacles = Column(JSON)  # Lista de obstáculos y sus dimensiones
    horizon_profile = Column(JSON)  # Perfil del horizonte
    
    # Resultados 3D
    shadow_maps = Column(JSON)  # Mapas de sombras para diferentes momentos
    sun_path_diagram = Column(JSON)  # Diagrama de trayectoria solar
    
    project = relationship("Project", back_populates="shadow_analysis")

    def to_dict(self):
        """Convierte el modelo a diccionario para la API"""
        return {
            'id': self.id,
            'project_id': self.project_id,
            'created_at': self.created_at.isoformat(),
            'annual_shading_loss': self.annual_shading_loss,
            'monthly_shading_losses': self.monthly_shading_losses,
            'hourly_shading_factors': self.hourly_shading_factors,
            'obstacles': self.obstacles,
            'horizon_profile': self.horizon_profile,
            'shadow_maps': self.shadow_maps,
            'sun_path_diagram': self.sun_path_diagram
        }
