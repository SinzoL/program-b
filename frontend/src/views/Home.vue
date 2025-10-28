<template>
  <div class="home-container">
    <!-- 品牌展示区域 -->
    <div class="brand-showcase" v-if="!p2lStore.currentAnalysis && p2lStore.chatHistory.length === 0">
      <div class="brand-content">
        <CubeLogo :size="64" color="#4A90E2" variant="gradient" :animate="true" class="brand-logo" />
        <h1 class="brand-title">P2L智能路由系统</h1>
        <p class="brand-subtitle">集成多个大模型的助手平台，分析问题并推荐合适模型</p>
        <div class="brand-features">
          <div class="feature-item">
            <CubeLogo :size="20" color="#00d4ff" />
            <span>智能路由分析</span>
          </div>
          <div class="feature-item">
            <CubeLogo :size="20" color="#00ff88" />
            <span>多模型支持</span>
          </div>
          <div class="feature-item">
            <CubeLogo :size="20" color="#ff6b6b" />
            <span>实时对话</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 系统状态卡片 -->
    <SystemStatus 
      :backend-health="p2lStore.backendHealth"
      :loading="healthChecking"
      :available-models="p2lStore.availableModels"
      :enabled-models="p2lStore.enabledModels"
      :smart-routing-enabled="smartRoutingEnabled"
      @check-health="checkHealth"
      @update:enabled-models="handleEnabledModelsChange"
      @update:smart-routing="handleSmartRoutingChange"
    />

    <!-- 主要功能区域 -->
    <div class="main-content">
      <!-- 左侧：输入和控制面板 -->
      <div class="input-panel">
        <InputPanel
          ref="inputPanelRef"
          v-model:prompt="userPrompt"
          v-model:selected-mode="selectedMode"
          :loading="p2lStore.loading"
          :backend-health="p2lStore.backendHealth"
          @analyze="analyzePrompt"
          @clear="clearAll"
          @show-examples="showExamples"
          @new-conversation="handleNewConversation"
        />

        <!-- P2L分析结果 -->
        <AnalysisResult
          :analysis="p2lStore.currentAnalysis"
          :recommendations="p2lStore.recommendations"
          :enabled-models="p2lStore.enabledModels"
          :loading="p2lStore.loading"
          :get-model-info="getModelInfo"
          :prompt="userPrompt"
          @call-llm="callLLM"
        />
      </div>

      <!-- 右侧：聊天历史 -->
      <div class="chat-panel">
        <ChatHistory
          ref="chatHistoryRef"
          :chat-history="p2lStore.chatHistory"
          @show-examples="showExamples"
          @clear-history="clearChatHistory"
          @conversation-switched="handleConversationSwitched"
        />
      </div>
    </div>

    <!-- 示例问题对话框 -->
    <ExampleDialog
      v-model="examplesVisible"
      @use-example="useExample"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useP2LStore } from '../stores/p2l'
import { ElNotification } from 'element-plus'

// 导入组件
import SystemStatus from '../components/SystemStatus.vue'
import InputPanel from '../components/InputPanel.vue'
import AnalysisResult from '../components/AnalysisResult.vue'
import ChatHistory from '../components/ChatHistory.vue'
import ExampleDialog from '../components/ExampleDialog.vue'
import CubeLogo from '../components/icons/CubeLogo.vue'

const p2lStore = useP2LStore()

// 响应式数据
const userPrompt = ref('')
const selectedMode = ref('balanced')
const healthChecking = ref(false)
const examplesVisible = ref(false)
const chatHistoryRef = ref(null)
const inputPanelRef = ref(null)
const smartRoutingEnabled = ref(false)

// 方法
const checkHealth = async () => {
  healthChecking.value = true
  try {
    const isHealthy = await p2lStore.checkBackendHealth()
    ElNotification({
      title: isHealthy ? '🚀 连接成功' : '⚠️ 连接失败',
      message: isHealthy ? 
        '<div class="tech-message-content">P2L服务连接正常，所有系统就绪</div>' : 
        '<div class="tech-message-content">P2L服务连接失败，请检查后端服务</div>',
      type: isHealthy ? 'success' : 'error',
      customClass: 'tech-notification',
      duration: 4000,
      dangerouslyUseHTMLString: true
    })
  } finally {
    healthChecking.value = false
  }
}

