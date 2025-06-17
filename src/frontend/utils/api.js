/**
 * API utility functions for communicating with the backend
 */

import axios from 'axios';
import { isDemoMode, demoApiResponses, simulateApiDelay } from './demoData';

// API Configuration based on environment
const getApiBaseURL = () => {
  // Check for environment variable first
  if (process.env.REACT_APP_API_URL) {
    return process.env.REACT_APP_API_URL;
  }

  // Fallback based on hostname
  const hostname = window.location.hostname;

  if (hostname === 'localhost' || hostname === '127.0.0.1') {
    return '/api/v1'; // Local development with proxy
  } else if (hostname.includes('netlify.app')) {
    return 'https://hypersequester-api.herokuapp.com/api/v1'; // Production API
  } else {
    return '/api/v1'; // Default fallback
  }
};

// Create axios instance with default configuration
const api = axios.create({
  baseURL: getApiBaseURL(),
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Demo mode interceptor
api.interceptors.request.use(
  async (config) => {
    // Check if we're in demo mode
    if (isDemoMode()) {
      const endpoint = config.url.replace(config.baseURL, '');
      const demoResponse = demoApiResponses[endpoint];

      if (demoResponse) {
        // Simulate API delay
        await simulateApiDelay();

        // Return demo data
        return Promise.reject({
          response: {
            data: demoResponse,
            status: 200,
            statusText: 'OK (Demo Mode)',
          },
          config,
          isDemo: true,
        });
      }
    }

    // Add auth token for real API calls
    const token = localStorage.getItem('authToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling and demo mode
api.interceptors.response.use(
  (response) => response,
  (error) => {
    // Handle demo mode responses
    if (error.isDemo) {
      return Promise.resolve(error.response);
    }

    // Handle real API errors
    if (error.response?.status === 401) {
      // Handle unauthorized access
      localStorage.removeItem('authToken');
      window.location.href = '/login';
    }

    // If API is not available and we're not in demo mode, enable demo mode
    if (!error.response && !isDemoMode()) {
      console.warn('API not available, enabling demo mode');
      window.location.search = window.location.search + (window.location.search ? '&' : '?') + 'demo=true';
    }

    return Promise.reject(error);
  }
);

// Authentication API
export const authAPI = {
  login: (credentials) => api.post('/auth/login', credentials),
  register: (userData) => api.post('/auth/register', userData),
  logout: () => api.post('/auth/logout'),
  refreshToken: () => api.post('/auth/refresh'),
};

// Properties API
export const propertiesAPI = {
  getAll: (params = {}) => api.get('/properties', { params }),
  getById: (id) => api.get(`/properties/${id}`),
  create: (propertyData) => api.post('/properties', propertyData),
  update: (id, propertyData) => api.put(`/properties/${id}`, propertyData),
  delete: (id) => api.delete(`/properties/${id}`),
};

// Assessments API
export const assessmentsAPI = {
  getAll: (params = {}) => api.get('/assessments', { params }),
  getById: (id) => api.get(`/assessments/${id}`),
  create: (assessmentData) => api.post('/assessments', assessmentData),
  update: (id, assessmentData) => api.put(`/assessments/${id}`, assessmentData),
  delete: (id) => api.delete(`/assessments/${id}`),
  getResults: (id) => api.get(`/assessments/${id}/results`),
  downloadReport: (id) => api.get(`/assessments/${id}/report`, { responseType: 'blob' }),
  downloadKML: (id) => api.get(`/assessments/${id}/kml`, { responseType: 'blob' }),
};

// Processing API
export const processingAPI = {
  getStatus: (jobId) => api.get(`/processing/status/${jobId}`),
  getQueue: () => api.get('/processing/queue'),
  cancelJob: (jobId) => api.delete(`/processing/jobs/${jobId}`),
};

// File upload API
export const uploadAPI = {
  uploadHyperspectralData: (file, onProgress) => {
    const formData = new FormData();
    formData.append('file', file);

    return api.post('/upload/hyperspectral', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: (progressEvent) => {
        if (onProgress) {
          const percentCompleted = Math.round(
            (progressEvent.loaded * 100) / progressEvent.total
          );
          onProgress(percentCompleted);
        }
      },
    });
  },
};

// Statistics API
export const statsAPI = {
  getDashboard: () => api.get('/stats/dashboard'),
  getPropertyStats: (propertyId) => api.get(`/stats/properties/${propertyId}`),
  getCarbonTrends: (params = {}) => api.get('/stats/carbon-trends', { params }),
};

// Settings API
export const settingsAPI = {
  get: () => api.get('/settings'),
  update: (settings) => api.put('/settings', settings),
  resetToDefaults: () => api.post('/settings/reset'),
};

// Utility functions
export const handleApiError = (error) => {
  if (error.response) {
    // Server responded with error status
    const { status, data } = error.response;
    return {
      status,
      message: data.message || data.error || 'An error occurred',
      details: data.details || null,
    };
  } else if (error.request) {
    // Request was made but no response received
    return {
      status: 0,
      message: 'Network error - please check your connection',
      details: null,
    };
  } else {
    // Something else happened
    return {
      status: -1,
      message: error.message || 'An unexpected error occurred',
      details: null,
    };
  }
};

export const downloadFile = (blob, filename) => {
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  window.URL.revokeObjectURL(url);
};

export default api;
