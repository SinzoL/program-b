/**
 * 大模型上下文对话管理器
 * 负责管理多轮对话、上下文存储、对话切换等核心功能
 */

// 数据存储结构定义
export class ConversationStorage {
  constructor() {
    this.dbName = 'P2LConversations'
    this.dbVersion = 1
    this.storeName = 'conversations'
    this.db = null
  }

  // 初始化IndexedDB
  async init() {
    return new Promise((resolve, reject) => {
      const request = indexedDB.open(this.dbName, this.dbVersion)
      
      request.onerror = () => reject(request.error)
      request.onsuccess = () => {
        this.db = request.result
        resolve(this.db)
      }
      
      request.onupgradeneeded = (event) => {
        const db = event.target.result
        
        // 创建对话存储表
        if (!db.objectStoreNames.contains(this.storeName)) {
          const store = db.createObjectStore(this.storeName, { 
            keyPath: 'id', 
            autoIncrement: false 
          })
          
          // 创建索引
          store.createIndex('createdAt', 'createdAt', { unique: false })
          store.createIndex('updatedAt', 'updatedAt', { unique: false })
          store.createIndex('title', 'title', { unique: false })
        }
      }
    })
  }

  // 保存对话
  async saveConversation(conversation) {
    const transaction = this.db.transaction([this.storeName], 'readwrite')
    const store = transaction.objectStore(this.storeName)
    
    return new Promise((resolve, reject) => {
      const request = store.put(conversation)
      request.onsuccess = () => resolve(conversation)
      request.onerror = () => reject(request.error)
    })
  }

  // 获取所有对话（按更新时间倒序）
  async getAllConversations() {
    const transaction = this.db.transaction([this.storeName], 'readonly')
    const store = transaction.objectStore(this.storeName)
    const index = store.index('updatedAt')
    
    return new Promise((resolve, reject) => {
      const request = index.getAll()
      request.onsuccess = () => {
        // 按更新时间倒序排列
        const conversations = request.result.sort((a, b) => b.updatedAt - a.updatedAt)
        resolve(conversations)
      }
      request.onerror = () => reject(request.error)
    })
  }

  // 获取单个对话
  async getConversation(id) {
    const transaction = this.db.transaction([this.storeName], 'readonly')
    const store = transaction.objectStore(this.storeName)
    
    return new Promise((resolve, reject) => {
      const request = store.get(id)
      request.onsuccess = () => resolve(request.result)
      request.onerror = () => reject(request.error)
    })
  }

  // 删除对话
  async deleteConversation(id) {
    const transaction = this.db.transaction([this.storeName], 'readwrite')
    const store = transaction.objectStore(this.storeName)
    
    return new Promise((resolve, reject) => {
      const request = store.delete(id)
      request.onsuccess = () => resolve(true)
      request.onerror = () => reject(request.error)
    })
  }
}

// 对话数据结构
export class Conversation {
  constructor(id = null) {
    this.id = id || this.generateId()
    this.title = ''
    this.messages = [] // 消息列表
    this.createdAt = Date.now()
    this.updatedAt = Date.now()
    this.summary = '' // 对话摘要（用于上下文压缩）
    this.tokenCount = 0 // 估算的token数量
  }

  // 生成唯一ID
  generateId() {
    return 'conv_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9)
  }

  // 添加消息
  addMessage(type, content, model = null, metadata = {}) {
    const message = {
      id: 'msg_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9),
      type, // 'user' | 'assistant'
      content,
      model, // 使用的模型名称
      timestamp: Date.now(),
      metadata // 额外信息（如处理时间、token数等）
    }
    
    this.messages.push(message)
    this.updatedAt = Date.now()
    
    // 如果是第一条用户消息，生成标题
    if (this.messages.length === 1 && type === 'user') {
      this.generateTitle(content)
    }
    
    // 更新token估算
    this.updateTokenCount()
    
    return message
  }

  // 生成对话标题（使用第一个问题的前60个字符）
  generateTitle(firstQuestion) {
    if (firstQuestion.length <= 60) {
      this.title = firstQuestion
    } else {
      this.title = firstQuestion.substring(0, 60) + '...'
    }
  }

  // 估算token数量（简单估算：中文按字符数，英文按单词数*1.3）
  updateTokenCount() {
    let totalTokens = 0
    
    this.messages.forEach(message => {
      const content = message.content
      // 简单的token估算算法
      const chineseChars = (content.match(/[\u4e00-\u9fff]/g) || []).length
      const englishWords = content.replace(/[\u4e00-\u9fff]/g, '').split(/\s+/).filter(word => word.length > 0).length
      
      totalTokens += chineseChars + Math.ceil(englishWords * 1.3)
    })
    
    this.tokenCount = totalTokens
  }

