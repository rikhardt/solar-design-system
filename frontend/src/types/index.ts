// Interfaces de Usuario
export interface User {
  id: number;
  email: string;
  name: string;
}

// Interfaces de Autenticación
export interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  loading: boolean;
  error: string | null;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterData extends LoginCredentials {
  name: string;
}

// Interfaces de Proyecto Solar
export interface SolarProject {
  id: number;
  name: string;
  description: string;
  location: {
    latitude: number;
    longitude: number;
  };
  createdAt: string;
  updatedAt: string;
  components: SolarComponent[];
  simulationResults?: SimulationResult;
}

// Interfaces de Componentes
export interface SolarComponent {
  id: number;
  type: 'panel' | 'inverter' | 'battery';
  manufacturer: string;
  model: string;
  specifications: {
    [key: string]: number | string;
  };
}

// Interfaces de Simulación
export interface SimulationResult {
  energyProduction: number;
  efficiency: number;
  co2Savings: number;
  roi: number;
  paybackPeriod: number;
  monthlyProduction: MonthlyProduction[];
}

export interface MonthlyProduction {
  month: string;
  production: number;
  consumption: number;
}

// Interfaces de Datos Meteorológicos
export interface WeatherData {
  location: string;
  timestamp: string;
  temperature: number;
  irradiance: number;
  humidity: number;
  windSpeed: number;
}

// Interfaces de Respuesta API
export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
}
