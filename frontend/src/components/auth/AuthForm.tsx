import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  TextField,
  Button,
  Typography,
  Alert,
  Container,
  CircularProgress
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';

const AuthForm: React.FC = () => {
  const [isLogin, setIsLogin] = useState(true);
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: ''
  });
  const [loading, setLoading] = useState(false);
  const { login, register, error } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      if (isLogin) {
        await login(formData.email, formData.password);
      } else {
        await register(formData.name, formData.email, formData.password);
      }
      navigate('/dashboard');
    } catch (err) {
      console.error('Error en autenticación:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  return (
    <Container maxWidth="sm">
      <Box
        sx={{
          marginTop: 8,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center'
        }}
      >
        <Card sx={{ width: '100%', mt: 3 }}>
          <CardContent>
            <Typography variant="h5" component="h1" gutterBottom align="center">
              {isLogin ? 'Iniciar Sesión' : 'Registro'}
            </Typography>

            {error && (
              <Alert severity="error" sx={{ mb: 2 }}>
                {error}
              </Alert>
            )}

            <form onSubmit={handleSubmit}>
              {!isLogin && (
                <TextField
                  margin="normal"
                  required
                  fullWidth
                  id="name"
                  label="Nombre"
                  name="name"
                  autoComplete="name"
                  autoFocus
                  value={formData.name}
                  onChange={handleChange}
                />
              )}

              <TextField
                margin="normal"
                required
                fullWidth
                id="email"
                label="Correo Electrónico"
                name="email"
                autoComplete="email"
                autoFocus={isLogin}
                value={formData.email}
                onChange={handleChange}
              />

              <TextField
                margin="normal"
                required
                fullWidth
                name="password"
                label="Contraseña"
                type="password"
                id="password"
                autoComplete="current-password"
                value={formData.password}
                onChange={handleChange}
              />

              <Button
                type="submit"
                fullWidth
                variant="contained"
                sx={{ mt: 3, mb: 2 }}
                disabled={loading}
              >
                {loading ? (
                  <CircularProgress size={24} />
                ) : isLogin ? (
                  'Iniciar Sesión'
                ) : (
                  'Registrarse'
                )}
              </Button>

              <Button
                fullWidth
                variant="text"
                onClick={() => setIsLogin(!isLogin)}
                sx={{ mt: 1 }}
              >
                {isLogin
                  ? '¿No tienes cuenta? Regístrate'
                  : '¿Ya tienes cuenta? Inicia sesión'}
              </Button>
            </form>
          </CardContent>
        </Card>
      </Box>
    </Container>
  );
};

export default AuthForm;
