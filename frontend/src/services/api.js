import axios from 'axios'

axios.defaults.withCredentials = true


export const apiService = {
  async login(formData) {
    const response = await axios.post('/auth/login/', formData)
    return response.data
  },

  async register(formData) {
    const response = await axios.post('/auth/register/', formData)
    return response.data
  },

  async logout() {
    const response = await axios.post('/auth/logout/')
    return response.data
  },

  async checkAuth() {
    try {
      const response = await axios.get('/auth/check/')
      return response.data
    } catch (error) {
      if (error.response?.status === 401) {
        return { authenticated: false }
      }
      throw error
    }
  },

  // User endpoints, needs updating
  async getUsers() {
    const response = await axios.get('/users/me')
    return response.data
  },

  async getCurrentUser() {
    const response = await axios.get('/auth/me/')
    return response.data
  },

  async getUser(id) {
    const response = await axios.get(`/users/${id}/`)
    return response.data
  },

  async createUser(userData) {
    const response = await axios.post('/users/', userData)
    return response.data
  },

  async updateUser(id, userData) {
    const response = await axios.put(`/users/${id}/`)
    return response.data
  },

  async deleteUser(id) {
    const response = await axios.delete(`/users/${id}/`)
    return response.data
  },

  async getDatasetList() {
    const response = await axios.get('/datasets/')
    return response.data
  },

  async getDatasetDetail(id) {
    const response = await axios.get(`/datasets/${id}/`)
    return response.data
  },

  async createDataset(formData) {
    const response = await axios.post('/datasets/create/', formData)
    return response.data
  },

  async patchDataset(id, formData) {
    const response = await axios.patch(`/datasets/${id}/new/`, formData)
    return response.data
  },

  async getResults(id) {
    const response = await axios.get(`/datasets/${id}/results/`)
    return response.data
  },

  async updateDataset(id, formData) {
    const response = await axios.patch(`/datasets/${id}/results-update/`, formData)
    return response.data
  },
}

