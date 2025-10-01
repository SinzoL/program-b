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
    
    // 配置版本（用于检测配置更新）
    configVersion: '2.0.1', // 更新版本号以强制刷新配置
    
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
      { name: 'claude-3-7-sonnet-20250219', provider: 'Anthropic', type: 'Claude', cost: '高', speed: '中', hasApiKey: true },
      { name: 'gemini-1.5-pro', provider: 'Google', type: 'Gemini', cost: '中', speed: '中', hasApiKey: true },
      { name: 'deepseek-chat', provider: 'DeepSeek', type: 'DeepSeek', cost: '低', speed: '中', hasApiKey: true },
      { name: 'deepseek-coder', provider: 'DeepSeek', type: 'DeepSeek', cost: '低', speed: '快', hasApiKey: true },
      { name: 'qwen2.5-72b-instruct', provider: '千问', type: 'Qwen', cost: '低', speed: '中', hasApiKey: true },
      { name: 'qwen-plus', provider: '千问', type: 'Qwen', cost: '中', speed: '中', hasApiKey: true },
      { name: 'qwen-turbo', provider: '千问', type: 'Qwen', cost: '极低', speed: '快', hasApiKey: true }
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
        // 检查配置版本，如果版本不匹配则清除旧配置
        const savedVersion = localStorage.getItem('p2l_config_version')
        if (savedVersion !== this.configVersion) {
          console.log(`配置版本更新 (${savedVersion} -> ${this.configVersion})，清除旧配置...`)
          localStorage.removeItem('p2l_enabled_models')
          localStorage.setItem('p2l_config_version', this.configVersion)
        }
        
        const saved = localStorage.getItem('p2l_enabled_models')
        if (saved) {
          const savedModels = JSON.parse(saved)
          // 过滤掉不存在的模型（比如旧的qwen2.5-plus-1127）
          const validModels = savedModels.filter(modelName => 
            this.availableModels.some(m => m.name === modelName)
          )
          
          // 如果有效模型数量不同，说明有旧模型被移除，需要更新
          if (validModels.length !== savedModels.length) {
            console.log('检测到过时的模型配置，正在更新...')
            // 添加新模型到启用列表
            const currentModelNames = this.availableModels.map(m => m.name)
            const newModels = currentModelNames.filter(name => !validModels.includes(name))
            this.enabledModels = [...validModels, ...newModels]
            // 保存更新后的配置
            this.setEnabledModels(this.enabledModels)
          } else {
            this.enabledModels = validModels
          }
        } else {
          // 默认启用所有模型
          this.enabledModels = this.availableModels.map(m => m.name)
          this.setEnabledModels(this.enabledModels)
        }
      } catch (error) {
        console.error('加载模型配置失败:', error)
        // 默认启用所有模型
        this.enabledModels = this.availableModels.map(m => m.name)
        this.setEnabledModels(this.enabledModels)
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