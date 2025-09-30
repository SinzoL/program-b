import { defineStore } from 'pinia'
import axios from 'axios'

const api = axios.create({
  baseURL: 'http://localhost:8080',
  timeout: 30000
})

export const useP2LStore = defineStore('p2l', {
  state: () => ({
    // 系统状态
    backendHealth: false,
    loading: false,
    
    // P2L分析结果
    currentAnalysis: null,
    recommendations: [],
    
    // 聊天历史
    chatHistory: [],
    
    // 模型信息
    availableModels: [
      { name: 'gpt-4o', provider: 'OpenAI', type: '通用强化', cost: '高', speed: '中' },
      { name: 'gpt-4o-mini', provider: 'OpenAI', type: '轻量快速', cost: '低', speed: '快' },
      { name: 'claude-3-5-sonnet-20241022', provider: 'Anthropic', type: '推理专家', cost: '高', speed: '中' },
      { name: 'claude-3-5-haiku-20241022', provider: 'Anthropic', type: '快速响应', cost: '中', speed: '快' },
      { name: 'gemini-1.5-pro-002', provider: 'Google', type: '多模态', cost: '中', speed: '中' },
      { name: 'gemini-1.5-flash-002', provider: 'Google', type: '闪电响应', cost: '低', speed: '极快' },
      { name: 'llama-3.1-70b-versatile', provider: 'Meta', type: '开源强化', cost: '中', speed: '中' },
      { name: 'llama-3.1-8b-instant', provider: 'Meta', type: '即时响应', cost: '极低', speed: '极快' },
      { name: 'llama-3.1-70b-instruct', provider: 'Meta', type: '开源指令', cost: '低', speed: '中' },
      { name: 'mixtral-8x7b-32768', provider: 'Mistral', type: '混合专家', cost: '低', speed: '快' },
      { name: 'qwen2.5-72b-instruct', provider: 'Alibaba', type: '中文专家', cost: '中', speed: '中' },
      { name: 'deepseek-v3', provider: 'DeepSeek', type: '深度推理', cost: '中', speed: '中' }
    ],
    
    // 优先模式
    priorityMode: 'balanced'
  }),

  getters: {
    isBackendReady: (state) => state.backendHealth,
    
    getModelByName: (state) => (name) => {
      return state.availableModels.find(model => model.name === name)
    },
    
    sortedRecommendations: (state) => {
      return [...state.recommendations].sort((a, b) => b.score - a.score)
    }
  },

  actions: {
    // 检查后端健康状态
    async checkBackendHealth() {
      try {
        const response = await api.get('/health')
        this.backendHealth = response.status === 200
        return this.backendHealth
      } catch (error) {
        console.error('后端服务检查失败:', error)
        this.backendHealth = false
        return false
      }
    },

    // P2L智能分析
    async analyzeWithP2L(prompt, mode = 'balanced') {
      this.loading = true
      try {
        const response = await api.post('/api/p2l/analyze', {
          prompt,
          mode,
          models: this.availableModels.map(m => m.name)
        })
        
        this.currentAnalysis = response.data
        this.recommendations = response.data.recommendations || []
        
        return response.data
      } catch (error) {
        console.error('P2L分析失败:', error)
        throw new Error('P2L分析服务暂时不可用')
      } finally {
        this.loading = false
      }
    },

    // 调用LLM生成回答
    async generateWithLLM(model, prompt) {
      this.loading = true
      try {
        const response = await api.post('/api/llm/generate', {
          model,
          prompt,
          max_tokens: 2000
        })
        
        const result = {
          id: Date.now(),
          prompt,
          model,
          response: response.data.response,
          timestamp: new Date(),
          cost: response.data.cost || 0,
          tokens: response.data.tokens || 0
        }
        
        this.chatHistory.push(result)
        return result
      } catch (error) {
        console.error('LLM调用失败:', error)
        throw new Error(`${model} 服务暂时不可用`)
      } finally {
        this.loading = false
      }
    },

    // 设置优先模式
    setPriorityMode(mode) {
      this.priorityMode = mode
    },

    // 清空聊天历史
    clearChatHistory() {
      this.chatHistory = []
      this.currentAnalysis = null
      this.recommendations = []
    }
  }
})