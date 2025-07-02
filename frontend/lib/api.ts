// API configuration utility
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001';

export const api = {
  baseURL: API_BASE_URL,
  
  // Helper function to make API calls
  async fetch(endpoint: string, options: RequestInit = {}) {
    const url = endpoint.startsWith('http') ? endpoint : `${API_BASE_URL}${endpoint}`;
    
    const defaultHeaders = {
      'Content-Type': 'application/json',
      ...options.headers,
    };

    // Add auth token if available
    const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null;
    if (token) {
      defaultHeaders['Authorization'] = `Bearer ${token}`;
    }

    const config: RequestInit = {
      ...options,
      headers: defaultHeaders,
    };

    try {
      const response = await fetch(url, config);
      return response;
    } catch (error) {
      console.error('API call failed:', error);
      throw error;
    }
  },

  // Specific API endpoints
  auth: {
    login: (credentials: { email: string; password: string }) =>
      api.fetch('/api/auth/login', {
        method: 'POST',
        body: JSON.stringify(credentials),
      }),
    
    register: (userData: { email: string; password: string; name: string }) =>
      api.fetch('/api/auth/register', {
        method: 'POST',
        body: JSON.stringify(userData),
      }),
    
    me: () => api.fetch('/api/auth/me'),
  },

  social: {
    analytics: () => api.fetch('/api/social/analytics'),
    platforms: () => api.fetch('/api/social/platforms'),
    post: (data: any) => api.fetch('/api/social/post', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  },

  channels: {
    list: () => api.fetch('/api/channels'),
    create: (data: any) => api.fetch('/api/channels', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
    get: (id: string) => api.fetch(`/api/channels/${id}`),
    update: (id: string, data: any) => api.fetch(`/api/channels/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    }),
    delete: (id: string) => api.fetch(`/api/channels/${id}`, {
      method: 'DELETE',
    }),
  },

  videos: {
    list: () => api.fetch('/api/videos'),
    create: (data: any) => api.fetch('/api/videos', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
    get: (id: string) => api.fetch(`/api/videos/${id}`),
    update: (id: string, data: any) => api.fetch(`/api/videos/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    }),
    delete: (id: string) => api.fetch(`/api/videos/${id}`, {
      method: 'DELETE',
    }),
  },

  wizard: {
    create: (data: any) => api.fetch('/api/wizard/create', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
    status: (id: string) => api.fetch(`/api/wizard/status/${id}`),
  },

  health: () => api.fetch('/health'),
};

export default api;