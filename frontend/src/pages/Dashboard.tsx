import React, { useState } from 'react';
import { 
  Box, 
  Container, 
  Grid, 
  Paper, 
  Typography, 
  Slider, 
  List,
  ListItem,
  ListItemText,
  IconButton
} from '@mui/material';
import DeleteIcon from '@mui/icons-material/Delete';
import DataEntryForm from '../components/projects/DataEntryForm';
import ThreeJSViewer from '../components/visualization/ThreeJSViewer';
import ComponentCatalog from '../components/catalog/ComponentCatalog';
import { Location, SystemConstraints, Component } from '../types/project';
import EconomicAnalysis from '../components/analysis/EconomicAnalysis';
import SimulationResults from '../components/simulation/SimulationResults';
import { styled } from '@mui/material/styles';

const calculateSystemSize = (components: Component[]): number => {
  const panels = components.filter(c => c.type === 'panel');
  // Asumiendo paneles de 360W en promedio
  return (panels.length * 0.360); // Tamaño del sistema en kW
};

const Item = styled(Paper)(({ theme }) => ({
  backgroundColor: theme.palette.mode === 'dark' ? '#1A2027' : '#fff',
  ...theme.typography.body2,
  padding: theme.spacing(2),
  color: theme.palette.text.secondary,
}));

const Dashboard: React.FC = () => {
  const [location, setLocation] = useState<Location | null>(null);
  const [selectedComponents, setSelectedComponents] = useState<Component[]>([]);
  const [systemConstraints, setSystemConstraints] = useState<SystemConstraints>({
    availableArea: 100,
    roofType: 'plano',
    orientation: 0,
    tilt: 30,
    obstacles: []
  });

  const handleAreaChange = (event: Event, newValue: number | number[]) => {
    setSystemConstraints(prev => ({
      ...prev,
      availableArea: newValue as number
    }));
  };

  const handleTiltChange = (event: Event, newValue: number | number[]) => {
    setSystemConstraints(prev => ({
      ...prev,
      tilt: newValue as number
    }));
  };

  const handleLocationChange = (newLocation: Location) => {
    setLocation(newLocation);
    console.log('Nueva ubicación seleccionada:', newLocation);
  };

  return (
    <Container maxWidth="xl">
      <Box sx={{ flexGrow: 1, mt: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Diseño de Sistema Solar Fotovoltaico
        </Typography>
        
        <Grid container spacing={3}>
          {/* Panel de Entrada de Datos */}
          <Grid item xs={12} md={4}>
            <Item>
              <Typography variant="h6" gutterBottom>
                Datos de Entrada
              </Typography>
              <DataEntryForm onLocationChange={handleLocationChange} />
            </Item>
          </Grid>

          {/* Visualización 3D / Mapa */}
          <Grid item xs={12} md={8}>
            <Item sx={{ height: '500px' }}>
              <Typography variant="h6" gutterBottom>
                Visualización del Sistema
              </Typography>
              <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
                <Box sx={{ mb: 2 }}>
                  <Typography gutterBottom>Área Disponible (m²)</Typography>
                  <Slider
                    value={systemConstraints.availableArea}
                    onChange={handleAreaChange}
                    min={10}
                    max={500}
                    valueLabelDisplay="auto"
                  />
                  <Typography gutterBottom>Inclinación (grados)</Typography>
                  <Slider
                    value={systemConstraints.tilt}
                    onChange={handleTiltChange}
                    min={0}
                    max={45}
                    valueLabelDisplay="auto"
                  />
                </Box>
                <Box sx={{ flexGrow: 1 }}>
                  <ThreeJSViewer systemConstraints={systemConstraints} />
                </Box>
              </Box>
            </Item>
          </Grid>

          {/* Catálogo de Componentes */}
          <Grid item xs={12} md={6}>
            <Item>
              <Typography variant="h6" gutterBottom>
                Catálogo de Componentes
              </Typography>
              <ComponentCatalog 
                onComponentSelect={(component) => {
                  setSelectedComponents(prev => [...prev, component]);
                }}
              />
              {selectedComponents.length > 0 && (
                <Box sx={{ mt: 2 }}>
                  <Typography variant="subtitle1" gutterBottom>
                    Componentes Seleccionados
                  </Typography>
                  <List>
                    {selectedComponents.map((component, index) => (
                      <ListItem
                        key={`${component.id}-${index}`}
                        secondaryAction={
                          <IconButton 
                            edge="end" 
                            aria-label="delete"
                            onClick={() => {
                              setSelectedComponents(prev => 
                                prev.filter((_, i) => i !== index)
                              );
                            }}
                          >
                            <DeleteIcon />
                          </IconButton>
                        }
                      >
                        <ListItemText
                          primary={`${component.manufacturer} ${component.model}`}
                          secondary={`Tipo: ${component.type}`}
                        />
                      </ListItem>
                    ))}
                  </List>
                </Box>
              )}
            </Item>
          </Grid>

          {/* Análisis Económico */}
          <Grid item xs={12} md={6}>
            <Item>
              <Typography variant="h6" gutterBottom>
                Análisis Económico
              </Typography>
              <EconomicAnalysis 
                selectedComponents={selectedComponents}
                systemSize={calculateSystemSize(selectedComponents)}
              />
            </Item>
          </Grid>

          {/* Resultados de Simulación */}
          <Grid item xs={12}>
            <Item>
              <Typography variant="h6" gutterBottom>
                Resultados de Simulación
              </Typography>
              <SimulationResults 
                selectedComponents={selectedComponents}
                systemConstraints={systemConstraints}
                location={location}
              />
            </Item>
          </Grid>
        </Grid>
      </Box>
    </Container>
  );
};

export default Dashboard;
