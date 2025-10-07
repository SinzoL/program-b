/**
 * 请求竞速器 - 并发请求策略
 * 同时发送多个请求，采用最快成功响应，提高成功率和速度
 */

import { p2lApi } from './api'

class RequestRacer {
  constructor() {
    this.activeRaces = new Map()
  }

  /**
   * 创建竞速请求
   * @param {string} raceId - 竞速标识符
   * @param {Array} requestConfigs - 请求配置数组
   * @param {Object} options - 选项
   */
  async race(raceId, requestConfigs, options = {}) {
    const {
      timeout = 30000,        // 单个请求超时
      maxConcurrent = 3,      // 最大并发数
      staggerDelay = 500,     // 错开发送延迟 (ms)
      fallbackDelay = 2000,   // 备用请求延迟 (ms)
      retryOnFailure = true   // 全部失败时是否重试
    } = options

    console.log(`🏁 [RequestRacer] 开始竞速: ${raceId}`)
    
    // 如果已有相同的竞速在进行，返回现有的Promise
    if (this.activeRaces.has(raceId)) {
      console.log(`⏳ [RequestRacer] 竞速 ${raceId} 已在进行中`)
      return this.activeRaces.get(raceId)
    }

    const racePromise = this._executeRace(requestConfigs, {
      timeout,
      maxConcurrent,
      staggerDelay,
      fallbackDelay,
      retryOnFailure,
      raceId
    })

    // 记录活跃的竞速
    this.activeRaces.set(raceId, racePromise)

    try {
      const result = await racePromise
      return result
    } finally {
      // 清理完成的竞速
      this.activeRaces.delete(raceId)
    }
  }

  /**
   * 执行竞速逻辑
   */
  async _executeRace(requestConfigs, options) {
    const { timeout, maxConcurrent, staggerDelay, fallbackDelay, retryOnFailure, raceId } = options
    
    // 限制并发数量
    const configs = requestConfigs.slice(0, maxConcurrent)
    
    return new Promise((resolve, reject) => {
      let completedCount = 0
      let hasResolved = false
      const errors = []
      const activeRequests = []

      // 取消所有未完成的请求
      const cancelAllRequests = () => {
        activeRequests.forEach(({ cancel }) => {
          if (cancel) cancel('Race completed')
        })
      }

      // 处理成功响应
      const handleSuccess = (response, requestIndex) => {
        if (hasResolved) return
        
        hasResolved = true
        console.log(`🏆 [RequestRacer] ${raceId} 获胜者: 请求${requestIndex + 1}`)
        cancelAllRequests()
        resolve(response)
      }

      // 处理失败响应
      const handleError = (error, requestIndex) => {
        completedCount++
        errors.push({ requestIndex, error })
        
        console.warn(`❌ [RequestRacer] ${raceId} 请求${requestIndex + 1}失败:`, error.message)
        
        // 如果所有请求都失败了
        if (completedCount === configs.length && !hasResolved) {
          hasResolved = true
          
          if (retryOnFailure) {
            console.log(`🔄 [RequestRacer] ${raceId} 所有请求失败，准备重试...`)
            // 延迟后重试，使用更保守的策略
            setTimeout(() => {
              this._executeRetryRace(requestConfigs, options)
                .then(resolve)
                .catch(reject)
            }, 1000)
          } else {
            const combinedError = new Error(`所有请求都失败了: ${errors.map(e => e.error.message).join('; ')}`)
            combinedError.allErrors = errors
            reject(combinedError)
          }
        }
      }

      // 创建带取消功能的请求
      const createCancellableRequest = (config, requestIndex) => {
        const source = axios.CancelToken?.source()
        
        const requestPromise = this._makeRequest(config, {
          timeout,
          cancelToken: source?.token
        })

        activeRequests.push({
          promise: requestPromise,
          cancel: source?.cancel
        })

        requestPromise
          .then(response => handleSuccess(response, requestIndex))
          .catch(error => {
            if (!axios.isCancel?.(error)) {
              handleError(error, requestIndex)
            }
          })
      }

      // 错开发送请求以避免同时冲击
      configs.forEach((config, index) => {
        if (index === 0) {
          // 立即发送第一个请求
          createCancellableRequest(config, index)
        } else if (index === 1) {
          // 稍微延迟发送第二个请求
          setTimeout(() => {
            if (!hasResolved) {
              createCancellableRequest(config, index)
            }
          }, staggerDelay)
        } else {
          // 更长延迟发送后续请求（作为备用）
          setTimeout(() => {
            if (!hasResolved) {
              createCancellableRequest(config, index)
            }
          }, fallbackDelay + (index - 2) * staggerDelay)
        }
      })
    })
  }

