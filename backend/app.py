import os
from src import create_app, db

app = create_app(os.getenv('FLASK_ENV', 'development'))

@app.shell_context_processor
def make_shell_context():
    """Configura el contexto del shell de Flask"""
    from src.modules.components.models import (
        Manufacturer, SolarPanel, Inverter, Battery, MountingSystem,
        ModuleTechnology, InverterType, BatteryChemistry, MountingType
    )
    
    return {
        'db': db,
        'Manufacturer': Manufacturer,
        'SolarPanel': SolarPanel,
        'Inverter': Inverter,
        'Battery': Battery,
        'MountingSystem': MountingSystem,
        'ModuleTechnology': ModuleTechnology,
        'InverterType': InverterType,
        'BatteryChemistry': BatteryChemistry,
        'MountingType': MountingType
    }

if __name__ == '__main__':
    app.run(debug=True)
