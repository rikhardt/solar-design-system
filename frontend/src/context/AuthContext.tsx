import React, { createContext, useState, useContext, useEffect, ReactNode } from 'react';
import { User, AuthState } from '../types';
import authService from '../services/authService';

interface AuthContextType extends AuthState {
  login: (email: string, password: string) => Promise<void>;
  register: (name: string, email: string, password: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [state, setState] = useState<AuthState>({
    user: null,
    isAuthenticated: false,
    loading: true,
    error: null
  });

  useEffect(() => {
    const initAuth = async () => {
      if (authService.isAuthenticated()) {
        try {
          const response = await authService.getCurrentUser();
          if (response.success && response.data) {
            setState({
              user: response.data,
              isAuthenticated: true,
              loading: false,
              error: null
            });
          } else {
            setState({
              user: null,
              isAuthenticated: false,
              loading: false,
              error: null
            });
          }
        } catch (error) {
          setState({
            user: null,
            isAuthenticated: false,
            loading: false,
            error: 'Error al obtener el usuario'
          });
        }
      } else {
        setState(prev => ({ ...prev, loading: false }));
      }
    };

    initAuth();
  }, []);

  const login = async (email: string, password: string) => {
    try {
      const response = await authService.login({ email, password });
      if (response.success && response.data) {
        setState({
          user: response.data.user,
          isAuthenticated: true,
          loading: false,
          error: null
        });
      } else {
        setState(prev => ({ 
          ...prev, 
          error: response.error || 'Error al iniciar sesión',
          loading: false 
        }));
      }
    } catch (error) {
      setState(prev => ({ 
        ...prev, 
        error: 'Error al iniciar sesión',
        loading: false 
      }));
    }
  };

  const register = async (name: string, email: string, password: string) => {
    try {
      const response = await authService.register({ name, email, password });
      if (response.success && response.data) {
        setState({
          user: response.data,
          isAuthenticated: true,
          loading: false,
          error: null
        });
      } else {
        setState(prev => ({ 
          ...prev, 
          error: response.error || 'Error al registrar usuario',
          loading: false 
        }));
      }
    } catch (error) {
      setState(prev => ({ 
        ...prev, 
        error: 'Error al registrar usuario',
        loading: false 
      }));
    }
  };

  const logout = () => {
    authService.logout();
    setState({
      user: null,
      isAuthenticated: false,
      loading: false,
      error: null
    });
  };

  return (
    <AuthContext.Provider
      value={{
        ...state,
        login,
        register,
        logout
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth debe ser usado dentro de un AuthProvider');
  }
  return context;
};
