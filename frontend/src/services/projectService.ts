import api from './api';
import { SolarProject, SolarComponent, ApiResponse, SimulationResult } from '../types';

export const projectService = {
  getAllProjects: async (): Promise<ApiResponse<SolarProject[]>> => {
    try {
      const response = await api.get<ApiResponse<SolarProject[]>>('/projects');
      return response.data;
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.error || 'Error al obtener proyectos'
      };
    }
  },

  getProjectById: async (id: number): Promise<ApiResponse<SolarProject>> => {
    try {
      const response = await api.get<ApiResponse<SolarProject>>(`/projects/${id}`);
      return response.data;
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.error || 'Error al obtener el proyecto'
      };
    }
  },

  createProject: async (project: Omit<SolarProject, 'id' | 'createdAt' | 'updatedAt'>): Promise<ApiResponse<SolarProject>> => {
    try {
      const response = await api.post<ApiResponse<SolarProject>>('/projects', project);
      return response.data;
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.error || 'Error al crear el proyecto'
      };
    }
  },

  updateProject: async (id: number, project: Partial<SolarProject>): Promise<ApiResponse<SolarProject>> => {
    try {
      const response = await api.put<ApiResponse<SolarProject>>(`/projects/${id}`, project);
      return response.data;
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.error || 'Error al actualizar el proyecto'
      };
    }
  },

  deleteProject: async (id: number): Promise<ApiResponse<void>> => {
    try {
      const response = await api.delete<ApiResponse<void>>(`/projects/${id}`);
      return response.data;
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.error || 'Error al eliminar el proyecto'
      };
    }
  },

  addComponent: async (projectId: number, component: Omit<SolarComponent, 'id'>): Promise<ApiResponse<SolarComponent>> => {
    try {
      const response = await api.post<ApiResponse<SolarComponent>>(`/projects/${projectId}/components`, component);
      return response.data;
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.error || 'Error al agregar componente'
      };
    }
  },

  getSimulation: async (projectId: number): Promise<ApiResponse<SimulationResult>> => {
    try {
      const response = await api.get<ApiResponse<SimulationResult>>(`/projects/${projectId}/simulation`);
      return response.data;
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.error || 'Error al obtener simulación'
      };
    }
  }
};

export default projectService;
