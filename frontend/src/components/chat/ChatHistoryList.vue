<template>
  <div class="history-panel">
    <el-card shadow="hover" class="history-card tech-card">
      <template #header>
        <div class="history-header">
          <div class="history-title">
            <TechIcons name="database" :size="20" color="#00d4ff" />
            <span>对话窗口管理</span>
            <el-badge :value="conversations.length" class="history-badge tech-badge" />
          </div>
          <div class="history-actions">
            <el-button 
              type="text" 
              size="small"
              @click="clearAllConversations"
              class="clear-btn tech-btn"
              :disabled="conversations.length === 0"
            >
              <TechIcons name="settings" :size="14" color="#ff6b6b" />
              清空全部
            </el-button>
          </div>
        </div>
      </template>
      
      <!-- 搜索框 -->
      <div class="search-section">
        <el-input
          v-model="searchKeyword"
          placeholder="搜索对话窗口..."
          size="default"
          class="search-input tech-input"
          clearable
        >
          <template #prefix>
            <TechIcons name="analytics" :size="16" color="#00d4ff" />
          </template>
        </el-input>
      </div>
      
      <!-- 对话窗口列表 -->
      <div class="conversations-list">
        <div v-if="filteredConversations.length === 0" class="no-results">
          <div class="empty-state">
            <div class="empty-icon-container">
              <CubeLogo :size="48" color="#4A90E2" variant="default" :animate="true" class="empty-icon" />
              <div class="empty-glow"></div>
            </div>
            <h3 class="empty-title">
              {{ searchKeyword ? '未找到匹配的对话' : '暂无对话窗口' }}
            </h3>
            <p class="empty-description">
              {{ searchKeyword 
                ? '尝试调整搜索关键词或清空搜索条件' 
                : '点击"新建对话"按钮开始您的第一次智能对话' 
              }}
            </p>
            <div class="empty-actions" v-if="searchKeyword">
              <el-button 
                type="primary" 
                size="small" 
                @click="searchKeyword = ''"
                class="tech-button"
              >
                <TechIcons name="analytics" :size="14" />
                清空搜索
              </el-button>
            </div>
          </div>
        </div>
        
        <div v-else class="conversations-items">
          <ChatHistoryItem
            v-for="conversation in filteredConversations"
            :key="conversation.id"
            :conversation="conversation"
            :is-expanded="expandedItems.has(conversation.id)"
            :is-current-conversation="conversation.id === currentConversationId"
            @toggle-expansion="toggleItemExpansion"
            @switch-conversation="switchConversation"
            @delete-conversation="deleteConversation"
          />
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { ElMessageBox, ElNotification } from 'element-plus'
import TechIcons from '../icons/TechIcons.vue'
import ChatHistoryItem from './ChatHistoryItem.vue'
import CubeLogo from '../icons/CubeLogo.vue'

const props = defineProps({
  conversations: {
    type: Array,
    default: () => []
  },
  currentConversationId: {
    type: String,
    default: null
  }
})

const emit = defineEmits(['switch-conversation', 'delete-conversation', 'clear-all-conversations'])

const searchKeyword = ref('')
const expandedItems = ref(new Set())

// 按更新时间排序的对话列表
const sortedConversations = computed(() => {
  return [...props.conversations].sort((a, b) => {
    const timeA = new Date(a.updatedAt || a.createdAt)
    const timeB = new Date(b.updatedAt || b.createdAt)
    return timeB - timeA // 最新的在前
  })
})

// 过滤的对话列表（搜索功能）
const filteredConversations = computed(() => {
  if (!searchKeyword.value.trim()) {
    return sortedConversations.value
  }
  
  const keyword = searchKeyword.value.toLowerCase()
  return sortedConversations.value.filter(conversation => {
    // 搜索对话标题
    if (conversation.title && conversation.title.toLowerCase().includes(keyword)) {
      return true
    }
    
    // 搜索消息内容
    return conversation.messages.some(message => 
      message.content.toLowerCase().includes(keyword) ||
      (message.model && message.model.toLowerCase().includes(keyword))
    )
  })
})

