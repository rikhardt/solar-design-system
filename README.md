# Sistema de Diseño Solar Fotovoltaico

Sistema para dimensionamiento y diseño de instalaciones solares fotovoltaicas.

## Características Principales

- Gestión de componentes fotovoltaicos (paneles, inversores, baterías, estructuras)
- Análisis de sombras y optimización de rendimiento
- Base de datos verificada de fabricantes y equipos
- API REST para integración con otros sistemas

## Estructura del Proyecto

```
solar-design-system/
├── backend/
│   ├── src/
│   │   ├── modules/
│   │   │   ├── auth/         # Autenticación y usuarios
│   │   │   ├── components/   # Gestión de componentes
│   │   │   ├── projects/     # Gestión de proyectos
│   │   │   ├── simulation/   # Cálculos y simulaciones
│   │   │   └── weather/      # Datos meteorológicos
│   │   └── templates/        # Plantillas de correo
│   ├── migrations/           # Migraciones de base de datos
│   └── tests/               # Pruebas unitarias
```

## Modelos de Datos

### Manufacturers (Fabricantes)
```json
{
  "id": 1,
  "name": "SolarTech Industries",
  "country": "España",
  "website": "https://solartech.es",
  "description": "Fabricante líder de componentes solares"
}
```

### SolarPanels (Paneles Solares)
```json
{
  "id": 1,
  "manufacturer": { ... },
  "model": "ST-400W-MH",
  "technology": "Monocristalino HJT",
  "electrical": {
    "nominal_power": 400.0,
    "mpp": {
      "voltage": 37.2,
      "current": 10.75
    },
    "voc": 45.6,
    "isc": 11.2,
    "efficiency": 21.5
  }
}
```

### Inverters (Inversores)
```json
{
  "id": 1,
  "manufacturer": { ... },
  "model": "ST-10K-TL",
  "type": "String",
  "dc_input": {
    "max_power": 15000,
    "max_voltage": 1000,
    "mppt_range": {
      "min": 200,
      "max": 800
    }
  }
}
```

### Batteries (Baterías)
```json
{
  "id": 1,
  "manufacturer": { ... },
  "model": "ST-10K-LFP",
  "chemistry": "Litio ferro fosfato",
  "electrical": {
    "nominal_voltage": 51.2,
    "capacity": {
      "nominal": 200.0,
      "usable": 180.0
    }
  }
}
```

### MountingStructures (Estructuras de Montaje)
```json
{
  "id": 1,
  "manufacturer": { ... },
  "model": "ST-GROUND-1A",
  "type": "Seguidor 1 eje",
  "mechanical": {
    "material": "Acero galvanizado",
    "wind_speed_max": 140
  }
}
```

### ShadowAnalysis (Análisis de Sombras)
```json
{
  "id": 1,
  "project_id": 1,
  "annual_shading_loss": 3.5,
  "monthly_shading_losses": {
    "enero": 4.2,
    "febrero": 3.8,
    "marzo": 3.3
  }
}
```

## API Endpoints

### Componentes

#### GET /api/components/manufacturers
Lista todos los fabricantes registrados.

#### GET /api/components/panels
Lista todos los paneles solares disponibles.

#### GET /api/components/inverters 
Lista todos los inversores disponibles.

#### GET /api/components/batteries
Lista todas las baterías disponibles.

#### GET /api/components/mounting-structures
Lista todas las estructuras de montaje disponibles.

#### GET /api/components/shadow-analyses
Lista todos los análisis de sombras realizados.

## Instalación y Configuración

1. Clonar el repositorio:
```bash
git clone https://github.com/username/solar-design-system.git
cd solar-design-system
```

2. Crear y activar entorno virtual:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

3. Instalar dependencias:
```bash
pip install -r requirements.txt
```

4. Configurar variables de entorno:
```bash
cp .env.example .env
# Editar .env con las configuraciones necesarias
```

5. Inicializar la base de datos:
```bash
flask db upgrade
```

6. Cargar datos de prueba:
```bash
python tests/test_data.py
```

7. Ejecutar el servidor:
```bash
flask run
```

## Uso de la API

### Ejemplo de consulta con curl:

```bash
# Listar fabricantes
curl -H "Accept: application/json" http://localhost:5000/api/components/manufacturers

# Listar paneles solares
curl -H "Accept: application/json" http://localhost:5000/api/components/panels
```

### Ejemplo de respuesta:

```json
{
  "manufacturers": [
    {
      "id": 1,
      "name": "SolarTech Industries",
      "country": "España",
      "website": "https://solartech.es"
    }
  ]
}
```

## Tecnologías Utilizadas

- Backend: Python/Flask
- Base de datos: SQLite (desarrollo), PostgreSQL (producción)
- ORM: SQLAlchemy
- Migraciones: Alembic
- Documentación: OpenAPI/Swagger

## Desarrollo

### Crear nuevas migraciones:

```bash
flask db migrate -m "descripción de los cambios"
flask db upgrade
```

### Ejecutar pruebas:

```bash
python -m pytest
```

## Contribuciones

1. Fork el repositorio
2. Crear una rama para la nueva funcionalidad
3. Commit los cambios
4. Push a la rama
5. Crear un Pull Request

## Licencia

Este proyecto está licenciado bajo MIT License.