const analyzePrompt = async () => {
  if (!userPrompt.value.trim()) {
    ElNotification({
      title: '输入提示',
      message: '请输入问题内容',
      type: 'warning',
      customClass: 'tech-notification',
      duration: 3000
    })
    return
  }
  
  if (!p2lStore.backendHealth) {
    ElNotification({
      title: '连接错误',
      message: 'P2L服务未连接，请检查后端服务',
      type: 'error',
      customClass: 'tech-notification',
      duration: 4000
    })
    return
  }

  try {
    await p2lStore.analyzeWithP2L(userPrompt.value, selectedMode.value)
    // 计算启用的模型数量
    const enabledRecommendations = p2lStore.recommendations.filter(rec => 
      p2lStore.enabledModels.includes(rec.model)
    )
    
    // 如果开启了智能路由，自动选择评分最高的模型进行回答
    if (smartRoutingEnabled.value && enabledRecommendations.length > 0) {
      // 找到评分最高的启用模型
      const bestModel = enabledRecommendations[0] // recommendations已经按分数排序
      
      ElNotification({
        title: '智能路由启动',
        message: `P2L分析完成，自动选择 ${bestModel.model} (评分: ${bestModel.score}) 进行回答`,
        type: 'success',
        customClass: 'tech-notification',
        duration: 4000
      })
      
      // 自动调用最佳模型
      await callLLM(bestModel.model)
    } else {
      ElNotification({
        title: 'P2L分析完成',
        message: `为您推荐了 ${enabledRecommendations.length} 个启用的模型，请选择一个进行回答`,
        type: 'success',
        customClass: 'tech-notification',
        duration: 4000
      })
    }
  } catch (error) {
    ElNotification({
      title: '操作失败',
      message: error.message,
      type: 'error',
      customClass: 'tech-notification',
      duration: 4000
    })
  }
}

const callLLM = async (modelName) => {
  try {
    // 获取当前对话历史 - 修复消息格式构建问题
    let conversationHistory = []
    if (chatHistoryRef.value) {
      const currentConversation = chatHistoryRef.value.getCurrentConversation()
      if (currentConversation?.messages) {
        // 正确构建对话历史：成对处理用户问题和AI回复
        const messages = currentConversation.messages
        const pairs = []
        
        for (let i = 0; i < messages.length; i++) {
          const msg = messages[i]
          if (msg.role === 'user' && msg.content.trim()) {
            // 找到对应的AI回复
            let response = ''
            if (i + 1 < messages.length && messages[i + 1].role === 'assistant') {
              response = messages[i + 1].content.trim()
            }
            
            pairs.push({
              prompt: msg.content.trim(),
              response: response,
              model: messages[i + 1]?.model || ''
            })
          }
        }
        
        conversationHistory = pairs
      }
    }
    
    const result = await p2lStore.generateWithLLM(modelName, userPrompt.value, conversationHistory)
    
    // 添加消息到当前对话
    if (chatHistoryRef.value) {
      // 添加用户消息（如果还没有）
      const currentConversation = chatHistoryRef.value.getCurrentConversation()
      const hasUserMessage = currentConversation?.messages.some(msg => 
        msg.role === 'user' && msg.content === userPrompt.value
      )
      
      if (!hasUserMessage) {
        await chatHistoryRef.value.addMessageToCurrentConversation({
          role: 'user',
          content: userPrompt.value,
          timestamp: new Date().toISOString()
        })
      }
      
      // 添加AI回复
      await chatHistoryRef.value.addMessageToCurrentConversation({
        role: 'assistant',
        content: result.response,
        model: modelName,
        tokens: result.tokens || 0,
        cost: result.cost || 0,
        responseTime: result.responseTime || 0,
        timestamp: new Date().toISOString()
      })
      
      // 滚动到最新消息
      chatHistoryRef.value.scrollToBottom()
    }
    
    // 清空输入框
    if (inputPanelRef.value) {
      inputPanelRef.value.clearInput()
    }
    
    ElNotification({
      title: '生成完成',
      message: `${modelName} 已生成回答`,
      type: 'success',
      customClass: 'tech-notification',
      duration: 4000
    })
  } catch (error) {
    ElNotification({
      title: '请求失败',
      message: error.message,
      type: 'error',
      customClass: 'tech-notification',
      duration: 4000
    })
  }
}

