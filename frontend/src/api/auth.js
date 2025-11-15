import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor to include auth token
api.interceptors.request.use(
  (config) => {
    const token = getToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Add response interceptor to handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      removeToken();
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Token management
export const getToken = () => {
  return localStorage.getItem('token');
};

export const setToken = (token) => {
  localStorage.setItem('token', token);
};

export const removeToken = () => {
  localStorage.removeItem('token');
};

// Auth API calls
export const login = async (credentials) => {
  try {
    const response = await api.post('/api/auth/login', credentials);
    const { access_token, ...userData } = response.data;
    setToken(access_token);
    return userData;
  } catch (error) {
    throw error.response?.data || { detail: 'Login failed' };
  }
};

export const signup = async (userData) => {
  try {
    const response = await api.post('/api/auth/signup', userData);
    const { access_token, ...userInfo } = response.data;
    setToken(access_token);
    return userInfo;
  } catch (error) {
    throw error.response?.data || { detail: 'Signup failed' };
  }
};

export const getCurrentUser = async () => {
  try {
    const response = await api.get('/api/auth/me');
    return response.data;
  } catch (error) {
    throw error.response?.data || { detail: 'Failed to get user info' };
  }
};

export default api;