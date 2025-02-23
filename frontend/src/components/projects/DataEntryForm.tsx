import React, { useState, memo } from 'react';
import { Box, TextField, Grid, Typography, Paper } from '@mui/material';
import { Location } from '../../types/project';
import ProjectMap from './ProjectMap';

type DataEntryFormProps = {
  onLocationChange: (location: Location) => void;
};

const DataEntryForm = memo(({ onLocationChange }: DataEntryFormProps) => {
  const [location, setLocation] = useState<Location>({
    latitude: -33.4489,
    longitude: -70.6693,
    address: '',
  });

  const handleLocationChange = (lat: number, lng: number): void => {
    const newLocation = {
      ...location,
      latitude: lat,
      longitude: lng,
    };
    setLocation(newLocation);
    onLocationChange(newLocation);
  };

  const handleAddressChange = (event: React.ChangeEvent<HTMLInputElement>): void => {
    const newLocation = {
      ...location,
      address: event.target.value,
    };
    setLocation(newLocation);
    onLocationChange(newLocation);
  };

  return (
    <Box component="section">
      <Typography variant="h6" gutterBottom>
        Ubicación del Proyecto
      </Typography>
      
      <Grid container spacing={2}>
        <Grid item xs={12}>
          <TextField
            fullWidth
            label="Dirección"
            value={location.address}
            onChange={handleAddressChange}
            margin="normal"
          />
        </Grid>
        
        <Grid item xs={6}>
          <TextField
            fullWidth
            label="Latitud"
            value={location.latitude}
            InputProps={{ readOnly: true }}
            margin="normal"
          />
        </Grid>
        
        <Grid item xs={6}>
          <TextField
            fullWidth
            label="Longitud"
            value={location.longitude}
            InputProps={{ readOnly: true }}
            margin="normal"
          />
        </Grid>

        <Grid item xs={12}>
          <Paper elevation={3} sx={{ height: '300px', width: '100%' }}>
            <ProjectMap
              location={location}
              onLocationChange={handleLocationChange}
            />
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
});

DataEntryForm.displayName = 'DataEntryForm';

export default DataEntryForm;