const clearAll = () => {
  userPrompt.value = ''
  ElNotification({
    title: '输入内容',
    message: '已清空输入内容',
    type: 'success',
    customClass: 'tech-notification',
    duration: 4000
  })
}

const clearChatHistory = () => {
  p2lStore.clearChatHistory()
  ElNotification({
    title: '对话历史',
    message: '已清空对话历史',
    type: 'success',
    customClass: 'tech-notification',
    duration: 4000
  })
}

const showExamples = () => {
  examplesVisible.value = true
}

const useExample = (prompt) => {
  userPrompt.value = prompt
  ElNotification({
    title: '示例问题',
    message: '示例问题已填入',
    type: 'success',
    customClass: 'tech-notification',
    duration: 4000
  })
}

const handleEnabledModelsChange = (enabledModels) => {
  p2lStore.setEnabledModels(enabledModels)
  ElNotification({
    title: '模型更新',
    message: `已更新模型配置，当前启用 ${enabledModels.length} 个模型`,
    type: 'success',
    customClass: 'tech-notification',
    duration: 4000
  })
}

// 智能路由开关处理
const handleSmartRoutingChange = (enabled) => {
  smartRoutingEnabled.value = enabled
  ElNotification({
    title: '智能路由',
    message: enabled ? 
      '已开启智能路由，分析后将自动选择最佳模型回答' : 
      '已关闭智能路由，需要手动选择模型回答',
    type: 'info',
    customClass: 'tech-notification',
    duration: 4000
  })
}

// 新对话管理相关函数
const handleNewConversation = (conversation) => {
  console.log('✅ 新对话已创建:', conversation.id)
  
  // 通知ChatHistory组件处理新对话
  if (chatHistoryRef.value) {
    chatHistoryRef.value.handleNewConversation(conversation)
  }
  
  ElNotification({
    title: '新对话',
    message: '已创建新的对话窗口',
    type: 'success',
    customClass: 'tech-notification',
    duration: 3000
  })
}

const handleConversationSwitched = (conversationId) => {
  console.log('✅ 切换到对话:', conversationId)
  
  ElNotification({
    title: '对话切换',
    message: '已切换到选定的对话窗口',
    type: 'info',
    customClass: 'tech-notification',
    duration: 2000
  })
}

// 辅助方法
const getModelInfo = (modelName) => {
  return p2lStore.getModelByName(modelName)
}

// 生命周期
onMounted(async () => {
  // 初始化启用的模型
  await p2lStore.initializeEnabledModels()
  checkHealth()
})
</script>

<style scoped>
.home-container {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
  min-height: calc(100vh - 40px); /* 减去padding */
  height: auto; /* 允许内容撑开高度 */
  display: flex;
  flex-direction: column;
  overflow-x: hidden; /* 禁用水平滚动 */
  box-sizing: border-box; /* 确保padding包含在宽度内 */
}

.brand-showcase {
  background: #fafafa;
  border: 2px solid #e0e0e0;
  border-radius: 16px;
  padding: 40px 20px;
  margin-bottom: 20px;
  text-align: center;
  position: relative;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.brand-content {
  position: relative;
  z-index: 1;
}

.brand-logo {
  margin-bottom: 20px;
  filter: drop-shadow(0 4px 12px rgba(74, 144, 226, 0.4));
}

.brand-title {
  font-size: 2.5rem;
  font-weight: bold;
  color: #2c3e50;
  margin: 0 0 16px 0;
}

.brand-subtitle {
  font-size: 1.1rem;
  color: #5a6c7d;
  margin: 0 0 32px 0;
  max-width: 600px;
  margin-left: auto;
  margin-right: auto;
  line-height: 1.6;
}

.brand-features {
  display: flex;
  justify-content: center;
  gap: 32px;
  flex-wrap: wrap;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #555;
  font-weight: 500;
  padding: 8px 16px;
  background: #f8f9fa;
  border-radius: 20px;
  border: 1px solid #d0d0d0;
  transition: all 0.3s ease;
}

.feature-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  border-color: #4A90E2;
  background: #ffffff;
}