  // 获取用于API的消息格式
  getMessagesForAPI(maxTokens = 4000) {
    // 如果token数量超过限制，使用摘要+最近消息的策略
    if (this.tokenCount > maxTokens) {
      return this.getCompressedMessages(maxTokens)
    }
    
    return this.messages.map(msg => ({
      role: msg.type === 'user' ? 'user' : 'assistant',
      content: msg.content
    }))
  }

  // 获取压缩后的消息（摘要+最近对话）
  getCompressedMessages(maxTokens) {
    const recentMessages = []
    let tokenCount = 0
    
    // 从最新消息开始往前取
    for (let i = this.messages.length - 1; i >= 0; i--) {
      const message = this.messages[i]
      const messageTokens = this.estimateMessageTokens(message.content)
      
      if (tokenCount + messageTokens > maxTokens * 0.7) { // 保留70%给最近消息
        break
      }
      
      recentMessages.unshift({
        role: message.type === 'user' ? 'user' : 'assistant',
        content: message.content
      })
      tokenCount += messageTokens
    }

    // 如果有摘要且还有剩余token空间，添加摘要
    const result = []
    if (this.summary && recentMessages.length < this.messages.length) {
      result.push({
        role: 'system',
        content: `以下是之前对话的摘要：${this.summary}`
      })
    }
    
    return result.concat(recentMessages)
  }

  // 估算单条消息的token数
  estimateMessageTokens(content) {
    const chineseChars = (content.match(/[\u4e00-\u9fff]/g) || []).length
    const englishWords = content.replace(/[\u4e00-\u9fff]/g, '').split(/\s+/).filter(word => word.length > 0).length
    return chineseChars + Math.ceil(englishWords * 1.3)
  }

  // 生成对话摘要（简单版本，实际可以调用AI接口）
  generateSummary() {
    if (this.messages.length < 4) return // 消息太少不需要摘要
    
    const userMessages = this.messages.filter(msg => msg.type === 'user')
    const assistantMessages = this.messages.filter(msg => msg.type === 'assistant')
    
    let summary = `用户主要询问了${userMessages.length}个问题，涉及：`
    
    // 提取关键词（简单实现）
    const allContent = this.messages.map(msg => msg.content).join(' ')
    const keywords = this.extractKeywords(allContent)
    
    summary += keywords.slice(0, 5).join('、')
    summary += `。助手提供了${assistantMessages.length}次回答。`
    
    this.summary = summary
    return summary
  }

  // 简单的关键词提取
  extractKeywords(text) {
    // 移除标点符号，分词
    const words = text.replace(/[^\u4e00-\u9fff\w\s]/g, ' ')
                     .split(/\s+/)
                     .filter(word => word.length > 1)
    
    // 统计词频
    const wordCount = {}
    words.forEach(word => {
      wordCount[word] = (wordCount[word] || 0) + 1
    })
    
    // 按频率排序，返回前几个
    return Object.entries(wordCount)
                 .sort((a, b) => b[1] - a[1])
                 .map(entry => entry[0])
  }
}

// 对话管理器主类
export class ConversationManager {
  constructor() {
    this.storage = new ConversationStorage()
    this.currentConversation = null
    this.conversations = []
    this.initialized = false
  }

  // 初始化管理器
  async init() {
    if (this.initialized) return
    
    try {
      await this.storage.init()
      await this.loadConversations()
      this.initialized = true
      console.log('✅ 对话管理器初始化成功')
    } catch (error) {
      console.error('❌ 对话管理器初始化失败:', error)
      throw error
    }
  }

  // 加载所有对话
  async loadConversations() {
    try {
      this.conversations = await this.storage.getAllConversations()
      console.log(`📚 加载了 ${this.conversations.length} 个历史对话`)
    } catch (error) {
      console.error('加载对话失败:', error)
      this.conversations = []
    }
  }

  // 创建新对话
  async createNewConversation() {
    // 保存当前对话
    if (this.currentConversation && this.currentConversation.messages.length > 0) {
      await this.saveCurrentConversation()
    }
    
    // 创建新对话
    this.currentConversation = new Conversation()
    console.log('🆕 创建新对话:', this.currentConversation.id)
    
    return this.currentConversation
  }

  // 切换到指定对话
  async switchToConversation(conversationId) {
    // 保存当前对话
    if (this.currentConversation && this.currentConversation.messages.length > 0) {
      await this.saveCurrentConversation()
    }
    
    // 加载目标对话
    const conversation = await this.storage.getConversation(conversationId)
    if (conversation) {
      this.currentConversation = Object.assign(new Conversation(), conversation)
      console.log('🔄 切换到对话:', conversationId)
      return this.currentConversation
    } else {
      throw new Error('对话不存在')
    }
  }

