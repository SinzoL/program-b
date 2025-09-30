<template>
  <el-card shadow="hover" class="chat-card">
    <template #header>
      <div class="card-header">
        <el-icon class="header-icon"><ChatDotRound /></el-icon>
        <span>对话历史</span>
        <el-badge :value="chatHistory.length" class="chat-badge" />
        <div class="header-actions">
          <el-button 
            v-if="chatHistory.length > 0"
            type="text" 
            size="small"
            @click="toggleViewMode"
            class="view-mode-btn"
          >
            <el-icon><List v-if="viewMode === 'detailed'" /><Document v-else /></el-icon>
            {{ viewMode === 'list' ? '详细视图' : '列表视图' }}
          </el-button>
          <el-button 
            v-if="chatHistory.length > 0"
            type="text" 
            size="small"
            @click="clearHistory"
            class="clear-btn"
          >
            <el-icon><Delete /></el-icon>
            清空
          </el-button>
        </div>
      </div>
    </template>
    
    <div class="chat-content" ref="chatContainer">
      <div v-if="chatHistory.length === 0" class="empty-chat">
        <el-empty description="暂无对话记录">
          <el-button type="primary" @click="handleShowExamples">查看示例问题</el-button>
        </el-empty>
      </div>
      
      <!-- 列表视图 -->
      <div v-else-if="viewMode === 'list'" class="history-list">
        <div class="list-header">
          <span class="list-title">对话记录 ({{ chatHistory.length }})</span>
          <el-input
            v-model="searchKeyword"
            placeholder="搜索对话..."
            size="small"
            class="search-input"
            clearable
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </div>
        
        <div class="history-items">
          <!-- 最新的对话 - 自动展开 -->
          <div 
            v-if="filteredHistory.length > 0" 
            :key="filteredHistory[0].id"
            class="history-item latest-item active"
          >
            <div class="latest-header">
              <div class="latest-badge">
                <el-icon><Star /></el-icon>
                <span>最新对话</span>
              </div>
              <div class="latest-meta">
                <el-tag size="small" type="success">{{ filteredHistory[0].model }}</el-tag>
                <span class="item-time">{{ formatTime(filteredHistory[0].timestamp) }}</span>
                <span class="item-cost">${{ filteredHistory[0].cost.toFixed(4) }}</span>
              </div>
            </div>
            
            <!-- 最新对话的完整内容 -->
            <div class="latest-content">
              <div class="content-section">
                <div class="section-header">
                  <el-icon><User /></el-icon>
                  <span>问题</span>
                </div>
                <div class="section-content user-content">{{ filteredHistory[0].prompt }}</div>
              </div>
              
              <div class="content-section">
                <div class="section-header">
                  <el-icon><Robot /></el-icon>
                  <span>回答 ({{ filteredHistory[0].tokens }} tokens)</span>
                </div>
                <div class="section-content ai-content" v-html="formatResponse(filteredHistory[0].response)"></div>
              </div>
            </div>
          </div>
          
          <!-- 历史记录分隔线 -->
          <div v-if="filteredHistory.length > 1" class="history-divider">
            <span>历史记录</span>
          </div>
          
          <!-- 其他历史记录 - 折叠显示 -->
          <div 
            v-for="(chat, index) in filteredHistory.slice(1)" 
            :key="chat.id"
            class="history-item"
            :class="{ 'active': expandedItems.has(chat.id) }"
            @click="toggleItemExpansion(chat.id)"
          >
            <div class="item-header">
              <div class="item-info">
                <div class="item-title">{{ truncateText(chat.prompt, 50) }}</div>
                <div class="item-meta">
                  <el-tag size="small" type="info">{{ chat.model }}</el-tag>
                  <span class="item-time">{{ formatTime(chat.timestamp) }}</span>
                  <span class="item-cost">${{ chat.cost.toFixed(4) }}</span>
                </div>
              </div>
              <el-icon class="expand-icon" :class="{ 'expanded': expandedItems.has(chat.id) }">
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
                  <div class="section-content user-content">{{ chat.prompt }}</div>
                </div>
                
                <div class="content-section">
                  <div class="section-header">
                    <el-icon><Robot /></el-icon>
                    <span>回答 ({{ chat.tokens }} tokens)</span>
                  </div>
                  <div class="section-content ai-content" v-html="formatResponse(chat.response)"></div>
                </div>
              </div>
            </el-collapse-transition>
          </div>
        </div>
      </div>
      
      <!-- 详细视图（原来的样式） -->
      <div v-else class="chat-messages">
        <div 
          v-for="chat in chatHistory" 
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

const emit = defineEmits(['show-examples', 'clear-history'])

