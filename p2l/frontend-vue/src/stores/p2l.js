import { defineStore } from 'pinia'
import axios from 'axios'

const api = axios.create({
  baseURL: 'http://localhost:8080',
  timeout: 60000
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
    
    // 模型信息 - 只包含有API密钥的主流模型
    availableModels: [
      { name: 'gpt-4o', provider: 'OpenAI', type: 'GPT', cost: '高', speed: '中', hasApiKey: true },
      { name: 'gpt-4o-mini', provider: 'OpenAI', type: 'GPT', cost: '低', speed: '快', hasApiKey: true },
      { name: 'claude-3-5-sonnet-20241022', provider: 'Anthropic', type: 'Claude', cost: '高', speed: '中', hasApiKey: true },
      { name: 'gemini-1.5-pro', provider: 'Google', type: 'Gemini', cost: '中', speed: '中', hasApiKey: true },
      { name: 'deepseek-chat', provider: 'DeepSeek', type: 'DeepSeek', cost: '低', speed: '中', hasApiKey: true },
      { name: 'deepseek-coder', provider: 'DeepSeek', type: 'DeepSeek', cost: '低', speed: '快', hasApiKey: true }
    ],
    
    // 启用的模型列表
    enabledModels: [],
    
    // 优先模式
    priorityMode: 'balanced'
  }),

  getters: {
    isBackendReady: (state) => state.backendHealth,
    
    getModelByName: (state) => (name) => {
      return state.availableModels.find(model => model.name === name)
    },
    
    // 过滤后的推荐结果（只显示启用的模型）
    sortedRecommendations: (state) => {
      return [...state.recommendations]
        .filter(rec => state.enabledModels.includes(rec.model))
        .sort((a, b) => b.score - a.score)
    },
    
    // 启用的模型信息
    enabledModelInfos: (state) => {
      return state.availableModels.filter(model => 
        state.enabledModels.includes(model.name)
      )
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
          models: this.enabledModels.length > 0 ? this.enabledModels : this.availableModels.map(m => m.name)
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
          response: response.data.response || response.data.content || '暂无回复内容',
          timestamp: new Date(),
          cost: response.data.cost || 0,
          tokens: response.data.tokens || response.data.tokens_used || 0
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

    // 设置启用的模型
    setEnabledModels(models) {
      this.enabledModels = models
      // 保存到localStorage
      localStorage.setItem('p2l_enabled_models', JSON.stringify(models))
    },

    // 初始化启用的模型（从localStorage加载或默认全部启用）
    initializeEnabledModels() {
      try {
        const saved = localStorage.getItem('p2l_enabled_models')
        if (saved) {
          this.enabledModels = JSON.parse(saved)
        } else {
          // 默认启用所有模型
          this.enabledModels = this.availableModels.map(m => m.name)
        }
      } catch (error) {
        console.error('加载模型配置失败:', error)
        // 默认启用所有模型
        this.enabledModels = this.availableModels.map(m => m.name)
      }
    },

    // 清空聊天历史
    clearChatHistory() {
      this.chatHistory = []
      this.currentAnalysis = null
      this.recommendations = []
    }
  }
})