import React from 'react';
import {
  Box,
  Typography,
  Grid,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow
} from '@mui/material';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts';
import { Component } from '../../types/project';

interface EconomicAnalysisProps {
  selectedComponents: Component[];
  systemSize?: number; // en kW
}

interface CostBreakdown {
  category: string;
  cost: number;
  percentage: number;
}

const calculateCosts = (components: Component[]): CostBreakdown[] => {
  const totalComponentCost = components.reduce((acc, component) => {
    // Costos estimados por tipo de componente
    const costs = {
      panel: 300, // USD por panel
      inverter: 1000, // USD por inversor
      battery: 7000 // USD por batería
    };
    return acc + costs[component.type];
  }, 0);

  const installationCost = totalComponentCost * 0.3; // 30% del costo de componentes
  const designCost = totalComponentCost * 0.1; // 10% del costo de componentes
  const total = totalComponentCost + installationCost + designCost;

  return [
    {
      category: 'Componentes',
      cost: totalComponentCost,
      percentage: (totalComponentCost / total) * 100
    },
    {
      category: 'Instalación',
      cost: installationCost,
      percentage: (installationCost / total) * 100
    },
    {
      category: 'Diseño e Ingeniería',
      cost: designCost,
      percentage: (designCost / total) * 100
    }
  ];
};

const generateROIData = (totalCost: number, systemSize: number = 10) => {
  const yearlyProduction = systemSize * 1600; // kWh por año (estimado)
  const electricityPrice = 0.15; // USD por kWh
  const yearlyRevenue = yearlyProduction * electricityPrice;
  
  return Array.from({ length: 26 }, (_, year) => ({
    year,
    balance: -totalCost + yearlyRevenue * year,
    production: yearlyProduction
  }));
};

const EconomicAnalysis: React.FC<EconomicAnalysisProps> = ({
  selectedComponents,
  systemSize = 10
}) => {
  const costBreakdown = calculateCosts(selectedComponents);
  const totalCost = costBreakdown.reduce((acc, item) => acc + item.cost, 0);
  const roiData = generateROIData(totalCost, systemSize);
  const paybackYear = roiData.find(data => data.balance > 0)?.year || 0;

  return (
    <Box>
      <Grid container spacing={3}>
        {/* Resumen de Costos */}
        <Grid item xs={12}>
          <TableContainer component={Paper} variant="outlined">
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Categoría</TableCell>
                  <TableCell align="right">Costo (USD)</TableCell>
                  <TableCell align="right">Porcentaje</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {costBreakdown.map((row) => (
                  <TableRow key={row.category}>
                    <TableCell>{row.category}</TableCell>
                    <TableCell align="right">
                      ${row.cost.toLocaleString()}
                    </TableCell>
                    <TableCell align="right">
                      {row.percentage.toFixed(1)}%
                    </TableCell>
                  </TableRow>
                ))}
                <TableRow>
                  <TableCell><strong>Total</strong></TableCell>
                  <TableCell align="right">
                    <strong>${totalCost.toLocaleString()}</strong>
                  </TableCell>
                  <TableCell align="right">100%</TableCell>
                </TableRow>
              </TableBody>
            </Table>
          </TableContainer>
        </Grid>

        {/* Gráfico ROI */}
        <Grid item xs={12}>
          <Typography variant="subtitle1" gutterBottom>
            Retorno de Inversión Proyectado
          </Typography>
          <Typography variant="body2" gutterBottom color="text.secondary">
            Tiempo estimado de recuperación: {paybackYear} años
          </Typography>
          <Box sx={{ height: 300 }}>
            <ResponsiveContainer width="100%" height="100%">
              <LineChart
                data={roiData}
                margin={{
                  top: 5,
                  right: 30,
                  left: 20,
                  bottom: 5,
                }}
              >
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis 
                  dataKey="year" 
                  label={{ 
                    value: 'Años', 
                    position: 'insideBottom', 
                    offset: -5 
                  }} 
                />
                <YAxis 
                  label={{ 
                    value: 'Balance (USD)', 
                    angle: -90, 
                    position: 'insideLeft' 
                  }} 
                />
                <Tooltip />
                <Legend />
                <Line
                  type="monotone"
                  dataKey="balance"
                  name="Balance Neto"
                  stroke="#8884d8"
                  activeDot={{ r: 8 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </Box>
        </Grid>
      </Grid>
    </Box>
  );
};

export default EconomicAnalysis;