// 视图模式：'list' 列表视图, 'detailed' 详细视图
const viewMode = ref('list')
const chatContainer = ref(null)
const searchKeyword = ref('')
const expandedItems = ref(new Set())

// 切换视图模式
const toggleViewMode = () => {
  viewMode.value = viewMode.value === 'list' ? 'detailed' : 'list'
  // 切换到详细视图时滚动到底部
  if (viewMode.value === 'detailed') {
    nextTick(() => {
      scrollToBottom()
    })
  }
}

// 切换列表项展开状态
const toggleItemExpansion = (itemId) => {
  if (expandedItems.value.has(itemId)) {
    expandedItems.value.delete(itemId)
  } else {
    expandedItems.value.add(itemId)
  }
}

// 过滤历史记录（搜索功能）
const filteredHistory = computed(() => {
  if (!searchKeyword.value.trim()) {
    return [...props.chatHistory].reverse() // 最新的在前面
  }
  
  const keyword = searchKeyword.value.toLowerCase()
  return [...props.chatHistory]
    .filter(chat => 
      chat.prompt.toLowerCase().includes(keyword) ||
      chat.response.toLowerCase().includes(keyword) ||
      chat.model.toLowerCase().includes(keyword)
    )
    .reverse()
})

// 清空历史记录
const clearHistory = () => {
  emit('clear-history')
  expandedItems.value.clear()
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

.header-actions {
  margin-left: auto;
  display: flex;
  gap: 8px;
}

.view-mode-btn, .clear-btn {
  padding: 4px 8px;
  font-size: 12px;
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

/* 列表视图样式 */
.history-list {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.list-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid #ebeef5;
}

.list-title {
  font-weight: bold;
  color: #303133;
  font-size: 14px;
}

.search-input {
  width: 200px;
}

.history-items {
  flex: 1;
  overflow-y: auto;
}

.history-item {
  border: 1px solid #ebeef5;
  border-radius: 8px;
  margin-bottom: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  background: #fff;
}

.history-item:hover {
  border-color: #409eff;
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.1);
}

.history-item.active {
  border-color: #409eff;
  box-shadow: 0 2px 12px rgba(64, 158, 255, 0.15);
}

/* 最新对话样式 */
.latest-item {
  border: 2px solid #67c23a !important;
  background: linear-gradient(135deg, #f0f9ff 0%, #f6ffed 100%);
  box-shadow: 0 4px 16px rgba(103, 194, 58, 0.2);
  margin-bottom: 16px;
}

.latest-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px;
  border-bottom: 1px solid #e1f3d8;
}

.latest-badge {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #67c23a;
  font-weight: bold;
  font-size: 14px;
}

.latest-badge .el-icon {
  font-size: 16px;
}

.latest-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
}

.latest-content {
  padding: 16px;
  background: rgba(255, 255, 255, 0.8);
}

/* 历史记录分隔线 */
.history-divider {
  display: flex;
  align-items: center;
  margin: 20px 0 16px 0;
  color: #909399;
  font-size: 13px;
  font-weight: 500;
}

.history-divider::before,
.history-divider::after {
  content: '';
  flex: 1;
  height: 1px;
  background: linear-gradient(to right, transparent, #e4e7ed, transparent);
}

.history-divider span {
  padding: 0 16px;
  background: #fff;
  border: 1px solid #e4e7ed;
  border-radius: 12px;
  color: #606266;
}

.item-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
}

.item-info {
  flex: 1;
  min-width: 0;
}

.item-title {
  font-weight: 500;
  color: #303133;
  margin-bottom: 6px;
  line-height: 1.4;
  word-break: break-word;
}

.item-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: #909399;
}

.item-time {
  color: #909399;
}

.item-cost {
  color: #f56c6c;
  font-weight: 500;
}

.expand-icon {
  font-size: 16px;
  color: #909399;
  transition: transform 0.3s ease;
  margin-left: 12px;
}

.expand-icon.expanded {
  transform: rotate(180deg);
}

.item-content {
  border-top: 1px solid #f0f0f0;
  padding: 16px;
  background: #fafafa;
}

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
  padding: 12px;
  border-radius: 6px;
  line-height: 1.6;
  font-size: 14px;
}

.user-content {
  background: #f0f9ff;
  border: 1px solid #d4edda;
  color: #303133;
}

.ai-content {
  background: #f6ffed;
  border: 1px solid #b3d8ff;
  color: #303133;
}

/* 详细视图样式（原来的样式） */
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
  .list-header {
    flex-direction: column;
    gap: 12px;
    align-items: stretch;
  }
  
  .search-input {
    width: 100%;
  }
  
  .item-meta {
    flex-wrap: wrap;
  }
  
  .header-actions {
    flex-direction: column;
    gap: 4px;
  }
}
</style>