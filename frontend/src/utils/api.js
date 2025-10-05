/**
 * 统一API配置 - 兼容Docker和本地开发环境
 */
import axios from 'axios'

// 创建统一的API实例
const createApiInstance = () => {
  const config = {
    timeout: 120000, // 增加到120秒，适应复杂编程问题
    headers: {
      'Content-Type': 'application/json'
    }
  }

  // 统一API路径配置 - 两个环境都使用相同路径
  // 本地开发：/api → Vite代理 → http://localhost:8080
  // Docker生产：/api → Nginx代理 → backend:8080
  config.baseURL = '/api'
  
  const envType = process.env.NODE_ENV === 'production' ? '🐳 Docker生产环境' : '🛠️ 本地开发环境'
  console.log(`${envType} - API Base URL:`, config.baseURL)

  const instance = axios.create(config)

  // 请求拦截器
  instance.interceptors.request.use(
    (config) => {
      console.log(`📤 API请求: ${config.method?.toUpperCase()} ${config.url}`)
      return config
    },
    (error) => {
      console.error('❌ API请求错误:', error)
      return Promise.reject(error)
    }
  )

  // 响应拦截器
  instance.interceptors.response.use(
    (response) => {
      console.log(`📥 API响应: ${response.status} ${response.config.url}`)
      return response
    },
    (error) => {
      console.error('❌ API响应错误:', error.response?.status, error.config?.url, error.message)
      return Promise.reject(error)
    }
  )

  return instance
}

// 导出统一的API实例
export const api = createApiInstance()

// 导出完整的API实例（包含所有axios方法）
export const p2lApi = api

// 添加便捷方法到 p2lApi 实例上
p2lApi.getModelInfo = () => api.get('/p2l/model-info')
p2lApi.analyze = (data) => api.post('/p2l/analyze', data)
p2lApi.health = () => api.get('/health')

export default api