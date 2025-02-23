import React from 'react';
import {
  Box,
  Grid,
  Typography,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow
} from '@mui/material';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts';
import { Component, SystemConstraints } from '../../types/project';

interface SimulationResultsProps {
  selectedComponents: Component[];
  systemConstraints: SystemConstraints;
  location: { latitude: number; longitude: number } | null;
}

const calculateMonthlyProduction = (
  systemSize: number,
  tilt: number,
  latitude: number
): { month: string; production: number }[] => {
  // Factores de producción mensual aproximados (kWh/kWp)
  const baseProduction = [
    { month: 'Ene', factor: 5.2 },
    { month: 'Feb', factor: 4.8 },
    { month: 'Mar', factor: 4.5 },
    { month: 'Abr', factor: 3.8 },
    { month: 'May', factor: 3.0 },
    { month: 'Jun', factor: 2.5 },
    { month: 'Jul', factor: 2.7 },
    { month: 'Ago', factor: 3.3 },
    { month: 'Sep', factor: 4.0 },
    { month: 'Oct', factor: 4.7 },
    { month: 'Nov', factor: 5.0 },
    { month: 'Dic', factor: 5.3 }
  ];

  // Ajuste por inclinación y latitud
  const tiltFactor = Math.cos((tilt - Math.abs(latitude)) * Math.PI / 180);
  
  return baseProduction.map(month => ({
    month: month.month,
    production: Math.round(systemSize * month.factor * tiltFactor * 30) // Producción mensual
  }));
};

const calculatePerformanceMetrics = (
  systemSize: number,
  monthlyProduction: { month: string; production: number }[]
) => {
  const annualProduction = monthlyProduction.reduce((acc, month) => acc + month.production, 0);
  const specificYield = annualProduction / systemSize; // kWh/kWp
  const performanceRatio = 0.8; // Valor típico entre 0.7 y 0.85
  const co2Savings = annualProduction * 0.5; // kg CO2 (factor aproximado)

  return {
    annualProduction,
    specificYield,
    performanceRatio,
    co2Savings
  };
};

const SimulationResults: React.FC<SimulationResultsProps> = ({
  selectedComponents,
  systemConstraints,
  location
}) => {
  const panels = selectedComponents.filter(c => c.type === 'panel');
  const systemSize = panels.length * 0.360; // kW (asumiendo paneles de 360W)
  
  const monthlyProduction = calculateMonthlyProduction(
    systemSize,
    systemConstraints.tilt,
    location?.latitude || -33.4489
  );

  const metrics = calculatePerformanceMetrics(systemSize, monthlyProduction);

  return (
    <Box>
      <Grid container spacing={3}>
        {/* Métricas Principales */}
        <Grid item xs={12}>
          <TableContainer component={Paper} variant="outlined">
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Métrica</TableCell>
                  <TableCell align="right">Valor</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                <TableRow>
                  <TableCell>Potencia Instalada</TableCell>
                  <TableCell align="right">{systemSize.toFixed(2)} kWp</TableCell>
                </TableRow>
                <TableRow>
                  <TableCell>Producción Anual Estimada</TableCell>
                  <TableCell align="right">
                    {metrics.annualProduction.toLocaleString()} kWh
                  </TableCell>
                </TableRow>
                <TableRow>
                  <TableCell>Producción Específica</TableCell>
                  <TableCell align="right">
                    {metrics.specificYield.toFixed(0)} kWh/kWp
                  </TableCell>
                </TableRow>
                <TableRow>
                  <TableCell>Performance Ratio</TableCell>
                  <TableCell align="right">
                    {(metrics.performanceRatio * 100).toFixed(1)}%
                  </TableCell>
                </TableRow>
                <TableRow>
                  <TableCell>Ahorro de CO2 Anual</TableCell>
                  <TableCell align="right">
                    {metrics.co2Savings.toFixed(0)} kg
                  </TableCell>
                </TableRow>
              </TableBody>
            </Table>
          </TableContainer>
        </Grid>

        {/* Gráfico de Producción Mensual */}
        <Grid item xs={12}>
          <Typography variant="subtitle1" gutterBottom>
            Producción Mensual Estimada
          </Typography>
          <Box sx={{ height: 300 }}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                data={monthlyProduction}
                margin={{
                  top: 5,
                  right: 30,
                  left: 20,
                  bottom: 5,
                }}
              >
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="month" />
                <YAxis 
                  label={{ 
                    value: 'Producción (kWh)', 
                    angle: -90, 
                    position: 'insideLeft' 
                  }}
                />
                <Tooltip />
                <Legend />
                <Bar 
                  dataKey="production" 
                  name="Producción" 
                  fill="#2196f3"
                />
              </BarChart>
            </ResponsiveContainer>
          </Box>
        </Grid>
      </Grid>
    </Box>
  );
};

export default SimulationResults;
