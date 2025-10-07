/**
 * 网络状态监控工具
 * 用于检测和报告网络连接质量
 */

class NetworkMonitor {
  constructor() {
    this.isOnline = navigator.onLine
    this.connectionQuality = 'unknown'
    this.latency = 0
    this.listeners = []
    
    this.init()
  }

  init() {
    // 监听网络状态变化
    window.addEventListener('online', () => {
      this.isOnline = true
      this.notifyListeners({ type: 'online' })
    })

    window.addEventListener('offline', () => {
      this.isOnline = false
      this.notifyListeners({ type: 'offline' })
    })

    // 定期检测网络质量
    this.startQualityCheck()
  }

  // 添加状态监听器
  addListener(callback) {
    this.listeners.push(callback)
  }

  // 移除监听器
  removeListener(callback) {
    this.listeners = this.listeners.filter(listener => listener !== callback)
  }

  // 通知所有监听器
  notifyListeners(event) {
    this.listeners.forEach(callback => callback(event))
  }

  // 检测网络延迟 - 优化生产环境兼容性
  async checkLatency() {
    if (!this.isOnline) return Infinity

    try {
      const start = performance.now()
      
      // 使用更安全的检测方式
      const controller = new AbortController()
      const timeoutId = setTimeout(() => controller.abort(), 5000) // 5秒超时
      
      const response = await fetch('/api/health', { 
        method: 'GET', // 改用GET，更兼容
        cache: 'no-cache',
        signal: controller.signal,
        headers: {
          'Accept': 'application/json'
        }
      })
      
      clearTimeout(timeoutId)
      const end = performance.now()
      
      if (response.ok) {
        this.latency = end - start
        return this.latency
      }
    } catch (error) {
      // 静默处理网络检测错误，避免控制台噪音
      if (error.name !== 'AbortError') {
        console.debug('网络延迟检测失败:', error.message)
      }
      this.latency = Infinity
    }
    
    return this.latency
  }

  // 评估连接质量 - 优化阈值和错误处理
  async assessConnectionQuality() {
    const latency = await this.checkLatency()
    
    let newQuality
    if (latency === Infinity) {
      // 检测失败不一定是离线，可能是CORS或其他问题
      newQuality = navigator.onLine ? 'unknown' : 'offline'
    } else if (latency < 200) {
      newQuality = 'excellent'
    } else if (latency < 500) {
      newQuality = 'good'
    } else if (latency < 1500) {
      newQuality = 'fair'
    } else {
      newQuality = 'poor'
    }

    // 只在质量真正改变时通知
    if (newQuality !== this.connectionQuality) {
      this.connectionQuality = newQuality
      this.notifyListeners({
        type: 'quality-update',
        quality: this.connectionQuality,
        latency: this.latency
      })
    }

    return this.connectionQuality
  }

  // 开始定期质量检查 - 优化检查频率
  startQualityCheck() {
    // 延迟3秒后开始第一次检查，避免应用启动时的干扰
    setTimeout(() => {
      this.assessConnectionQuality()
    }, 3000)
    
    // 每60秒检查一次（降低频率，减少网络负担）
    setInterval(() => {
      this.assessConnectionQuality()
    }, 60000)
  }

  // 获取当前状态
  getStatus() {
    return {
      isOnline: this.isOnline,
      quality: this.connectionQuality,
      latency: this.latency
    }
  }

  // 获取质量描述
  getQualityDescription() {
    const descriptions = {
      'offline': '网络连接已断开',
      'poor': '网络连接较差，可能影响使用体验',
      'fair': '网络连接一般，部分功能可能较慢',
      'good': '网络连接良好',
      'excellent': '网络连接优秀',
      'unknown': '网络状态正常'  // 改为更积极的描述
    }
    
    return descriptions[this.connectionQuality] || descriptions.unknown
  }

  // 获取建议操作
  getRecommendation() {
    const recommendations = {
      'offline': '请检查网络连接后重试',
      'poor': '建议等待网络改善或切换到更稳定的网络',
      'fair': '复杂任务可能需要更长时间，请耐心等待',
      'good': '网络状况良好，可以正常使用',
      'excellent': '网络状况优秀，享受流畅体验',
      'unknown': '正在检测网络状况...'
    }
    
    return recommendations[this.connectionQuality] || recommendations.unknown
  }
}

// 创建全局实例
export const networkMonitor = new NetworkMonitor()

// 导出类供其他地方使用
export default NetworkMonitor