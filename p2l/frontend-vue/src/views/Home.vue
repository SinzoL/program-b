<template>
  <div class="home-container">
    <!-- 系统状态卡片 -->
    <el-card class="status-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <el-icon class="header-icon"><Monitor /></el-icon>
          <span>系统状态</span>
        </div>
      </template>
      <div class="status-content">
        <el-tag :type="p2lStore.backendHealth ? 'success' : 'danger'" size="large">
          <el-icon><CircleCheck v-if="p2lStore.backendHealth" /><CircleClose v-else /></el-icon>
          {{ p2lStore.backendHealth ? 'P2L服务正常' : 'P2L服务离线' }}
        </el-tag>
        <el-button 
          type="primary" 
          @click="checkHealth" 
          :loading="healthChecking"
          size="small"
        >
          重新检测
        </el-button>
      </div>
    </el-card>

    <!-- 主要功能区域 -->
    <div class="main-content">
      <!-- 左侧：输入和控制面板 -->
      <div class="input-panel">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <el-icon class="header-icon"><EditPen /></el-icon>
              <span>智能提问</span>
            </div>
          </template>
          
          <!-- 优先模式选择 -->
          <div class="priority-section">
            <label class="section-label">优先模式：</label>
            <el-radio-group v-model="selectedMode" @change="onModeChange">
              <el-radio-button label="performance">🏆 性能优先</el-radio-button>
              <el-radio-button label="cost">💰 成本优先</el-radio-button>
              <el-radio-button label="speed">⚡ 速度优先</el-radio-button>
              <el-radio-button label="balanced">⚖️ 平衡模式</el-radio-button>
            </el-radio-group>
          </div>

          <!-- 问题输入 -->
          <div class="input-section">
            <el-input
              v-model="userPrompt"
              type="textarea"
              :rows="4"
              placeholder="请输入您的问题，例如：展示js实现字符串中下划线转化为驼峰"
              maxlength="1000"
              show-word-limit
              @keydown.ctrl.enter="analyzePrompt"
            />
          </div>

          <!-- 操作按钮 -->
          <div class="action-buttons">
            <el-button 
              type="primary" 
              size="large"
              @click="analyzePrompt"
              :loading="p2lStore.loading"
              :disabled="!userPrompt.trim() || !p2lStore.backendHealth"
            >
              <el-icon><MagicStick /></el-icon>
              P2L智能分析
            </el-button>
            <el-button 
              @click="clearAll"
              :disabled="p2lStore.loading"
            >
              <el-icon><Delete /></el-icon>
              清空结果
            </el-button>
          </div>
        </el-card>

        <!-- P2L分析结果 -->
        <el-card v-if="p2lStore.currentAnalysis" class="analysis-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <el-icon class="header-icon"><DataAnalysis /></el-icon>
              <span>P2L智能分析</span>
            </div>
          </template>
          
          <div class="analysis-content">
            <!-- 任务特征 -->
            <div class="task-info">
              <el-descriptions :column="2" border>
                <el-descriptions-item label="任务类型">
                  <el-tag>{{ p2lStore.currentAnalysis?.task_analysis?.task_type || '未知' }}</el-tag>
                </el-descriptions-item>
                <el-descriptions-item label="复杂度">
                  <el-tag :type="getComplexityType(p2lStore.currentAnalysis.complexity)">
                    {{ p2lStore.currentAnalysis?.task_analysis?.complexity || '未知' }}
                  </el-tag>
                </el-descriptions-item>
                <el-descriptions-item label="语言">
                  <el-tag type="info">{{ p2lStore.currentAnalysis?.task_analysis?.language || '未知' }}</el-tag>
                </el-descriptions-item>
                <el-descriptions-item label="推荐模型">
                  <el-tag type="success">{{ p2lStore.currentAnalysis.recommended_model }}</el-tag>
                </el-descriptions-item>
              </el-descriptions>
            </div>

            <!-- 模型排名 -->
            <div class="rankings">
              <h4>🏆 模型智能排名</h4>
              <div class="ranking-list">
                <div 
                  v-for="(rec, index) in p2lStore.sortedRecommendations" 
                  :key="rec.model"
                  class="ranking-item"
                  :class="{ 'top-recommendation': index === 0 }"
                >
                  <div class="rank-badge">{{ index + 1 }}</div>
                  <div class="model-info">
                    <div class="model-name">{{ rec.model }}</div>
                    <div class="model-details">
                      <el-tag size="small">{{ getModelInfo(rec.model)?.provider }}</el-tag>
                      <el-tag size="small" type="info">{{ getModelInfo(rec.model)?.type }}</el-tag>
                    </div>
                  </div>
                  <div class="score-section">
                    <el-progress 
                      :percentage="Math.round(rec.score * 100)" 
                      :color="getScoreColor(rec.score)"
                      :stroke-width="8"
                    />
                    <span class="score-text">{{ (rec.score * 100).toFixed(1) }}%</span>
                  </div>
                  <el-button 
                    type="primary" 
                    size="small"
                    @click="callLLM(rec.model)"
                    :loading="p2lStore.loading"
                  >
                    调用模型
                  </el-button>
                </div>
              </div>
            </div>
          </div>
        </el-card>
      </div>

      <!-- 右侧：聊天历史 -->
      <div class="chat-panel">
        <el-card shadow="hover" class="chat-card">
          <template #header>
            <div class="card-header">
              <el-icon class="header-icon"><ChatDotRound /></el-icon>
              <span>对话历史</span>
              <el-badge :value="p2lStore.chatHistory.length" class="chat-badge" />
            </div>
          </template>
          
          <div class="chat-content" ref="chatContainer">
            <div v-if="p2lStore.chatHistory.length === 0" class="empty-chat">
              <el-empty description="暂无对话记录">
                <el-button type="primary" @click="showExamples">查看示例问题</el-button>
              </el-empty>
            </div>
            
            <div v-else class="chat-messages">
              <div 
                v-for="chat in p2lStore.chatHistory" 
                :key="chat.id"
                class="chat-message"
              >
                <!-- 用户问题 -->
                <div class="message user-message">
                  <div class="message-header">
                    <el-icon><User /></el-icon>
                    <span>您的问题</span>
                    <el-tag size="small">{{ formatTime(chat.timestamp) }}</el-tag>
                  </div>
                  <div class="message-content">{{ chat.prompt }}</div>
                </div>
                
                <!-- AI回答 -->
                <div class="message ai-message">
                  <div class="message-header">
                    <el-icon><Robot /></el-icon>
                    <span>{{ chat.model }}</span>
                    <div class="message-meta">
                      <el-tag size="small" type="success">{{ chat.tokens }} tokens</el-tag>
                      <el-tag size="small" type="warning">${{ chat.cost.toFixed(4) }}</el-tag>
                    </div>
                  </div>
                  <div class="message-content" v-html="formatResponse(chat.response)"></div>
                </div>
              </div>
            </div>
          </div>
        </el-card>
      </div>
    </div>

    <!-- 示例问题对话框 -->
    <el-dialog v-model="examplesVisible" title="示例问题" width="600px">
      <div class="examples-list">
        <div 
          v-for="example in exampleQuestions" 
          :key="example.id"
          class="example-item"
          @click="useExample(example.prompt)"
        >
          <div class="example-category">{{ example.category }}</div>
          <div class="example-prompt">{{ example.prompt }}</div>
          <div class="example-description">{{ example.description }}</div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { useP2LStore } from '../stores/p2l'
