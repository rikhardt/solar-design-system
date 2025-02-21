import api from './api';
import { ApiResponse, User, LoginCredentials, RegisterData } from '../types';

export const authService = {
  async login(credentials: LoginCredentials): Promise<ApiResponse<{ token: string; user: User }>> {
    try {
      const response = await api.post<ApiResponse<{ token: string; user: User }>>('/auth/login', credentials);
      if (response.data.data) {
        localStorage.setItem('token', response.data.data.token);
      }
      return response.data;
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.error || 'Error al iniciar sesión'
      };
    }
  },

  async register(data: RegisterData): Promise<ApiResponse<User>> {
    try {
      const response = await api.post<ApiResponse<User>>('/auth/register', data);
      return response.data;
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.error || 'Error al registrar usuario'
      };
    }
  },

  async getCurrentUser(): Promise<ApiResponse<User>> {
    try {
      const response = await api.get<ApiResponse<User>>('/auth/me');
      return response.data;
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.error || 'Error al obtener usuario actual'
      };
    }
  },

  async logout(): Promise<void> {
    localStorage.removeItem('token');
  },

  isAuthenticated(): boolean {
    return !!localStorage.getItem('token');
  }
};

export default authService;