// 切换列表项展开状态
const toggleItemExpansion = (conversationId) => {
  if (expandedItems.value.has(conversationId)) {
    expandedItems.value.delete(conversationId)
  } else {
    expandedItems.value.add(conversationId)
  }
}

// 切换对话
const switchConversation = (conversationId) => {
  emit('switch-conversation', conversationId)
  // 展开当前对话的详情
  expandedItems.value.add(conversationId)
}

// 删除对话
const deleteConversation = async (conversationId) => {
  try {
    const conversation = props.conversations.find(conv => conv.id === conversationId)
    const conversationTitle = conversation?.title || '未命名对话'
    
    await ElMessageBox.confirm(
      `删除对话"${conversationTitle}", 此操作不可恢复。`,
      '删除对话',
      {
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
        type: 'warning',
        confirmButtonClass: 'el-button--danger',
        customClass: 'tech-message-box',
        showClose: false,
        center: true
      }
    )
    
    emit('delete-conversation', conversationId)
    expandedItems.value.delete(conversationId)
    
    ElNotification({
      title: '操作成功',
      message: '对话已删除',
      type: 'success',
      customClass: 'tech-notification',
      duration: 3000
    })
  } catch (error) {
    // 用户取消删除
    if (error === 'cancel') {
      return
    }
    console.error('删除对话失败:', error)
    ElNotification({
      title: '操作失败',
      message: '删除对话失败，请重试',
      type: 'error',
      customClass: 'tech-notification',
      duration: 4000
    })
  }
}

// 清空所有对话
const clearAllConversations = async () => {
  try {
    await ElMessageBox.confirm(
      `将删除 ${props.conversations.length} 个对话窗口, 此操作不可恢复`,
      '清空所有对话',
      {
        confirmButtonText: '确定清空',
        cancelButtonText: '取消',
        type: 'warning',
        confirmButtonClass: 'el-button--danger',
        customClass: 'tech-message-box',
        showClose: false,
        center: true
      }
    )
    
    emit('clear-all-conversations')
    expandedItems.value.clear()
    searchKeyword.value = ''
    
    ElNotification({
      title: '操作成功',
      message: '所有对话已清空',
      type: 'success',
      customClass: 'tech-notification',
      duration: 3000
    })
  } catch (error) {
    // 用户取消清空
    if (error === 'cancel') {
      return
    }
    console.error('清空对话失败:', error)
    ElNotification({
      title: '操作失败',
      message: '清空对话失败，请重试',
      type: 'error',
      customClass: 'tech-notification',
      duration: 4000
    })
  }
}
</script>

<style scoped>
.history-panel {
  height: 100%;
  overflow: hidden;
}

.history-card {
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  border: 1px solid rgba(0, 212, 255, 0.3);
  background: linear-gradient(135deg, rgba(15, 15, 35, 0.05), rgba(0, 212, 255, 0.02));
  box-shadow: 0 4px 20px rgba(0, 212, 255, 0.1);
}

.history-card :deep(.el-card__body) {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 20px;
  overflow: hidden;
  min-height: 0;
  height: calc(100% - 60px);
  background: rgba(15, 15, 35, 0.02);
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
  color: #00d4ff;
}

.tech-badge :deep(.el-badge__content) {
  background: linear-gradient(135deg, #00d4ff, #0099cc);
  border: none;
  box-shadow: 0 2px 8px rgba(0, 212, 255, 0.3);
}

.history-actions {
  display: flex;
  gap: 8px;
}

.clear-btn {
  padding: 6px 12px;
  font-size: 12px;
  color: #ff6b6b;
  background: linear-gradient(135deg, rgba(255, 107, 107, 0.1), rgba(255, 107, 107, 0.05));
  border: 1px solid rgba(255, 107, 107, 0.3);
  border-radius: 6px;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 4px;
}

.clear-btn:hover:not(:disabled) {
  color: #ff6b6b;
  background: linear-gradient(135deg, rgba(255, 107, 107, 0.2), rgba(255, 107, 107, 0.1));
  box-shadow: 0 2px 8px rgba(255, 107, 107, 0.3);
  transform: translateY(-1px);
}

.clear-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.search-section {
  margin-bottom: 16px;
  flex-shrink: 0;
}

.tech-input :deep(.el-input__wrapper) {
  background: linear-gradient(135deg, rgba(0, 212, 255, 0.05), rgba(0, 255, 136, 0.02));
  border: 1px solid rgba(0, 212, 255, 0.3);
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 212, 255, 0.1);
  transition: all 0.3s ease;
}

