<template>
  <div class="chat-history-container">
    <!-- Tab切换界面 -->
    <el-tabs v-model="activeTab" class="chat-tabs" type="border-card">
      <!-- 当前对话Tab -->
      <el-tab-pane label="当前对话" name="current" class="tab-pane">
        <template #label>
          <span class="tab-label">
            <el-icon><ChatDotRound /></el-icon>
            当前对话
          </span>
        </template>
        
        <div class="current-chat">
      <!-- 空状态：显示占位符结构 -->
      <el-card v-if="chatHistory.length === 0" class="placeholder-chat" shadow="hover">
        <template #header>
          <div class="placeholder-header">
            <div class="placeholder-title">
              <el-icon class="header-icon"><ChatDotRound /></el-icon>
              <span>对话区域</span>
              <el-tag size="small" type="info">等待输入</el-tag>
            </div>
          </div>
        </template>
        
        <div class="placeholder-content">
          <!-- 问题占位符 -->
          <div class="content-section">
            <div class="section-header">
              <el-icon><User /></el-icon>
              <span>问题</span>
            </div>
            <div class="section-content placeholder-text">
              <div class="placeholder-message">
                <el-icon class="placeholder-icon"><Edit /></el-icon>
                <span>请在左侧输入您的问题，然后选择合适的模型进行分析...</span>
              </div>
            </div>
          </div>
          
          <!-- 回答占位符 -->
          <div class="content-section">
            <div class="section-header">
              <el-icon><Robot /></el-icon>
              <span>回答</span>
            </div>
            <div class="section-content placeholder-text">
              <div class="placeholder-message">
                <el-icon class="placeholder-icon"><Loading /></el-icon>
                <span>模型的回答将在这里显示...</span>
              </div>
            </div>
          </div>
        </div>
      </el-card>

      <!-- 有对话记录时显示最新对话 - 使用统一模板 -->
      <el-card v-else-if="chatHistory.length > 0 && latestChat" class="placeholder-chat" shadow="hover">
        <template #header>
          <div class="placeholder-header">
            <div class="placeholder-title">
              <el-icon class="header-icon"><ChatDotRound /></el-icon>
              <span>当前对话</span>
              <el-tag size="small" type="success">{{ latestChat.model }}</el-tag>
            </div>
            <div class="current-meta">
              <span class="chat-time">{{ formatTime(latestChat.timestamp) }}</span>
              <span class="chat-cost">${{ latestChat.cost.toFixed(4) }}</span>
            </div>
          </div>
        </template>
        
        <div class="placeholder-content">
          <!-- 问题区域 - 填充实际内容 -->
          <div class="content-section">
            <div class="section-header">
              <el-icon><User /></el-icon>
              <span>问题</span>
            </div>
            <div class="section-content question-content">
              {{ latestChat.prompt }}
            </div>
          </div>
          
          <!-- 回答区域 - 填充实际内容 -->
          <div class="content-section">
            <div class="section-header">
              <el-icon><Robot /></el-icon>
              <span>回答 ({{ latestChat.tokens }} tokens)</span>
            </div>
            <div class="section-content answer-content" v-html="formatResponse(latestChat.response)"></div>
          </div>
        </div>
      </el-card>
        </div>
      </el-tab-pane>

      <!-- 历史记录Tab -->
      <el-tab-pane name="history" class="tab-pane">
        <template #label>
          <span class="tab-label">
            <el-icon><History /></el-icon>
            历史记录
            <el-badge v-if="chatHistory.length > 0" :value="chatHistory.length" class="tab-badge" />
          </span>
        </template>
        
        <div class="history-panel">
        <el-card shadow="hover" class="history-card">
          <template #header>
            <div class="history-header">
              <div class="history-title">
                <el-icon><History /></el-icon>
                <span>历史对话记录</span>
                <el-badge :value="historicalChats.length" class="history-badge" />
              </div>
              <div class="history-actions">
                <el-button 
                  type="text" 
                  size="small"
                  @click="clearHistory"
                  class="clear-btn"
                >
                  <el-icon><Delete /></el-icon>
                  清空历史
                </el-button>
              </div>
            </div>
          </template>
          
          <!-- 搜索框 -->
          <div class="search-section">
            <el-input
              v-model="searchKeyword"
              placeholder="搜索历史对话..."
              size="default"
              class="search-input"
              clearable
            >
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
            </el-input>
          </div>
          
          <!-- 历史记录列表 -->
          <div class="history-list">
            <div v-if="filteredHistoricalChats.length === 0" class="no-results">
              <el-empty description="没有找到匹配的历史记录" />
            </div>
            
            <div v-else class="history-items">
              <div 
                v-for="(chat, index) in filteredHistoricalChats" 
                :key="chat.id"
                class="history-item"
                :class="{ 'expanded': expandedItems.has(chat.id) }"
              >
                <div class="item-header" @click="toggleItemExpansion(chat.id)">
                  <div class="item-info">
                    <div class="item-title">{{ truncateText(chat.prompt, 60) }}</div>
                    <div class="item-meta">
                      <el-tag size="small" type="info">{{ chat.model }}</el-tag>
                      <span class="item-time">{{ formatTime(chat.timestamp) }}</span>
                      <span class="item-cost">${{ chat.cost.toFixed(4) }}</span>
                      <span class="item-tokens">{{ chat.tokens }} tokens</span>
                    </div>
                  </div>
                  <el-icon class="expand-icon" :class="{ 'rotated': expandedItems.has(chat.id) }">
                    <ArrowDown />
                  </el-icon>
                </div>
                
                <!-- 展开的详细内容 -->
                <el-collapse-transition>
                  <div v-if="expandedItems.has(chat.id)" class="item-content">
                    <div class="content-section">
                      <div class="section-header">
                        <el-icon><User /></el-icon>
                        <span>问题</span>
                      </div>
                      <div class="section-content question-content">{{ chat.prompt }}</div>
                    </div>
                    
                    <div class="content-section">
                      <div class="section-header">
                        <el-icon><Robot /></el-icon>
                        <span>回答</span>
                      </div>
                      <div class="section-content answer-content" v-html="formatResponse(chat.response)"></div>
                    </div>
                  </div>
                </el-collapse-transition>
              </div>
            </div>
          </div>
        </el-card>
        </div>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup>