  /**
   * 重试竞速（更保守的策略）
   */
  async _executeRetryRace(requestConfigs, options) {
    console.log(`🔄 [RequestRacer] 执行重试竞速`)
    
    // 重试时使用更保守的配置
    const retryOptions = {
      ...options,
      timeout: options.timeout * 1.5,  // 增加超时时间
      maxConcurrent: Math.min(2, requestConfigs.length), // 减少并发数
      staggerDelay: options.staggerDelay * 2, // 增加错开延迟
      retryOnFailure: false // 重试时不再递归重试
    }

    return this._executeRace(requestConfigs, retryOptions)
  }

  /**
   * 发送单个请求
   */
  async _makeRequest(config, options = {}) {
    const { timeout, cancelToken } = options
    
    // 创建请求配置
    const requestConfig = {
      ...config,
      timeout,
      cancelToken
    }

    // 根据请求类型调用相应的方法
    if (config.method?.toLowerCase() === 'post') {
      return p2lApi.post(config.url, config.data, requestConfig)
    } else {
      return p2lApi.get(config.url, requestConfig)
    }
  }

  /**
   * P2L分析竞速请求
   */
  async raceP2LAnalysis(prompt, mode = 'balanced', enabledModels = []) {
    const baseRequest = {
      method: 'post',
      url: '/p2l/analyze',
      data: {
        prompt,
        priority: mode,
        enabled_models: enabledModels
      }
    }

    // 创建多个稍有不同的请求配置
    const requestConfigs = [
      // 主请求
      { ...baseRequest },
      
      // 备用请求1 - 稍微不同的参数
      {
        ...baseRequest,
        data: {
          ...baseRequest.data,
          temperature: 0.7 // 稍微调整参数
        }
      },
      
      // 备用请求2 - 更简化的请求
      {
        ...baseRequest,
        data: {
          prompt,
          priority: mode
        }
      }
    ]

    return this.race(`p2l-analysis-${Date.now()}`, requestConfigs, {
      timeout: 60000,      // 60秒超时，P2L分析相对较快
      maxConcurrent: 3,    // 最多3个并发
      staggerDelay: 800,   // 800ms错开
      fallbackDelay: 3000, // 3秒后发送备用请求
      retryOnFailure: true
    })
  }

  /**
   * LLM生成竞速请求
   */
  async raceLLMGeneration(model, prompt, messages = []) {
    const baseRequest = {
      method: 'post',
      url: '/llm/generate',
      data: {
        model,
        prompt,
        messages,
        max_tokens: 2000
      }
    }

    // 为LLM请求创建备用配置
    const requestConfigs = [
      // 主请求
      { ...baseRequest },
      
      // 备用请求 - 稍微不同的参数
      {
        ...baseRequest,
        data: {
          ...baseRequest.data,
          temperature: 0.8,
          max_tokens: 1500
        }
      }
    ]

    return this.race(`llm-generation-${model}-${Date.now()}`, requestConfigs, {
      timeout: 150000,     // 150秒超时，与API配置保持一致
      maxConcurrent: 2,    // LLM请求并发数较少
      staggerDelay: 2000,  // 2秒错开，给服务器更多时间
      fallbackDelay: 8000, // 8秒后发送备用请求
      retryOnFailure: true
    })
  }

  /**
   * 健康检查竞速
   */
  async raceHealthCheck() {
    const requestConfigs = [
      { method: 'get', url: '/health' },
      { method: 'get', url: '/models' },
      { method: 'head', url: '/health' } // HEAD请求更快
    ]

    return this.race('health-check', requestConfigs, {
      timeout: 10000,
      maxConcurrent: 3,
      staggerDelay: 200,
      fallbackDelay: 1000,
      retryOnFailure: false
    })
  }
}

// 导入axios用于取消令牌
import axios from 'axios'

// 创建全局实例
export const requestRacer = new RequestRacer()

export default RequestRacer