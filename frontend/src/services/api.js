import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8080'

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  }
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
}, (error) => {
  return Promise.reject(error)
})

export const authService = {
  login: (email, password) => api.post('/auth/login', { email, password }),
  register: (email, password, name) => api.post('/auth/register', { email, password, name }),
  refresh: () => api.post('/auth/refresh')
}

export const auditService = {
  getAll: (page = 0, size = 10, sortBy = 'id', sortDir = 'ASC') => 
    api.get('/audit', { params: { page, size, sortBy, sortDir } }),
  getById: (id) => api.get(`/audit/${id}`),
  create: (data) => api.post('/audit', data),
  update: (id, data) => api.put(`/audit/${id}`, data),
  delete: (id) => api.delete(`/audit/${id}`),
  search: (query) => api.get(`/audit/search?q=${query}`),
  getStats: () => api.get('/audit/stats'),
  export: (format = 'csv') => api.get(`/audit/export?format=${format}`, { responseType: 'blob' })
}

export const aiService = {
  describe: (text) => api.post('/describe', { text }),
  categorise: (text) => api.post('/categorise', { text }),
  recommend: (text) => api.post('/recommend', { text }),
  generateReport: (auditId) => api.post(`/generate-report/${auditId}`),
  query: (question) => api.post('/query', { question }),
  analyseDocument: (text) => api.post('/analyse-document', { text }),
  health: () => api.get('/health')
}

export default api
