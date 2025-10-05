<template>
  <el-card class="current-chat-card tech-card" shadow="hover">
    <template #header>
      <div class="current-header">
        <div class="current-title">
          <TechIcons name="brain" :size="20" color="#00ff88" />
          <span>对话</span>
          <el-tag size="small" type="success" class="tech-tag">
            {{ conversation.messages.length }} 条消息
          </el-tag>
          <el-tag size="small" type="info" class="time-tag">
            {{ formatTime(conversation.updatedAt) }}
          </el-tag>
        </div>
        <div class="current-meta">
          <span class="conversation-id">ID: {{ conversation.id.substring(0, 8) }}</span>
          <span class="total-tokens">{{ getTotalTokens() }} tokens</span>
          <span class="total-cost">${{ getTotalCost().toFixed(4) }}</span>
        </div>
      </div>
    </template>
    
    <div class="conversation-content">
      <!-- 消息列表 -->
      <div class="messages-container" ref="messagesContainer">
        <div 
          v-for="(message, index) in conversation.messages" 
          :key="index"
          class="message-item"
          :class="{ 
            'user-message': message.role === 'user',
            'assistant-message': message.role === 'assistant'
          }"
        >
          <!-- 用户消息 -->
          <div v-if="message.role === 'user'" class="user-message-content">
            <div class="message-header">
              <TechIcons name="analytics" :size="16" color="#00d4ff" />
              <span class="message-label">用户</span>
              <span class="message-time">{{ formatTime(message.timestamp) }}</span>
            </div>
            <div class="message-body user-body">
              {{ message.content }}
            </div>
          </div>
          
          <!-- AI回复消息 -->
          <div v-else-if="message.role === 'assistant'" class="assistant-message-content">
            <div class="message-header">
              <TechIcons name="robot" :size="16" color="#00ff88" />
              <span class="message-label">{{ message.model || 'AI助手' }}</span>
              <el-tag v-if="message.tokens" size="small" type="success" class="tokens-tag">
                {{ message.tokens }} tokens
              </el-tag>
              <el-tag v-if="message.responseTime" size="small" type="info" class="time-tag">
                {{ formatResponseTime(message.responseTime) }}
              </el-tag>
              <span class="message-time">{{ formatTime(message.timestamp) }}</span>
            </div>
            <div class="message-body assistant-body" v-html="formatResponse(message.content)"></div>
            <div v-if="message.cost" class="message-cost">
              成本: ${{ message.cost.toFixed(4) }}
            </div>
          </div>
        </div>
        
        <!-- 空状态提示 -->
        <div v-if="conversation.messages.length === 0" class="empty-conversation">
          <div class="empty-icon">
            <TechIcons name="brain" :size="48" color="#00d4ff" />
          </div>
          <h3>开始新对话</h3>
          <p>在下方输入您的问题，开始与AI的智能对话</p>
        </div>
      </div>
    </div>
  </el-card>
</template>

<script setup>
import { ref, nextTick, watch } from 'vue'
import TechIcons from '../icons/TechIcons.vue'

const props = defineProps({
  conversation: {
    type: Object,
    required: true
  }
})

const messagesContainer = ref(null)

// 格式化时间
const formatTime = (timestamp) => {
  if (!timestamp) return ''
  
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
  
  return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})
}

// 格式化响应时间
const formatResponseTime = (responseTime) => {
  if (!responseTime || responseTime === 0) {
    return '耗时: --'
  }
  return `耗时: ${responseTime.toFixed(2)}s`
}

