import api from './api';
import { WeatherData, ApiResponse } from '../types';

export const weatherService = {
  getCurrentWeather: async (latitude: number, longitude: number): Promise<ApiResponse<WeatherData>> => {
    try {
      const response = await api.get<ApiResponse<WeatherData>>(`/weather/current`, {
        params: { latitude, longitude }
      });
      return response.data;
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.error || 'Error al obtener datos meteorológicos'
      };
    }
  },

  getHistoricalData: async (
    latitude: number, 
    longitude: number, 
    startDate: string, 
    endDate: string
  ): Promise<ApiResponse<WeatherData[]>> => {
    try {
      const response = await api.get<ApiResponse<WeatherData[]>>('/weather/historical', {
        params: {
          latitude,
          longitude,
          startDate,
          endDate
        }
      });
      return response.data;
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.error || 'Error al obtener datos históricos'
      };
    }
  },

  getForecast: async (
    latitude: number,
    longitude: number,
    days: number = 7
  ): Promise<ApiResponse<WeatherData[]>> => {
    try {
      const response = await api.get<ApiResponse<WeatherData[]>>('/weather/forecast', {
        params: {
          latitude,
          longitude,
          days
        }
      });
      return response.data;
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.error || 'Error al obtener pronóstico'
      };
    }
  },

  getIrradianceData: async (
    latitude: number,
    longitude: number,
    date: string
  ): Promise<ApiResponse<{ hourly: number[] }>> => {
    try {
      const response = await api.get<ApiResponse<{ hourly: number[] }>>('/weather/irradiance', {
        params: {
          latitude,
          longitude,
          date
        }
      });
      return response.data;
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.error || 'Error al obtener datos de irradiancia'
      };
    }
  }
};

export default weatherService;
