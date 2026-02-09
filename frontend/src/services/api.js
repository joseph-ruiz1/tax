import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api', // use env var if set, else proxy path
  withCredentials: true, 
});

api.interceptors.request.use(config => {
  const method = config.method?.toUpperCase()
  if (['POST', 'PUT', 'PATCH', 'DELETE'].includes(method)) {
    const csrfToken = getCookie('csrftoken')
    if (csrfToken) {
      config.headers['X-CSRFToken'] = csrfToken
    }
  }
  return config
})

// Utility: parse a cookie value by name
function getCookie(name) {
  const match = document.cookie.match(new RegExp('(^|; )' + name + '=([^;]*)'))
  return match ? decodeURIComponent(match[2]) : null
}

export const apiService = {
  async login(formData) {
    const response = await api.post('/auth/login/', formData)
    return response.data
  },

  async register(formData) {
    const response = await api.post('/auth/registration/', formData)
    return response.data
  },

  async logout() {
    const response = await api.post('/auth/logout/')
    return response.data
  },

  async checkAuth() {
    try {
      const response = await api.get('/auth/user/')
      return {
        authenticated: true,
        user: response.data
      }
    } catch (error) {
      if (error.response?.status === 401) {
        return { authenticated: false }
      }
      throw error
    }
  },

  async getCurrentUser() {
    const response = await api.get('/auth/me/')
    return response.data
  },

  async getUser(id) {
    const response = await api.get(`/users/${id}/`)
    return response.data
  },

  async createUser(userData) {
    const response = await api.post('/users/', userData)
    return response.data
  },

  async updateUser(id, userData) {
    const response = await api.put(`/users/${id}/`, userData)
    return response.data
  },

  async deleteUser(id) {
    const response = await api.delete(`/users/${id}/`)
    return response.data
  },

  async getDatasetList() {
    const response = await api.get('/datasets/')
    return response.data
  },

  async getDatasetDetail(id) {
    const response = await api.get(`/datasets/${id}/`)
    return response.data
  },

  async deleteDataset(id) {
    const response = await api.delete(`/datasets/${id}/`)
    return response.data
  },

  async createDataset(formData) {
    const response = await api.post('/datasets/create/', formData)
    return response.data
  },

  async patchDataset(id, formData) {
    const response = await api.patch(`/datasets/${id}/new/`, formData)
    return response.data
  },

  async getResults(id) {
    const response = await api.get(`/datasets/${id}/results/`)
    return response.data
  },

  async updateDataset(id, formData) {
    const response = await api.patch(`/datasets/${id}/results-update/`, formData)
    return response.data
  },
};