// 格式化回复内容
const formatResponse = (response) => {
  if (!response || typeof response !== 'string') {
    return '暂无回复内容'
  }
  
  return response
    .replace(/```(\w+)?\n([\s\S]*?)```/g, '<pre class="code-block"><code>$2</code></pre>')
    .replace(/`([^`]+)`/g, '<code class="inline-code">$1</code>')
    .replace(/\n/g, '<br>')
}

// 计算总token数
const getTotalTokens = () => {
  return props.conversation.messages.reduce((total, message) => {
    return total + (message.tokens || 0)
  }, 0)
}

// 计算总成本
const getTotalCost = () => {
  return props.conversation.messages.reduce((total, message) => {
    return total + (message.cost || 0)
  }, 0)
}

// 滚动到底部
const scrollToBottom = () => {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
  })
}

// 监听消息变化，自动滚动到底部
watch(() => props.conversation.messages.length, () => {
  scrollToBottom()
}, { immediate: true })

// 暴露方法
defineExpose({
  scrollToBottom
})
</script>

<style scoped>
.current-chat-card {
  height: 100%;
  min-height: 650px;
  border: 2px solid #00ff88;
  background: linear-gradient(135deg, rgba(0, 255, 136, 0.05) 0%, rgba(0, 255, 136, 0.1) 100%);
  box-shadow: 0 4px 20px rgba(0, 255, 136, 0.3);
  display: flex;
  flex-direction: column;
  position: relative;
  overflow: hidden;
}

.current-chat-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: linear-gradient(90deg, transparent, #00ff88, transparent);
  animation: scan 2s infinite;
}

@keyframes scan {
  0% { transform: translateX(-100%); }
  100% { transform: translateX(100%); }
}

.current-chat-card :deep(.el-card__body) {
  flex: 1;
  min-height: 600px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background: rgba(15, 15, 35, 0.02);
  padding: 0;
}

.current-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.current-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: bold;
  color: #00ff88;
}

.tech-tag {
  background: linear-gradient(135deg, #00ff88, #00cc66);
  color: white;
  border: none;
  box-shadow: 0 2px 8px rgba(0, 255, 136, 0.3);
}

.time-tag {
  background: linear-gradient(135deg, #00d4ff, #0099cc);
  color: white;
  border: none;
  box-shadow: 0 2px 8px rgba(0, 212, 255, 0.3);
  font-family: 'Monaco', 'Consolas', monospace;
  font-size: 11px;
}

.tokens-tag {
  background: linear-gradient(135deg, #00ff88, #00cc66);
  color: white;
  border: none;
  box-shadow: 0 2px 8px rgba(0, 255, 136, 0.3);
  font-family: 'Monaco', 'Consolas', monospace;
  font-size: 11px;
}

.current-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 12px;
}

.conversation-id {
  color: #888;
  font-family: 'Monaco', 'Consolas', monospace;
}

.total-tokens {
  color: #00ff88;
  font-weight: 500;
  text-shadow: 0 0 4px rgba(0, 255, 136, 0.5);
}

.total-cost {
  color: #ff6b6b;
  font-weight: 500;
  text-shadow: 0 0 4px rgba(255, 107, 107, 0.5);
}

.conversation-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  height: 100%;
}

.messages-container {
  flex: 1;
  overflow-y: auto; /* 启用垂直滚动 */
  overflow-x: hidden; /* 禁用水平滚动 */
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 16px;
  max-height: 1100px; /* 固定消息容器最大高度 */
  min-height: 1100px; /* 最小高度保证可见性 */
}

.message-item {
  display: flex;
  flex-direction: column;
  margin-bottom: 16px;
}

.user-message-content,
.assistant-message-content {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.message-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  font-weight: 500;
}

.message-label {
  font-weight: 600;
}

.message-time {
  color: #888;
  font-size: 11px;
  margin-left: auto;
}

.message-body {
  padding: 12px 16px;
  border-radius: 8px;
  line-height: 1.6;
  word-break: break-word;
  font-size: 14px;
}

.user-body {
  background: linear-gradient(135deg, rgba(0, 212, 255, 0.1), rgba(0, 212, 255, 0.05));
  border: 1px solid rgba(0, 212, 255, 0.3);
  color: #fff;
  border-left: 4px solid #00d4ff;
}

.assistant-body {
  background: linear-gradient(135deg, rgba(0, 255, 136, 0.1), rgba(0, 255, 136, 0.05));
  border: 1px solid rgba(0, 255, 136, 0.3);
  color: #fff;
  border-left: 4px solid #00ff88;
}

.message-cost {
  font-size: 11px;
  color: #ff6b6b;
  text-align: right;
  font-family: 'Monaco', 'Consolas', monospace;
}

.empty-conversation {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  color: #888;
  padding: 40px;
}

.empty-icon {
  margin-bottom: 16px;
  opacity: 0.6;
}

.empty-conversation h3 {
  color: #00d4ff;
  margin: 0 0 8px 0;
  font-size: 1.2rem;
}

.empty-conversation p {
  margin: 0;
  font-size: 0.9rem;
  line-height: 1.5;
}

/* 滚动条样式 */
.messages-container::-webkit-scrollbar {
  width: 6px;
}

.messages-container::-webkit-scrollbar-track {
  background: rgba(0, 212, 255, 0.1);
  border-radius: 3px;
}

.messages-container::-webkit-scrollbar-thumb {
  background: rgba(0, 212, 255, 0.5);
  border-radius: 3px;
}

.messages-container::-webkit-scrollbar-thumb:hover {
  background: rgba(0, 212, 255, 0.7);
}

/* 代码样式 */
:deep(.code-block) {
  background: linear-gradient(135deg, rgba(15, 15, 35, 0.1), rgba(0, 212, 255, 0.05));
  border: 1px solid rgba(0, 212, 255, 0.2);
  padding: 12px;
  border-radius: 6px;
  overflow-x: auto;
  margin: 10px 0;
  font-family: 'Monaco', 'Consolas', monospace;
  font-size: 13px;
  box-shadow: 0 2px 8px rgba(0, 212, 255, 0.1);
}

:deep(.inline-code) {
  background: rgba(0, 212, 255, 0.1);
  color: #00d4ff;
  padding: 2px 6px;
  border-radius: 4px;
  font-family: 'Monaco', 'Consolas', monospace;
  font-size: 13px;
  border: 1px solid rgba(0, 212, 255, 0.2);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .current-header {
    flex-direction: column;
    gap: 8px;
    align-items: flex-start;
  }
  
  .current-meta {
    align-self: flex-end;
  }
  
  .messages-container {
    padding: 12px;
  }
  
  .message-body {
    padding: 10px 12px;
    font-size: 13px;
  }
}
</style>