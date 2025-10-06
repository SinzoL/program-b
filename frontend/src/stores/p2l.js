import { defineStore } from 'pinia'
import { p2lApi } from '@/utils/api'

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
    
    // 模型信息 - 从后端API动态获取
    availableModels: [],
    
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
        const response = await p2lApi.get('/health')
        this.backendHealth = response.status === 200
        return this.backendHealth
      } catch (error) {
        console.error('后端服务检查失败:', error)
        this.backendHealth = false
        return false
      }
    },

    // 从后端获取模型列表
    async loadModelsFromBackend() {
      try {
        const response = await p2lApi.get('/models')
        const backendData = response.data
        
        // 处理后端返回的数据格式 {models: [...], total: 42}
        const modelNames = backendData.models || []
        
        // 转换模型名称为前端格式
        this.availableModels = modelNames.map(name => ({
          name,
          provider: this.getProviderDisplayName(this.getProviderFromModelName(name)),
          type: this.getModelType(name),
          cost: this.getCostLevel(this.estimateCostFromModelName(name)),
          speed: this.getSpeedLevel(this.estimateSpeedFromModelName(name)),
          hasApiKey: true
        }))
        
        console.log(`✅ 从后端加载了 ${this.availableModels.length} 个模型`)
        return this.availableModels
      } catch (error) {
        console.error('从后端获取模型列表失败:', error)
        // 如果获取失败，使用默认的几个主要模型
        this.availableModels = [
          { name: 'gpt-4o', provider: 'OpenAI', type: 'GPT', cost: '高', speed: '中', hasApiKey: true },
          { name: 'claude-3-5-sonnet-20241022', provider: 'Anthropic', type: 'Claude', cost: '高', speed: '中', hasApiKey: true },
          { name: 'gemini-1.5-pro', provider: 'Google', type: 'Gemini', cost: '中', speed: '中', hasApiKey: true }
        ]
        return this.availableModels
      }
    },

    // 辅助方法：从模型名称推断提供商
    getProviderFromModelName(modelName) {
      if (modelName.includes('gpt') || modelName.includes('o1')) return 'openai'
      if (modelName.includes('claude')) return 'anthropic'
      if (modelName.includes('gemini')) return 'google'
      if (modelName.includes('deepseek')) return 'deepseek'
      if (modelName.includes('qwen')) return 'qwen'
      if (modelName.includes('llama')) return 'meta'
      if (modelName.includes('yi')) return 'yi'
      return 'unknown'
    },

    // 辅助方法：获取提供商显示名称
    getProviderDisplayName(provider) {
      const providerMap = {
        'openai': 'OpenAI',
        'anthropic': 'Anthropic', 
        'google': 'Google',
        'deepseek': 'DeepSeek',
        'qwen': '千问',
        'meta': 'Meta',
        'yi': '零一万物',
        'yinli': 'yinli代理',
        'probex': 'ProbeX代理',
        'unknown': '未知'
      }
      return providerMap[provider] || provider
    },

    // 辅助方法：从模型名称估算成本
    estimateCostFromModelName(modelName) {
      if (modelName.includes('o1') || modelName.includes('gpt-4')) return 0.015
      if (modelName.includes('claude-3-opus')) return 0.015
      if (modelName.includes('claude') || modelName.includes('gemini-1.5-pro')) return 0.01
      if (modelName.includes('gpt-4o-mini') || modelName.includes('deepseek') || modelName.includes('qwen')) return 0.002
      if (modelName.includes('gemini-1.5-flash')) return 0.001
      return 0.005
    },

    // 辅助方法：从模型名称估算速度
    estimateSpeedFromModelName(modelName) {
      if (modelName.includes('turbo') || modelName.includes('flash') || modelName.includes('mini')) return 0.8
      if (modelName.includes('deepseek') || modelName.includes('qwen')) return 1.0
      if (modelName.includes('o1') || modelName.includes('opus')) return 3.0
      return 1.5
    },

    // 辅助方法：获取模型类型
    getModelType(modelName) {
      if (modelName.includes('gpt')) return 'GPT'
      if (modelName.includes('claude')) return 'Claude'
      if (modelName.includes('gemini')) return 'Gemini'
      if (modelName.includes('deepseek')) return 'DeepSeek'
      if (modelName.includes('qwen')) return 'Qwen'
      return 'LLM'
    },

    // 辅助方法：获取成本等级
    getCostLevel(costPer1k) {
      if (costPer1k <= 0.001) return '极低'
      if (costPer1k <= 0.005) return '低'
      if (costPer1k <= 0.015) return '中'
      return '高'
    },

    // 辅助方法：获取速度等级
    getSpeedLevel(responseTime) {
      if (responseTime <= 1.0) return '快'
      if (responseTime <= 2.0) return '中'
      return '慢'
    },

    // P2L智能分析
    async analyzeWithP2L(prompt, mode = 'balanced') {
      this.loading = true
      try {
        const response = await p2lApi.post('/p2l/analyze', {
          prompt,
          priority: mode, // 修正参数名
          enabled_models: this.enabledModels.length > 0 ? this.enabledModels : this.availableModels.map(m => m.name)
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
    async generateWithLLM(model, prompt, conversationHistory = []) {
      this.loading = true
      try {
        // 构建消息历史，包含完整的对话上下文
        const messages = []
        
        // 添加历史对话记录
        conversationHistory.forEach(item => {
          messages.push({
            role: 'user',
            content: item.prompt
          })
          messages.push({
            role: 'assistant', 
            content: item.response
          })
        })
        
        // 添加当前用户问题
        messages.push({
          role: 'user',
          content: prompt
        })
        
        const response = await p2lApi.post('/llm/generate', {
          model,
          prompt,
          messages, // 传递完整的对话历史
          max_tokens: 2000
        })
        
        // 检查后端是否返回了错误状态
        if (response.data.provider === 'error') {
          throw new Error(response.data.content || response.data.response || 'LLM服务调用失败')
        }
        
        const result = {
          id: Date.now(),
          prompt,
          model,
          response: response.data.response || response.data.content || '暂无回复内容',
          timestamp: new Date(),
          cost: response.data.cost || 0,
          tokens: response.data.tokens || response.data.tokens_used || 0,
          provider: response.data.provider || 'unknown',
          responseTime: response.data.response_time || 0  // 添加响应时间
        }
        
        this.chatHistory.push(result)
        return result
      } catch (error) {
        console.error('LLM调用失败:', error)
        
        // 如果是网络错误或超时，提供更详细的错误信息
        if (error.code === 'ECONNABORTED' || error.message.includes('timeout')) {
          throw new Error(`${model} 响应超时，编程问题可能需要更长时间处理，请稍后重试`)
        } else if (error.response?.status >= 500) {
          throw new Error(`${model} 服务器内部错误，请稍后重试`)
        } else {
          throw new Error(error.message || `${model} 服务暂时不可用`)
        }
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
    async initializeEnabledModels() {
      try {
        // 首先从后端加载模型列表
        await this.loadModelsFromBackend()
        
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
          // 过滤掉不存在的模型
          const validModels = savedModels.filter(modelName => 
            this.availableModels.some(m => m.name === modelName)
          )
          
          // 如果有效模型数量不同，说明有旧模型被移除或新模型被添加，需要更新
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
        
        console.log(`✅ 初始化完成，启用了 ${this.enabledModels.length} 个模型`)
      } catch (error) {
        console.error('初始化模型配置失败:', error)
        // 如果初始化失败，使用默认配置
        if (this.availableModels.length > 0) {
          this.enabledModels = this.availableModels.map(m => m.name)
          this.setEnabledModels(this.enabledModels)
        }
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