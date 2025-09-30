<template>
  <el-card shadow="hover" class="chat-card">
    <template #header>
      <div class="card-header">
        <el-icon class="header-icon"><ChatDotRound /></el-icon>
        <span>对话历史</span>
        <el-badge :value="chatHistory.length" class="chat-badge" />
        <el-button 
          v-if="chatHistory.length > 1"
          type="text" 
          size="small"
          @click="toggleHistoryView"
          class="toggle-history-btn"
        >
          {{ showAllHistory ? '折叠历史' : `展开全部 (${chatHistory.length})` }}
          <el-icon>
            <ArrowUp v-if="showAllHistory" />
            <ArrowDown v-else />
          </el-icon>
        </el-button>
      </div>
    </template>
    
    <div class="chat-content" ref="chatContainer">
      <div v-if="chatHistory.length === 0" class="empty-chat">
        <el-empty description="暂无对话记录">
          <el-button type="primary" @click="handleShowExamples">查看示例问题</el-button>
        </el-empty>
      </div>
      
      <div v-else class="chat-messages">
        <!-- 显示历史记录提示 -->
        <div v-if="!showAllHistory && chatHistory.length > 1" class="history-hint">
          <el-alert
            :title="`还有 ${chatHistory.length - 1} 条历史对话`"
            type="info"
            :closable="false"
            show-icon
          >
            <template #default>
              <span>点击右上角"展开全部"查看所有对话记录</span>
            </template>
          </el-alert>
        </div>
        
        <div 
          v-for="chat in displayedHistory" 
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
</template>

<script setup>
import { ref, computed, nextTick, defineProps, defineEmits } from 'vue'

const props = defineProps({
  chatHistory: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['show-examples'])

const showAllHistory = ref(false)
const chatContainer = ref(null)

// 计算属性 - 显示的历史记录
const displayedHistory = computed(() => {
  if (showAllHistory.value || props.chatHistory.length <= 1) {
    return props.chatHistory
  }
  // 只显示最新的一条
  return props.chatHistory.slice(-1)
})

const toggleHistoryView = () => {
  showAllHistory.value = !showAllHistory.value
  // 如果展开了历史记录，滚动到底部显示最新消息
  if (showAllHistory.value) {
    nextTick(() => {
      if (chatContainer.value) {
        chatContainer.value.scrollTop = chatContainer.value.scrollHeight
      }
    })
  }
}

const handleShowExamples = () => {
  emit('show-examples')
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

// 暴露滚动到底部的方法
const scrollToBottom = () => {
  nextTick(() => {
    if (chatContainer.value) {
      chatContainer.value.scrollTop = chatContainer.value.scrollHeight
    }
  })
}

defineExpose({
  scrollToBottom
})
</script>

<style scoped>
.chat-card {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.chat-card :deep(.el-card__body) {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 20px;
  overflow: hidden;
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

.chat-content {
  flex: 1;
  overflow-y: auto;
  padding-right: 10px;
}

/* 自定义滚动条样式 */
.chat-content::-webkit-scrollbar {
  width: 6px;
}

.chat-content::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.chat-content::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.chat-content::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

.empty-chat {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 300px;
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

.toggle-history-btn {
  margin-left: 10px;
  padding: 4px 8px;
}

.history-hint {
  margin-bottom: 15px;
}

.history-hint :deep(.el-alert) {
  border-radius: 8px;
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
</style>