.tech-input :deep(.el-input__wrapper:hover) {
  border-color: #00d4ff;
  box-shadow: 0 4px 12px rgba(0, 212, 255, 0.2);
}

.tech-input :deep(.el-input__wrapper.is-focus) {
  border-color: #00ff88;
  box-shadow: 0 0 0 2px rgba(0, 255, 136, 0.2);
}

.tech-input :deep(.el-input__inner) {
  color: #ffffff !important;
  background: transparent !important;
  border: none !important;
  font-weight: 500;
  text-shadow: 0 1px 3px rgba(0, 0, 0, 0.5);
}

.tech-input :deep(.el-input__inner::placeholder) {
  color: rgba(255, 255, 255, 0.6) !important;
  font-style: italic;
}

.conversations-list {
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
  padding: 40px 20px;
}

.empty-state {
  text-align: center;
  max-width: 320px;
  margin: 0 auto;
}

.empty-icon-container {
  position: relative;
  display: inline-block;
  margin-bottom: 24px;
}

.empty-icon {
  position: relative;
  z-index: 2;
  filter: drop-shadow(0 4px 12px rgba(74, 144, 226, 0.4));
}

.empty-glow {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 80px;
  height: 80px;
  background: radial-gradient(circle, rgba(74, 144, 226, 0.2) 0%, transparent 70%);
  border-radius: 50%;
  animation: empty-glow-pulse 3s ease-in-out infinite;
  z-index: 1;
}

@keyframes empty-glow-pulse {
  0%, 100% {
    transform: translate(-50%, -50%) scale(1);
    opacity: 0.6;
  }
  50% {
    transform: translate(-50%, -50%) scale(1.2);
    opacity: 0.3;
  }
}