import { ElMessage, ElNotification } from 'element-plus'

const p2lStore = useP2LStore()

// 响应式数据
const userPrompt = ref('')
const selectedMode = ref('balanced')
const healthChecking = ref(false)
const examplesVisible = ref(false)
const chatContainer = ref(null)

// 示例问题
const exampleQuestions = ref([
  {
    id: 1,
    category: '编程开发',
    prompt: '展示js实现字符串中下划线转化为驼峰',
    description: '代码实现类问题，适合测试编程能力'
  },
  {
    id: 2,
    category: '创意写作',
    prompt: '写一首关于人工智能的现代诗',
    description: '创意类问题，测试文学创作能力'
  },
  {
    id: 3,
    category: '数据分析',
    prompt: '分析电商网站用户行为数据的关键指标',
    description: '分析类问题，测试逻辑推理能力'
  },
  {
    id: 4,
    category: '技术解释',
    prompt: '解释什么是区块链技术及其应用场景',
    description: '解释类问题，测试知识整理能力'
  }
])

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

const onModeChange = (mode) => {
  p2lStore.setPriorityMode(mode)
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
    await nextTick()
    if (chatContainer.value) {
      chatContainer.value.scrollTop = chatContainer.value.scrollHeight
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
  examplesVisible.value = false
  ElMessage.success('已填入示例问题')
}

// 辅助方法
const getComplexityType = (complexity) => {
  const types = {
    '简单': 'success',
    '中等': 'warning', 
    '复杂': 'danger'
  }
  return types[complexity] || 'info'
}

const getModelInfo = (modelName) => {
  return p2lStore.getModelByName(modelName)
}

const getScoreColor = (score) => {
  if (score >= 0.8) return '#67c23a'
  if (score >= 0.6) return '#e6a23c'
  return '#f56c6c'
}

const formatTime = (timestamp) => {
  return new Date(timestamp).toLocaleTimeString()
}

const formatResponse = (response) => {
  // 检查response是否存在
  if (!response || typeof response !== 'string') {
    return '暂无回复内容'
  }
  
  // 简单的代码高亮处理
  return response
    .replace(/```(\w+)?\n([\s\S]*?)```/g, '<pre class="code-block"><code>$2</code></pre>')
    .replace(/`([^`]+)`/g, '<code class="inline-code">$1</code>')
    .replace(/\n/g, '<br>')
}

// 生命周期
onMounted(() => {
  checkHealth()
})
</script>

<style scoped>
.home-container {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
}

.status-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: bold;
}

.header-icon {
  font-size: 18px;
}

.status-content {
  display: flex;
  align-items: center;
  gap: 15px;
}

.main-content {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  min-height: 600px;
}

.input-panel, .chat-panel {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.priority-section, .input-section {
  margin-bottom: 20px;
}

.section-label {
  display: block;
  margin-bottom: 10px;
  font-weight: bold;
  color: #606266;
}

.action-buttons {
  display: flex;
  gap: 10px;
}

.analysis-card {
  flex: 1;
}

.analysis-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.task-info {
  margin-bottom: 20px;
}

.rankings h4 {
  margin: 0 0 15px 0;
  color: #303133;
}

.ranking-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.ranking-item {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 15px;
  border: 1px solid #ebeef5;
  border-radius: 8px;
  transition: all 0.3s;
}

.ranking-item:hover {
  border-color: #409eff;
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.1);
}

.top-recommendation {
  border-color: #67c23a;
  background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
}

.rank-badge {
  width: 30px;
  height: 30px;
  border-radius: 50%;
  background: #409eff;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  flex-shrink: 0;
}

.top-recommendation .rank-badge {
  background: #67c23a;
}

.model-info {
  flex: 1;
}

.model-name {
  font-weight: bold;
  margin-bottom: 5px;
}

.model-details {
  display: flex;
  gap: 5px;
}

.score-section {
  display: flex;
  align-items: center;
  gap: 10px;
  min-width: 150px;
}

.score-text {
  font-weight: bold;
  color: #409eff;
}

.chat-card {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.chat-content {
  flex: 1;
  max-height: 600px;
  overflow-y: auto;
}

.empty-chat {
  height: 300px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.chat-messages {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.chat-message {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.message {
  padding: 15px;
  border-radius: 8px;
  border: 1px solid #ebeef5;
}

.user-message {
  background: #f0f9ff;
  border-color: #409eff;
}

.ai-message {
  background: #f6ffed;
  border-color: #67c23a;
}

.message-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 10px;
  font-weight: bold;
}

.message-meta {
  margin-left: auto;
  display: flex;
  gap: 5px;
}

.message-content {
  line-height: 1.6;
  color: #303133;
}

.chat-badge {
  margin-left: auto;
}

.examples-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.example-item {
  padding: 15px;
  border: 1px solid #ebeef5;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
}

.example-item:hover {
  border-color: #409eff;
  background: #f0f9ff;
}

.example-category {
  font-size: 12px;
  color: #909399;
  margin-bottom: 5px;
}

.example-prompt {
  font-weight: bold;
  margin-bottom: 5px;
}

.example-description {
  font-size: 14px;
  color: #606266;
}

/* 代码样式 */
:deep(.code-block) {
  background: #f5f5f5;
  padding: 10px;
  border-radius: 4px;
  overflow-x: auto;
  margin: 10px 0;
}

:deep(.inline-code) {
  background: #f5f5f5;
  padding: 2px 4px;
  border-radius: 3px;
  font-family: 'Monaco', 'Consolas', monospace;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .main-content {
    grid-template-columns: 1fr;
  }
}
</style>