import axios from 'axios'
import { ElMessage } from 'element-plus'

const api = axios.create({
  baseURL: 'http://127.0.0.1:8000/api',
})

api.interceptors.response.use(
  respons => respons,
  error => {
    ElMessage.error(error.response?.data?.detail || error.message || 'Error occurred')
    return Promise.reject(error)
  }
)

export const generateDataset = (data) => api.post('/dataset/generate', data)
export const getDatasetList = () => api.get('/dataset/list')
export const startTraining = (data) => api.post('/train/start', data)
export const stopTask = () => api.post('/task/stop')
export const getResultsList = () => api.get('/results/list')
export const compareResults = (data) => api.post('/results/compare', data)

export default api
