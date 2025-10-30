import axios from 'axios';

// Determine API URL based on environment
const getApiUrl = () => {
  // If VITE_API_URL is explicitly set, use it
  if (import.meta.env.VITE_API_URL) {
    return import.meta.env.VITE_API_URL.replace(/\/$/, '');
  }
  
  // In production (on Render), use relative path since frontend is served by backend
  if (import.meta.env.PROD) {
    return '/api';
  }
  
  // In development, use localhost
  return 'http://localhost:8000/api';
};

const API_URL = getApiUrl();

const api = axios.create({
  baseURL: API_URL,
});

// Add token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const authAPI = {
  signup: (data) => api.post('/auth/signup', data),
  login: (data) => api.post('/auth/login', data),
  getCurrentUser: () => api.get('/auth/me'),
};

export const ticketsAPI = {
  createTicket: (formData) => api.post('/tickets/', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  }),
  getAllTickets: () => api.get('/tickets/'),
  getTicket: (id) => api.get(`/tickets/${id}`),
  updateStatus: (id, status) => api.put(`/tickets/${id}/status?ticket_status=${status}`),
};

export default api;