.empty-title {
  font-size: 1.2rem;
  font-weight: 600;
  color: #4A90E2;
  margin: 0 0 12px 0;
  background: linear-gradient(45deg, #4A90E2, #00d4ff);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.empty-description {
  font-size: 0.9rem;
  color: #888;
  line-height: 1.5;
  margin: 0 0 24px 0;
}

.empty-actions {
  display: flex;
  justify-content: center;
  gap: 12px;
}

.tech-button {
  background: linear-gradient(135deg, #4A90E2, #00d4ff);
  border: none;
  border-radius: 20px;
  padding: 8px 16px;
  color: white;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(74, 144, 226, 0.3);
}

.tech-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(74, 144, 226, 0.4);
  background: linear-gradient(135deg, #5BA0F2, #10E4FF);
}

.tech-button:active {
  transform: translateY(0);
}

.conversations-items {
  flex: 1;
  overflow-y: auto;
  padding-right: 8px;
}

/* 自定义滚动条 */
.conversations-items::-webkit-scrollbar {
  width: 6px;
}

.conversations-items::-webkit-scrollbar-track {
  background: rgba(0, 212, 255, 0.1);
  border-radius: 3px;
}

.conversations-items::-webkit-scrollbar-thumb {
  background: rgba(0, 212, 255, 0.5);
  border-radius: 3px;
}

.conversations-items::-webkit-scrollbar-thumb:hover {
  background: rgba(0, 212, 255, 0.7);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .history-header {
    flex-direction: column;
    gap: 8px;
    align-items: flex-start;
  }
  
  .history-actions {
    align-self: flex-end;
  }
}
</style>

<style>
/* 全局样式 - 科技主题确认框 */
.tech-message-box {
  background: linear-gradient(135deg, rgba(15, 23, 42, 0.95), rgba(30, 41, 59, 0.92)) !important;
  backdrop-filter: blur(20px) !important;
  border: 2px solid rgba(0, 212, 255, 0.4) !important;
  border-radius: 12px !important;
  box-shadow: 
    0 8px 32px rgba(0, 0, 0, 0.3),
    0 0 0 1px rgba(0, 212, 255, 0.2),
    inset 0 1px 0 rgba(255, 255, 255, 0.1) !important;
}

.tech-message-box::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: linear-gradient(90deg, transparent, #00d4ff, transparent);
  animation: tech-scan 3s infinite;
}

@keyframes tech-scan {
  0% { transform: translateX(-100%); }
  100% { transform: translateX(100%); }
}

.tech-message-box .el-message-box__header {
  background: linear-gradient(135deg, rgba(0, 212, 255, 0.1), rgba(0, 255, 136, 0.05)) !important;
  border-bottom: 1px solid rgba(0, 212, 255, 0.3) !important;
  padding: 20px 24px 16px !important;
  border-radius: 12px 12px 0 0 !important;
}

.tech-message-box .el-message-box__title {
  color: #00d4ff !important;
  font-weight: 600 !important;
  font-size: 16px !important;
  text-shadow: 0 0 10px rgba(0, 212, 255, 0.5) !important;
}

.tech-message-box .el-message-box__content {
  padding: 20px 24px !important;
  background: rgba(15, 15, 35, 0.02) !important;
}

.tech-message-box .el-message-box__message {
  color: #e2e8f0 !important;
  font-size: 14px !important;
  line-height: 1.6 !important;
  text-shadow: 0 1px 3px rgba(0, 0, 0, 0.5) !important;
}

.tech-message-box .el-message-box__btns {
  padding: 16px 24px 20px !important;
  background: linear-gradient(135deg, rgba(0, 212, 255, 0.05), rgba(0, 255, 136, 0.02)) !important;
  border-top: 1px solid rgba(0, 212, 255, 0.2) !important;
  border-radius: 0 0 12px 12px !important;
  display: flex !important;
  gap: 12px !important;
  justify-content: center !important;
}

.tech-message-box .el-button {
  border-radius: 8px !important;
  padding: 10px 20px !important;
  font-weight: 500 !important;
  transition: all 0.3s ease !important;
  border: 1px solid transparent !important;
  position: relative !important;
  overflow: hidden !important;
}

.tech-message-box .el-button--default {
  background: linear-gradient(135deg, rgba(148, 163, 184, 0.1), rgba(148, 163, 184, 0.05)) !important;
  color: #94a3b8 !important;
  border-color: rgba(148, 163, 184, 0.3) !important;
}

.tech-message-box .el-button--default:hover {
  background: linear-gradient(135deg, rgba(148, 163, 184, 0.2), rgba(148, 163, 184, 0.1)) !important;
  color: #e2e8f0 !important;
  border-color: #94a3b8 !important;
  transform: translateY(-2px) !important;
  box-shadow: 0 4px 12px rgba(148, 163, 184, 0.3) !important;
}

.tech-message-box .el-button--danger {
  background: linear-gradient(135deg, #ff6b6b, #ff5252) !important;
  color: white !important;
  border: none !important;
  box-shadow: 0 4px 15px rgba(255, 107, 107, 0.4) !important;
}

.tech-message-box .el-button--danger:hover {
  background: linear-gradient(135deg, #ff5252, #ff4444) !important;
  transform: translateY(-2px) !important;
  box-shadow: 0 6px 20px rgba(255, 107, 107, 0.5) !important;
}

.tech-message-box .el-button::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  transition: left 0.5s ease;
}

.tech-message-box .el-button:hover::before {
  left: 100%;
}

/* 警告图标样式 */
.tech-message-box .el-message-box__status.el-icon {
  color: #fbbf24 !important;
  font-size: 24px !important;
  filter: drop-shadow(0 0 8px rgba(251, 191, 36, 0.6)) !important;
}
</style>