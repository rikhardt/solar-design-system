from src import create_app, db
from src.modules.components.models import (
    Manufacturer, SolarPanel, Inverter, Battery, 
    MountingStructure, ShadowAnalysis,
    ModuleTechnology, InverterType, BatteryChemistry, MountingType
)

def create_test_data():
    app = create_app('development')
    with app.app_context():
        # Crear usuario de prueba
        from src.modules.auth.models import User
        from src.modules.projects.models import Project
        
        user = User(
            username='test_user',
            email='test@example.com',
            role='engineer'
        )
        user.password = 'test123'
        db.session.add(user)
        db.session.commit()

        # Crear proyecto de prueba
        project = Project(
            name='Instalación Solar Residencial',
            description='Proyecto piloto de energía solar',
            location={
                'lat': -33.4489,
                'lon': -70.6693,
                'address': 'Av. Principal 123',
                'city': 'Santiago',
                'country': 'Chile'
            },
            system_size=10.5,
            type='residencial',
            status='active',
            owner_id=user.id
        )
        db.session.add(project)
        db.session.commit()

        # Crear fabricante
        manufacturer = Manufacturer(
            name="SolarTech Industries",
            country="España",
            website="https://solartech.es",
            description="Fabricante líder de componentes solares"
        )
        db.session.add(manufacturer)
        db.session.commit()

        # Crear panel solar
        panel = SolarPanel(
            manufacturer_id=manufacturer.id,
            model="ST-400W-MH",
            technology=ModuleTechnology.MONO_HJT,
            nominal_power=400.0,
            voltage_mpp=37.2,
            current_mpp=10.75,
            voltage_oc=45.6,
            current_sc=11.2,
            efficiency=21.5,
            temp_coefficient_pmax=-0.26,
            length=1765,
            width=1048,
            thickness=35,
            weight=21.5,
            cells_count=120,
            warranty_product=25,
            warranty_power_80=30,
            certificates=["IEC 61215", "IEC 61730"]
        )
        db.session.add(panel)

        # Crear inversor
        inverter = Inverter(
            manufacturer_id=manufacturer.id,
            model="ST-10K-TL",
            type=InverterType.STRING,
            max_power_dc=15000,
            max_voltage_dc=1000,
            mppt_voltage_min=200,
            mppt_voltage_max=800,
            max_current_dc=25,
            mppt_count=2,
            nominal_power_ac=10000,
            max_efficiency=98.3,
            ip_rating="IP65"
        )
        db.session.add(inverter)

        # Crear batería
        battery = Battery(
            manufacturer_id=manufacturer.id,
            model="ST-10K-LFP",
            chemistry=BatteryChemistry.LFP,
            nominal_voltage=51.2,
            nominal_capacity=200,
            usable_capacity=180,
            nominal_energy=10.24,
            round_trip_efficiency=96.0,
            cycle_life=6000,
            warranty_years=10
        )
        db.session.add(battery)

        # Crear estructura de montaje
        structure = MountingStructure(
            manufacturer_id=manufacturer.id,
            model="ST-GROUND-1A",
            type=MountingType.TRACKER_1AXIS,
            material="Acero galvanizado",
            wind_speed_max=140,
            tilt_angle_min=0,
            tilt_angle_max=60,
            tracking_type="1 eje horizontal",
            backtracking=True
        )
        db.session.add(structure)

        # Crear análisis de sombras
        shadow = ShadowAnalysis(
            project_id=1,
            annual_shading_loss=3.5,
            monthly_shading_losses={
                "enero": 4.2,
                "febrero": 3.8,
                "marzo": 3.3
            },
            obstacles=[{
                "tipo": "edificio",
                "altura": 15,
                "distancia": 20,
                "azimuth": 180
            }]
        )
        db.session.add(shadow)

        # Guardar todos los cambios
        db.session.commit()

        print("Datos de prueba creados exitosamente")

if __name__ == "__main__":
    create_test_data()
