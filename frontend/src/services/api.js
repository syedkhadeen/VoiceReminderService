import axios from 'axios'

// API base URL - use environment variable or default to localhost
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'
const WORKER_BASE_URL = import.meta.env.VITE_WORKER_URL || 'http://localhost:8001'

// Create axios instance
const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
})

// Request interceptor for logging
api.interceptors.request.use(
    (config) => {
        console.log(`[API] ${config.method?.toUpperCase()} ${config.url}`)
        return config
    },
    (error) => Promise.reject(error)
)

// Response interceptor for error handling
api.interceptors.response.use(
    (response) => response,
    (error) => {
        console.error('[API Error]', error.response?.data || error.message)
        return Promise.reject(error)
    }
)

// Users API
export const usersApi = {
    // Get all users
    getAll: async (page = 1, size = 10) => {
        const response = await api.get('/api/users', { params: { page, size } })
        return response.data
    },

    // Get user by ID
    getById: async (id) => {
        const response = await api.get(`/api/users/${id}`)
        return response.data
    },

    // Create user
    create: async (email) => {
        const response = await api.post('/api/users', { email })
        return response.data
    },

    // Delete user
    delete: async (id) => {
        await api.delete(`/api/users/${id}`)
    },
}

// Reminders API
export const remindersApi = {
    // Get all reminders
    getAll: async (page = 1, size = 10) => {
        const response = await api.get('/api/reminders', { params: { page, size } })
        return response.data
    },

    // Get reminder by ID
    getById: async (id) => {
        const response = await api.get(`/api/reminders/${id}`)
        return response.data
    },

    // Get reminders by user ID
    getByUserId: async (userId, status = 'all', page = 1, size = 10) => {
        const response = await api.get(`/api/users/${userId}/reminders`, {
            params: { status, page, size },
        })
        return response.data
    },

    // Create reminder
    create: async (data) => {
        const response = await api.post('/api/reminders', data)
        return response.data
    },

    // Get stats
    getStats: async () => {
        const response = await api.get('/api/reminders/stats')
        return response.data
    },
}

// Health check
export const healthApi = {
    check: async () => {
        const response = await api.get('/api/health')
        return response.data
    },

    checkWorker: async () => {
        const response = await axios.get(`${WORKER_BASE_URL}/health`)
        return response.data
    },
}

export default api