@media (max-width: 768px) {
  .brand-title {
    font-size: 2rem;
  }
  
  .brand-features {
    gap: 16px;
  }
  
  .feature-item {
    font-size: 0.9rem;
  }
}
=======
.feature-item {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #555;
  font-weight: 500;
  padding: 8px 16px;
  background: #f8f9fa;
  border-radius: 20px;
  border: 1px solid #d0d0d0;
  transition: all 0.3s ease;
}

.feature-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  border-color: #4A90E2;
  background: #ffffff;
}



.brand-content {
  position: relative;
  z-index: 1;
}

.brand-logo {
  margin-bottom: 20px;
  filter: drop-shadow(0 4px 12px rgba(74, 144, 226, 0.4));
}

.brand-title {
  font-size: 2.5rem;
  font-weight: bold;
  color: #2c3e50;
  margin: 0 0 16px 0;
}

.brand-subtitle {
  font-size: 1.1rem;
  color: #5a6c7d;
  margin: 0 0 32px 0;
  max-width: 600px;
  margin-left: auto;
  margin-right: auto;
  line-height: 1.6;
}

.brand-features {
  display: flex;
  justify-content: center;
  gap: 32px;
  flex-wrap: wrap;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #666;
  font-weight: 500;
  padding: 8px 16px;
  background: #ffffff;
  border-radius: 20px;
  border: 1px solid #e0e0e0;
  transition: all 0.3s ease;
}

.feature-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  border-color: #4A90E2;
}

@media (max-width: 768px) {
  .brand-title {
    font-size: 2rem;
  }
  
  .brand-features {
    gap: 16px;
  }
  
  .feature-item {
    font-size: 0.9rem;
  }
}

.main-content {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  flex: 1;
  min-height: 700px; /* 确保有足够的最小高度 */
  overflow-x: hidden; /* 禁用水平滚动 */
  overflow-y: visible; /* 允许垂直内容显示 */
  width: 100%; /* 确保不超出容器宽度 */
  box-sizing: border-box;
}

.input-panel, .chat-panel {
  display: flex;
  flex-direction: column;
  gap: 20px;
  min-height: 700px; /* 确保有足够高度 */
  overflow-x: hidden; /* 禁用水平滚动 */
  overflow-y: visible; /* 允许垂直内容显示 */
  width: 100%; /* 确保不超出网格列宽度 */
  box-sizing: border-box;
}

/* 确保子组件能够正确显示 */
.input-panel > :deep(*),
.chat-panel > :deep(*) {
  flex-shrink: 0;
}

/* AnalysisResult组件需要更多空间 */
.input-panel > :deep(*:last-child) {
  flex: 1;
  min-height: 700px; /* 确保AnalysisResult有足够高度 */
  overflow: visible; /* 允许内容完全显示 */
}

.chat-panel > :deep(*:last-child) {
  flex: 1;
  min-height: 600px; /* 确保ChatHistory有足够高度 */
  overflow: visible; /* 允许内容完全显示 */
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .main-content {
    grid-template-columns: 1fr;
    height: auto;
    min-height: calc(100vh - 200px);
  }
  
  .input-panel, .chat-panel {
    height: auto;
    min-height: 400px;
  }
}

/* 移动端优化 */
@media (max-width: 768px) {
  .home-container {
    padding: 10px;
    height: auto;
  }
  
  .main-content {
    gap: 15px;
  }
  
  .input-panel, .chat-panel {
    gap: 15px;
  }
}


</style>