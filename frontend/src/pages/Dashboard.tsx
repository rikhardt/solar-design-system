import React, { useEffect, useState } from 'react';
import {
  Grid,
  Card,
  CardContent,
  Typography,
  Box,
  CircularProgress,
  Paper
} from '@mui/material';
import {
  SolarPower,
  Cloud,
  Battery90,
  TrendingUp
} from '@mui/icons-material';
import { SolarProject, WeatherData } from '../types';

const Dashboard: React.FC = () => {
  const [loading, setLoading] = useState(true);
  const [projects, setProjects] = useState<SolarProject[]>([]);
  const [weatherData, setWeatherData] = useState<WeatherData | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        // TODO: Implementar llamadas a la API real
        // Simulación de datos para la demo
        setTimeout(() => {
          setProjects([
            {
              id: 1,
              name: 'Proyecto Solar Residencial',
              description: 'Sistema fotovoltaico para vivienda',
              location: { latitude: -33.4569, longitude: -70.6483 },
              createdAt: new Date().toISOString(),
              updatedAt: new Date().toISOString(),
              components: []
            }
          ]);
          
          setWeatherData({
            location: 'Santiago, Chile',
            timestamp: new Date().toISOString(),
            temperature: 25,
            irradiance: 850,
            humidity: 45,
            windSpeed: 10
          });
          
          setLoading(false);
        }, 1000);
      } catch (error) {
        console.error('Error al cargar datos:', error);
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
        <CircularProgress />
      </Box>
    );
  }

  const DashboardCard = ({ title, value, icon, color }: any) => (
    <Card sx={{ height: '100%' }}>
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          {icon}
          <Typography variant="h6" component="div" sx={{ ml: 1 }}>
            {title}
          </Typography>
        </Box>
        <Typography variant="h4" component="div" color={color}>
          {value}
        </Typography>
      </CardContent>
    </Card>
  );

  return (
    <Box sx={{ flexGrow: 1 }}>
      <Typography variant="h4" gutterBottom>
        Dashboard
      </Typography>

      <Grid container spacing={3}>
        <Grid item xs={12} sm={6} md={3}>
          <DashboardCard
            title="Proyectos Activos"
            value={projects.length}
            icon={<SolarPower color="primary" />}
            color="primary"
          />
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <DashboardCard
            title="Temperatura"
            value={`${weatherData?.temperature}°C`}
            icon={<Cloud color="info" />}
            color="info"
          />
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <DashboardCard
            title="Irradiancia"
            value={`${weatherData?.irradiance} W/m²`}
            icon={<TrendingUp color="warning" />}
            color="warning"
          />
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <DashboardCard
            title="Eficiencia"
            value="95%"
            icon={<Battery90 color="success" />}
            color="success"
          />
        </Grid>

        <Grid item xs={12}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Proyectos Recientes
            </Typography>
            {projects.map((project) => (
              <Box key={project.id} sx={{ mb: 2 }}>
                <Typography variant="subtitle1">{project.name}</Typography>
                <Typography variant="body2" color="text.secondary">
                  {project.description}
                </Typography>
              </Box>
            ))}
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Dashboard;
