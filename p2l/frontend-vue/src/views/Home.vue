<template>
  <div class="home-container">
    <!-- 系统状态卡片 -->
    <SystemStatus 
      :backend-health="p2lStore.backendHealth"
      :loading="healthChecking"
      :available-models="p2lStore.availableModels"
      :enabled-models="p2lStore.enabledModels"
      @check-health="checkHealth"
      @update:enabled-models="handleEnabledModelsChange"
    />

    <!-- 主要功能区域 -->
    <div class="main-content">
      <!-- 左侧：输入和控制面板 -->
      <div class="input-panel">
        <InputPanel
          v-model:prompt="userPrompt"
          v-model:selected-mode="selectedMode"
          :loading="p2lStore.loading"
          :backend-health="p2lStore.backendHealth"
          @analyze="analyzePrompt"
          @clear="clearAll"
          @show-examples="showExamples"
        />

        <!-- P2L分析结果 -->
        <AnalysisResult
          :analysis="p2lStore.currentAnalysis"
          :recommendations="p2lStore.recommendations"
          :enabled-models="p2lStore.enabledModels"
          :loading="p2lStore.loading"
          :get-model-info="getModelInfo"
          @call-llm="callLLM"
        />
      </div>

      <!-- 右侧：聊天历史 -->
      <div class="chat-panel">
        <ChatHistory
          ref="chatHistoryRef"
          :chat-history="p2lStore.chatHistory"
          @show-examples="showExamples"
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
import { ElMessage, ElNotification } from 'element-plus'

// 导入组件
import SystemStatus from '../components/SystemStatus.vue'
import InputPanel from '../components/InputPanel.vue'
import AnalysisResult from '../components/AnalysisResult.vue'
import ChatHistory from '../components/ChatHistory.vue'
import ExampleDialog from '../components/ExampleDialog.vue'

const p2lStore = useP2LStore()

// 响应式数据
const userPrompt = ref('')
const selectedMode = ref('balanced')
const healthChecking = ref(false)
const examplesVisible = ref(false)
const chatHistoryRef = ref(null)

// 方法
const checkHealth = async () => {
  healthChecking.value = true
  try {
    const isHealthy = await p2lStore.checkBackendHealth()
    ElMessage({
      type: isHealthy ? 'success' : 'error',
      message: isHealthy ? 'P2L服务连接正常' : 'P2L服务连接失败'
    })
  } finally {
    healthChecking.value = false
  }
}

const analyzePrompt = async () => {
  if (!userPrompt.value.trim()) {
    ElMessage.warning('请输入问题内容')
    return
  }
  
  if (!p2lStore.backendHealth) {
    ElMessage.error('P2L服务未连接，请检查后端服务')
    return
  }

  try {
    await p2lStore.analyzeWithP2L(userPrompt.value, selectedMode.value)
    ElNotification({
      title: 'P2L分析完成',
      message: `为您推荐了 ${p2lStore.recommendations.length} 个模型`,
      type: 'success'
    })
  } catch (error) {
    ElMessage.error(error.message)
  }
}

const callLLM = async (modelName) => {
  try {
    const result = await p2lStore.generateWithLLM(modelName, userPrompt.value)
    ElNotification({
      title: '生成完成',
      message: `${modelName} 已生成回答`,
      type: 'success'
    })
    
    // 滚动到最新消息
    if (chatHistoryRef.value) {
      chatHistoryRef.value.scrollToBottom()
    }
  } catch (error) {
    ElMessage.error(error.message)
  }
}

const clearAll = () => {
  userPrompt.value = ''
  p2lStore.clearChatHistory()
  ElMessage.success('已清空所有结果')
}

const showExamples = () => {
  examplesVisible.value = true
}

const useExample = (prompt) => {
  userPrompt.value = prompt
  ElMessage.success('已填入示例问题')
}

const handleEnabledModelsChange = (enabledModels) => {
  p2lStore.setEnabledModels(enabledModels)
  ElMessage.success(`已更新模型配置，当前启用 ${enabledModels.length} 个模型`)
}

// 辅助方法
const getModelInfo = (modelName) => {
  return p2lStore.getModelByName(modelName)
}

// 生命周期
onMounted(() => {
  // 初始化启用的模型
  p2lStore.initializeEnabledModels()
  checkHealth()
})
</script>

<style scoped>
.home-container {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
}

.main-content {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  height: calc(100vh - 200px); /* 使用视口高度减去顶部空间 */
  min-height: 600px;
}

.input-panel, .chat-panel {
  display: flex;
  flex-direction: column;
  gap: 20px;
  height: 100%; /* 占满父容器高度 */
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .main-content {
    grid-template-columns: 1fr;
  }
}
</style>