import React, { useState } from 'react';
import {
  Box,
  Tabs,
  Tab,
  Card,
  CardContent,
  CardActions,
  Button,
  Typography,
  Grid,
  Chip,
  TextField,
  InputAdornment
} from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import { Component } from '../../types/project';

interface ComponentCatalogProps {
  onComponentSelect: (component: Component) => void;
}

// Datos de ejemplo - En una implementación real, esto vendría de una API
const sampleComponents: Component[] = [
  {
    id: '1',
    type: 'panel',
    manufacturer: 'SunPower',
    model: 'SPR-X22-360',
    specifications: {
      power: 360,
      efficiency: 22.7,
      warranty: 25,
      dimensions: '1046x1690x40',
      weight: 18.6
    }
  },
  {
    id: '2',
    type: 'inverter',
    manufacturer: 'SMA',
    model: 'Sunny Boy 5.0',
    specifications: {
      power: 5000,
      efficiency: 97.6,
      warranty: 10,
      mpptChannels: 2,
      maxVoltage: 600
    }
  },
  {
    id: '3',
    type: 'battery',
    manufacturer: 'Tesla',
    model: 'Powerwall 2',
    specifications: {
      capacity: 13.5,
      power: 7,
      warranty: 10,
      dimensions: '1150x755x155',
      weight: 114
    }
  }
];

const ComponentCatalog: React.FC<ComponentCatalogProps> = ({ onComponentSelect }) => {
  const [activeTab, setActiveTab] = useState<'panel' | 'inverter' | 'battery'>('panel');
  const [searchTerm, setSearchTerm] = useState('');

  const handleTabChange = (event: React.SyntheticEvent, newValue: 'panel' | 'inverter' | 'battery') => {
    setActiveTab(newValue);
  };

  const filteredComponents = sampleComponents.filter(component => 
    component.type === activeTab &&
    (component.manufacturer.toLowerCase().includes(searchTerm.toLowerCase()) ||
     component.model.toLowerCase().includes(searchTerm.toLowerCase()))
  );

  const renderSpecifications = (specs: { [key: string]: number | string }) => {
    return Object.entries(specs).map(([key, value]) => (
      <Chip
        key={key}
        label={`${key}: ${value}`}
        size="small"
        sx={{ m: 0.5 }}
      />
    ));
  };

  return (
    <Box>
      <Tabs
        value={activeTab}
        onChange={handleTabChange}
        variant="fullWidth"
        sx={{ mb: 2 }}
      >
        <Tab label="Paneles Solares" value="panel" />
        <Tab label="Inversores" value="inverter" />
        <Tab label="Baterías" value="battery" />
      </Tabs>

      <TextField
        fullWidth
        variant="outlined"
        placeholder="Buscar por fabricante o modelo..."
        value={searchTerm}
        onChange={(e) => setSearchTerm(e.target.value)}
        sx={{ mb: 2 }}
        InputProps={{
          startAdornment: (
            <InputAdornment position="start">
              <SearchIcon />
            </InputAdornment>
          ),
        }}
      />

      <Grid container spacing={2}>
        {filteredComponents.map((component) => (
          <Grid item xs={12} sm={6} key={component.id}>
            <Card variant="outlined">
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  {component.manufacturer} {component.model}
                </Typography>
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                  {renderSpecifications(component.specifications)}
                </Box>
              </CardContent>
              <CardActions>
                <Button
                  size="small"
                  variant="contained"
                  onClick={() => onComponentSelect(component)}
                >
                  Seleccionar
                </Button>
              </CardActions>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Box>
  );
};

export default ComponentCatalog;
