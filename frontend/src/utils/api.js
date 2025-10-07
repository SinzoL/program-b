/**
 * 统一API配置 - 兼容Docker和本地开发环境
 */
import axios from 'axios'

// 创建统一的API实例
const createApiInstance = () => {
  const config = {
    timeout: 150000, // 增加到150秒，适应服务器环境的网络延迟
    headers: {
      'Content-Type': 'application/json'
    },
    // 增加重试配置
    retry: 3,
    retryDelay: 1000,
    retryCondition: (error) => {
      // 网络错误或5xx错误时重试
      return !error.response || (error.response.status >= 500 && error.response.status <= 599)
    }
  }

  // 统一API路径配置 - 两个环境都使用相同路径
  // 本地开发：/api → Vite代理 → http://localhost:8080
  // Docker生产：/api → Nginx代理 → backend:8080
  config.baseURL = '/api'
  
  const envType = process.env.NODE_ENV === 'production' ? '🐳 Docker生产环境' : '🛠️ 本地开发环境'
  console.log(`${envType} - API Base URL:`, config.baseURL)
  console.log(`⏱️ API超时设置: ${config.timeout}ms (${config.timeout/1000}秒)`)

  const instance = axios.create(config)

  // 请求拦截器 - 增加请求时间戳
  instance.interceptors.request.use(
    (config) => {
      config.metadata = { startTime: new Date() }
      console.log(`📤 API请求: ${config.method?.toUpperCase()} ${config.url}`)
      return config
    },
    (error) => {
      console.error('❌ API请求错误:', error)
      return Promise.reject(error)
    }
  )

  // 响应拦截器 - 增加响应时间统计和详细错误处理
  instance.interceptors.response.use(
    (response) => {
      const duration = new Date() - response.config.metadata.startTime
      console.log(`📥 API响应: ${response.status} ${response.config.url} (${duration}ms)`)
      
      // 如果响应时间过长，给出提示
      if (duration > 30000) {
        console.warn(`⚠️ 响应时间较长: ${duration}ms，可能是服务器网络延迟`)
      }
      
      return response
    },
    (error) => {
      const duration = error.config?.metadata ? new Date() - error.config.metadata.startTime : 0
      
      // 详细的错误日志
      if (error.code === 'ECONNABORTED') {
        console.error(`⏰ API超时: ${error.config?.url} (${duration}ms)`)
      } else if (error.response) {
        console.error(`❌ API响应错误: ${error.response.status} ${error.config?.url} (${duration}ms)`, error.response.data)
      } else if (error.request) {
        console.error(`🔌 网络连接错误: ${error.config?.url} (${duration}ms)`)
      } else {
        console.error(`❌ API请求配置错误:`, error.message)
      }
      
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