  // 保存当前对话
  async saveCurrentConversation() {
    if (!this.currentConversation) return
    
    try {
      await this.storage.saveConversation(this.currentConversation)
      
      // 更新本地对话列表
      const existingIndex = this.conversations.findIndex(conv => conv.id === this.currentConversation.id)
      if (existingIndex >= 0) {
        this.conversations[existingIndex] = { ...this.currentConversation }
      } else {
        this.conversations.unshift({ ...this.currentConversation })
      }
      
      // 重新排序（按更新时间）
      this.conversations.sort((a, b) => b.updatedAt - a.updatedAt)
      
      console.log('💾 对话已保存:', this.currentConversation.id)
    } catch (error) {
      console.error('保存对话失败:', error)
      throw error
    }
  }

  // 添加用户消息
  async addUserMessage(content) {
    if (!this.currentConversation) {
      await this.createNewConversation()
    }
    
    const message = this.currentConversation.addMessage('user', content)
    await this.saveCurrentConversation()
    
    return message
  }

  // 添加助手回复
  async addAssistantMessage(content, model, metadata = {}) {
    if (!this.currentConversation) {
      throw new Error('没有当前对话')
    }
    
    const message = this.currentConversation.addMessage('assistant', content, model, metadata)
    
    // 如果对话变长，生成摘要
    if (this.currentConversation.messages.length > 10 && !this.currentConversation.summary) {
      this.currentConversation.generateSummary()
    }
    
    await this.saveCurrentConversation()
    
    return message
  }

  // 获取当前对话的API消息格式
  getCurrentMessagesForAPI(maxTokens = 4000) {
    if (!this.currentConversation) {
      return []
    }
    
    return this.currentConversation.getMessagesForAPI(maxTokens)
  }

  // 删除对话
  async deleteConversation(conversationId) {
    try {
      await this.storage.deleteConversation(conversationId)
      
      // 从本地列表中移除
      this.conversations = this.conversations.filter(conv => conv.id !== conversationId)
      
      // 如果删除的是当前对话，创建新对话
      if (this.currentConversation && this.currentConversation.id === conversationId) {
        this.currentConversation = null
      }
      
      console.log('🗑️ 对话已删除:', conversationId)
    } catch (error) {
      console.error('删除对话失败:', error)
      throw error
    }
  }

  // 获取对话列表
  getConversationList() {
    return this.conversations.map(conv => ({
      id: conv.id,
      title: conv.title || '新对话',
      updatedAt: conv.updatedAt,
      messageCount: conv.messages.length,
      preview: conv.messages.length > 0 ? conv.messages[conv.messages.length - 1].content.substring(0, 50) + '...' : ''
    }))
  }

  // 获取当前对话
  getCurrentConversation() {
    return this.currentConversation
  }

  // 清空所有对话（危险操作）
  async clearAllConversations() {
    try {
      // 删除所有对话
      for (const conv of this.conversations) {
        await this.storage.deleteConversation(conv.id)
      }
      
      this.conversations = []
      this.currentConversation = null
      
      console.log('🧹 所有对话已清空')
    } catch (error) {
      console.error('清空对话失败:', error)
      throw error
    }
  }
}

// 创建全局单例并添加便捷方法
class ConversationManagerInstance extends ConversationManager {
  // 添加便捷方法以匹配组件调用
  async initialize() {
    return this.init()
  }
  
  async createConversation() {
    return this.createNewConversation()
  }
  
  async switchConversation(conversationId) {
    return this.switchToConversation(conversationId)
  }
  
  async addMessage(conversationId, message) {
    // 如果不是当前对话，先切换
    if (!this.currentConversation || this.currentConversation.id !== conversationId) {
      await this.switchToConversation(conversationId)
    }
    
    if (message.role === 'user') {
      return this.addUserMessage(message.content)
    } else if (message.role === 'assistant') {
      return this.addAssistantMessage(message.content, message.model, {
        tokens: message.tokens,
        cost: message.cost,
        responseTime: message.responseTime
      })
    }
  }
  
  async getAllConversations() {
    return this.conversations
  }
  
  getCurrentConversationId() {
    return this.currentConversation ? this.currentConversation.id : null
  }
  
  async clearAllConversations() {
    return super.clearAllConversations()
  }
  
  getConversationContext(conversationId) {
    const conversation = this.conversations.find(conv => conv.id === conversationId)
    return conversation ? conversation.getMessagesForAPI() : []
  }
}

export const conversationManager = new ConversationManagerInstance()

// 导出工具函数
export const formatTimestamp = (timestamp) => {
  const date = new Date(timestamp)
  const now = new Date()
  const diffMs = now - date
  const diffMins = Math.floor(diffMs / 60000)
  const diffHours = Math.floor(diffMs / 3600000)
  const diffDays = Math.floor(diffMs / 86400000)

  if (diffMins < 1) return '刚刚'
  if (diffMins < 60) return `${diffMins}分钟前`
  if (diffHours < 24) return `${diffHours}小时前`
  if (diffDays < 7) return `${diffDays}天前`
  
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })
}