import { ref, computed, nextTick, defineProps, defineEmits } from 'vue'

const props = defineProps({
  chatHistory: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['show-examples', 'clear-history'])

// Tab控制
const activeTab = ref('current')
const searchKeyword = ref('')
const expandedItems = ref(new Set())

// 最新的对话
const latestChat = computed(() => {
  return props.chatHistory.length > 0 ? props.chatHistory[props.chatHistory.length - 1] : null
})

// 历史对话（所有对话记录，按时间倒序）
const historicalChats = computed(() => {
  if (props.chatHistory.length === 0) return []
  return [...props.chatHistory].reverse() // 所有对话按时间倒序
})

// 过滤的历史记录（搜索功能）
const filteredHistoricalChats = computed(() => {
  if (!searchKeyword.value.trim()) {
    return historicalChats.value
  }
  
  const keyword = searchKeyword.value.toLowerCase()
  return historicalChats.value.filter(chat => 
    chat.prompt.toLowerCase().includes(keyword) ||
    chat.response.toLowerCase().includes(keyword) ||
    chat.model.toLowerCase().includes(keyword)
  )
})



// 切换列表项展开状态
const toggleItemExpansion = (itemId) => {
  if (expandedItems.value.has(itemId)) {
    expandedItems.value.delete(itemId)
  } else {
    expandedItems.value.add(itemId)
  }
}

// 清空历史记录
const clearHistory = () => {
  emit('clear-history')
  expandedItems.value.clear()
  activeTab.value = 'current'
}

const handleShowExamples = () => {
  emit('show-examples')
}

// 截断文本
const truncateText = (text, maxLength) => {
  if (!text) return ''
  if (text.length <= maxLength) return text
  return text.substring(0, maxLength) + '...'
}

const formatTime = (timestamp) => {
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
/* 主容器 */
.chat-history-container {
  display: flex;
  flex-direction: column;
  height: 100%;
  min-height: 700px; /* 与左侧保持一致 */
  overflow: hidden;
}

/* Tab容器 */
.chat-tabs {
  height: 100%;
  min-height: 700px; /* 确保最小高度与左侧一致 */
  display: flex;
  flex-direction: column;
}

.chat-tabs :deep(.el-tabs__content) {
  flex: 1;
  overflow: hidden;
  padding: 0;
  min-height: 650px; /* 减去Tab头部高度后的最小高度 */
}

.chat-tabs :deep(.el-tab-pane) {
  height: 100%;
  min-height: 650px; /* 确保Tab面板有足够高度 */
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

/* Tab标签样式 */
.tab-label {
  display: flex;
  align-items: center;
  gap: 6px;
}

.tab-badge {
  margin-left: 4px;
}

/* Tab面板 */
.tab-pane {
  height: 100%;
  overflow: hidden;
}

/* 当前对话区域 */
.current-chat {
  height: 100%;
  min-height: 650px; /* 确保有足够高度 */
  display: flex;
  flex-direction: column;
}

.current-chat-card {
  border: 2px solid #67c23a;
  background: linear-gradient(135deg, #f0f9ff 0%, #f6ffed 100%);
  box-shadow: 0 4px 16px rgba(103, 194, 58, 0.2);
  height: 100%;
  display: flex;
  flex-direction: column;
}

/* 占位符对话卡片 */
.placeholder-chat {
  height: 100%; /* 占满Tab面板的全部高度 */
  min-height: 650px; /* 确保最小高度与左侧一致 */
  border: 2px dashed #d9d9d9;
  background: linear-gradient(135deg, #fafafa 0%, #f5f5f5 100%);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
}

.placeholder-chat :deep(.el-card__body) {
  flex: 1; /* 占用卡片的剩余空间 */
  min-height: 600px; /* 确保内容区域有足够高度 */
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.placeholder-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.placeholder-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: bold;
  color: #909399;
}

.placeholder-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0;
  padding: 0;
  height: 100%;
  min-height: 600px;
}

/* 问题和回答区域的高度分配 */
.placeholder-content .content-section {
  flex: 1;
  display: flex;
  flex-direction: column;
  border-bottom: 1px solid #ebeef5;
}

.placeholder-content .content-section:last-child {
  border-bottom: none;
}

.placeholder-content .content-section .section-header {
  flex-shrink: 0;
  padding: 12px 16px;
  background: #f8f9fa;
  border-bottom: 1px solid #ebeef5;
}

.placeholder-content .content-section .section-content {
  flex: 1;
  margin: 0;
}

.placeholder-text {
  background: #f8f9fa !important;
  border: none !important;
  color: #909399 !important;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0;
}

.placeholder-message {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  text-align: center;
}

.placeholder-icon {
  font-size: 24px;
  color: #c0c4cc;
}

.placeholder-message span {
  font-size: 14px;
  line-height: 1.5;
  max-width: 300px;
}

/* 问题内容样式 - 较小的高度，适合简短问题 */
.question-content {
  background: #f0f9ff !important;
  border: 1px solid #d4edda !important;
  color: #303133 !important;
  min-height: 80px; /* 较小的最小高度 */
  max-height: 200px; /* 限制最大高度 */
  height: auto; /* 自适应高度 */
  padding: 12px 16px; /* 较小的内边距 */
  line-height: 1.5;
  word-break: break-word;
  overflow-y: auto;
  overflow-x: hidden;
  box-sizing: border-box;
  white-space: pre-wrap;
  font-size: 14px;
  border-radius: 6px;
}

/* 回答内容样式 - 较大的高度，适合长回答 */
.answer-content {
  background: #f6ffed !important;
  border: 1px solid #b3d8ff !important;
  color: #303133 !important;
  min-height: 150px; /* 较大的最小高度 */
  height: 100%; /* 充分利用分配的空间 */
  padding: 16px; /* 较大的内边距 */
  line-height: 1.6;
  word-break: break-word;
  overflow-y: auto;
  overflow-x: hidden;
  box-sizing: border-box;
  white-space: pre-wrap;
  font-size: 14px;
  border-radius: 6px;
}

/* 问题内容滚动条样式 */
.question-content::-webkit-scrollbar {
  width: 4px; /* 较细的滚动条 */
}

.question-content::-webkit-scrollbar-track {
  background: #e6f7ff;
  border-radius: 2px;
}

.question-content::-webkit-scrollbar-thumb {
  background: #91d5ff;
  border-radius: 2px;
}

.question-content::-webkit-scrollbar-thumb:hover {
  background: #69c0ff;
}

/* 回答内容滚动条样式 */
.answer-content::-webkit-scrollbar {
  width: 6px; /* 较粗的滚动条 */
}

.answer-content::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.answer-content::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.answer-content::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

/* 当前对话的元数据样式 */
.current-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 12px;
}

.chat-time {
  color: #909399;
}

.chat-cost {
  color: #f56c6c;
  font-weight: 500;
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
  color: #303133;
}

.header-icon {
  font-size: 18px;
  color: #67c23a;
}

.current-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 12px;
}

.chat-time {
  color: #909399;
}

.chat-cost {
  color: #f56c6c;
  font-weight: 500;
}

.current-content {
  padding: 0;
}



/* 历史记录面板 */
.history-panel {
  height: 100%;
  overflow: hidden;
}

.history-card {
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.history-card :deep(.el-card__body) {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 20px;
  overflow: hidden;
  min-height: 0;
  height: calc(100% - 60px); /* 减去卡片头部高度 */
}

.history-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.history-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: bold;
  color: #303133;
}

.history-badge {
  margin-left: 8px;
}

.history-actions {
  display: flex;
  gap: 8px;
}

.clear-btn {
  padding: 4px 8px;
  font-size: 12px;
  color: #f56c6c;
}

.clear-btn:hover {
  color: #f56c6c;
  background: rgba(245, 108, 108, 0.1);
}

/* 搜索区域 */
.search-section {
  margin-bottom: 16px;
  flex-shrink: 0;
}

.search-input {
  width: 100%;
}

/* 历史记录列表 */
.history-list {
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.no-results {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

.history-items {
  flex: 1;
  overflow-y: auto;
  padding-right: 8px;
}

/* 自定义滚动条 */
.history-items::-webkit-scrollbar {
  width: 6px;
}

.history-items::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.history-items::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.history-items::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

/* 历史记录项 */
.history-item {
  border: 1px solid #ebeef5;
  border-radius: 8px;
  margin-bottom: 12px;
  background: #fff;
  transition: all 0.3s ease;
  overflow: hidden;
}

.history-item:hover {
  border-color: #409eff;
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.1);
}

.history-item.expanded {
  border-color: #409eff;
  box-shadow: 0 2px 12px rgba(64, 158, 255, 0.15);
}

.item-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.item-header:hover {
  background: #f8f9fa;
}

.item-info {
  flex: 1;
  min-width: 0;
}

.item-title {
  font-weight: 500;
  color: #303133;
  margin-bottom: 8px;
  line-height: 1.4;
  word-break: break-word;
  font-size: 14px;
}

.item-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  flex-wrap: wrap;
}

.item-time {
  color: #909399;
}

.item-cost {
  color: #f56c6c;
  font-weight: 500;
}

.item-tokens {
  color: #67c23a;
  font-weight: 500;
}

.expand-icon {
  font-size: 16px;
  color: #909399;
  transition: transform 0.3s ease;
  margin-left: 12px;
  flex-shrink: 0;
}

.expand-icon.rotated {
  transform: rotate(180deg);
}

.item-content {
  border-top: 1px solid #f0f0f0;
  padding: 16px;
  background: #fafafa;
}

/* 内容区域 */
.content-section {
  margin-bottom: 16px;
}

.content-section:last-child {
  margin-bottom: 0;
}

.section-header {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 8px;
  font-weight: 500;
  color: #606266;
  font-size: 13px;
}

.section-content {
  line-height: 1.6;
  font-size: 14px;
  word-break: break-word;
  padding: 0;
  margin: 0;
  border-radius: 0;
}



/* 代码样式 */
:deep(.code-block) {
  background: #f5f5f5;
  padding: 10px;
  border-radius: 4px;
  overflow-x: auto;
  margin: 10px 0;
  font-family: 'Monaco', 'Consolas', monospace;
  font-size: 13px;
}

:deep(.inline-code) {
  background: #f5f5f5;
  padding: 2px 4px;
  border-radius: 3px;
  font-family: 'Monaco', 'Consolas', monospace;
  font-size: 13px;
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
  
  .item-meta {
    flex-direction: column;
    align-items: flex-start;
    gap: 4px;
  }
  
  .history-controls {
    flex-direction: column;
  }
  
  .history-toggle-btn,
  .examples-btn {
    width: 100%;
  }
}

/* 动画效果 */
@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.history-panel {
  animation: slideDown 0.3s ease-out;
}
</style>