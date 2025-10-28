<template>
  <div class="chat-history-container tech-container">
    <!-- Tab切换界面 -->
    <el-tabs v-model="activeTab" class="chat-tabs tech-tabs" type="border-card">
      <!-- 当前对话Tab -->
      <el-tab-pane label="当前对话" name="current" class="tab-pane">
        <template #label>
          <span class="tab-label">
            <TechIcons name="brain" :size="16" color="#00d4ff" />
            当前对话
            <el-badge v-if="currentConversation && currentConversation.messages.length > 0" 
                      :value="getUserQuestionCount(currentConversation)" 
                      class="tab-badge tech-badge" />
          </span>
        </template>
        
        <div class="current-chat">
          <!-- 空状态：显示占位符 -->
          <ChatPlaceholder v-if="!currentConversation || currentConversation.messages.length === 0" />
          
          <!-- 有对话记录时显示当前对话窗口 -->
          <ChatCurrentView v-else :conversation="currentConversation" />
        </div>
      </el-tab-pane>

      <!-- 对话窗口Tab -->
      <el-tab-pane name="conversations" class="tab-pane">
        <template #label>
          <span class="tab-label">
            <TechIcons name="database" :size="16" color="#00d4ff" />
            对话窗口
            <el-badge v-if="conversations.length > 0" :value="conversations.length" class="tab-badge tech-badge" />
          </span>
        </template>
        
        <ChatHistoryList 
          :conversations="conversations"
          :current-conversation-id="currentConversationId"
          @switch-conversation="switchConversation"
          @delete-conversation="deleteConversation"
          @clear-all-conversations="clearAllConversations"
        />
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup>
import { ref, computed, nextTick, onMounted } from 'vue'
import TechIcons from './icons/TechIcons.vue'
import ChatPlaceholder from './chat/ChatPlaceholder.vue'
import ChatCurrentView from './chat/ChatCurrentView.vue'
import ChatHistoryList from './chat/ChatHistoryList.vue'
import { conversationManager } from '@/utils/conversationManager'

const props = defineProps({
  // 保持向后兼容，但优先使用对话管理器
  chatHistory: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['show-examples', 'clear-history', 'conversation-switched'])

// Tab控制
const activeTab = ref('current')

// 对话状态
const conversations = ref([])
const currentConversationId = ref(null)

// 当前对话
const currentConversation = computed(() => {
  if (!currentConversationId.value) return null
  return conversations.value.find(conv => conv.id === currentConversationId.value)
})

// 计算用户问题数量
const getUserQuestionCount = (conversation) => {
  if (!conversation || !conversation.messages) return 0
  return conversation.messages.filter(msg => msg.role === 'user').length
}

// 初始化对话管理器
const initializeConversations = async () => {
  try {
    await conversationManager.initialize()
    
    // 加载所有对话（只加载已保存的对话）
    conversations.value = await conversationManager.getAllConversations()
    
    // 获取当前对话ID
    currentConversationId.value = conversationManager.getCurrentConversationId()
    
    // 如果没有当前对话，创建一个临时对话（不保存到历史记录）
    if (!currentConversationId.value) {
      const newConversation = await conversationManager.createNewConversation()
      currentConversationId.value = newConversation.id
      console.log('🆕 创建初始临时对话:', newConversation.id)
    }
    
    console.log('✅ 对话管理器初始化完成:', {
      conversationsCount: conversations.value.length,
      currentId: currentConversationId.value
    })
  } catch (error) {
    console.error('❌ 对话管理器初始化失败:', error)
  }
}

// 切换对话 - 改进版本，确保完整加载对话数据
const switchConversation = async (conversationId) => {
  try {
    // 切换到目标对话
    const conversation = await conversationManager.switchConversation(conversationId)
    currentConversationId.value = conversationId
    
    // 更新本地对话列表中的数据，确保显示最新信息
    const conversationIndex = conversations.value.findIndex(conv => conv.id === conversationId)
    if (conversationIndex >= 0 && conversation) {
      conversations.value[conversationIndex] = { ...conversation }
    }
    
    // 切换到当前对话标签页
    activeTab.value = 'current'
    
    console.log('✅ 切换到对话:', conversationId, '消息数量:', conversation?.messages?.length || 0)
    emit('conversation-switched', conversationId)
  } catch (error) {
    console.error('❌ 切换对话失败:', error)
  }
}

// 删除对话
const deleteConversation = async (conversationId) => {
  try {
    await conversationManager.deleteConversation(conversationId)
    
    // 更新本地状态
    conversations.value = conversations.value.filter(conv => conv.id !== conversationId)
    
    // 如果删除的是当前对话，切换到其他对话或创建新对话
    if (currentConversationId.value === conversationId) {
      if (conversations.value.length > 0) {
        await switchConversation(conversations.value[0].id)
      } else {
        const newConversation = await conversationManager.createConversation()
        conversations.value.push(newConversation)
        currentConversationId.value = newConversation.id
      }
    }
    
    console.log('✅ 删除对话:', conversationId)
  } catch (error) {
    console.error('❌ 删除对话失败:', error)
  }
}

// 清空所有对话
const clearAllConversations = async () => {
  try {
    await conversationManager.clearAllConversations()
    conversations.value = []
    
    // 创建新对话
    const newConversation = await conversationManager.createConversation()
    conversations.value.push(newConversation)
    currentConversationId.value = newConversation.id
    
    activeTab.value = 'current'
    console.log('✅ 清空所有对话')
    emit('clear-history')
  } catch (error) {
    console.error('❌ 清空对话失败:', error)
  }
}

// 添加新消息到当前对话 - 改进版本，支持临时对话转正式对话
const addMessageToCurrentConversation = async (message) => {
  try {
    if (!currentConversationId.value) {
      const newConversation = await conversationManager.createNewConversation()
      currentConversationId.value = newConversation.id
    }
    
    // 确保消息格式正确
    const formattedMessage = {
      ...message,
      role: message.role || message.type,
      type: message.type || message.role,
      timestamp: message.timestamp || new Date().toISOString(),
      tokens: message.tokens || 0,
      cost: message.cost || 0,
      responseTime: message.responseTime || 0
    }
    
    // 检查当前对话是否为临时对话
    const currentConversation = conversationManager.getCurrentConversation()
    const wasTemporary = currentConversation?._isTemporary
    
    await conversationManager.addMessage(currentConversationId.value, formattedMessage)
    
    // 如果对话从临时转为正式，更新本地对话列表
    if (wasTemporary) {
      const updatedConversation = await conversationManager.storage.getConversation(currentConversationId.value)
      if (updatedConversation) {
        // 添加到对话列表中
        const existingIndex = conversations.value.findIndex(conv => conv.id === currentConversationId.value)
        if (existingIndex >= 0) {
          conversations.value[existingIndex] = updatedConversation
        } else {
          conversations.value.unshift(updatedConversation)
        }
        console.log('📝 临时对话已转为正式对话并加入历史记录:', currentConversationId.value)
      }
    } else {
      // 更新现有对话
      const updatedConversation = await conversationManager.storage.getConversation(currentConversationId.value)
      if (updatedConversation) {
        const conversationIndex = conversations.value.findIndex(conv => conv.id === currentConversationId.value)
        if (conversationIndex >= 0) {
          conversations.value[conversationIndex] = updatedConversation
        }
      }
    }
    
    console.log('✅ 添加消息到对话:', currentConversationId.value, '消息内容:', formattedMessage.content.substring(0, 50))
  } catch (error) {
    console.error('❌ 添加消息失败:', error)
  }
}

// 处理新对话创建
const handleNewConversation = async (conversation) => {
  conversations.value.push(conversation)
  currentConversationId.value = conversation.id
  activeTab.value = 'current'
  
  console.log('✅ 新对话已创建:', conversation.id)
}

// 暴露滚动到底部的方法
const scrollToBottom = () => {
  nextTick(() => {
    console.log('Scroll to bottom called')
  })
}

// 组件挂载时初始化
onMounted(() => {
  initializeConversations()
})

// 暴露方法给父组件
defineExpose({
  scrollToBottom,
  addMessageToCurrentConversation,
  handleNewConversation,
  getCurrentConversationId: () => currentConversationId.value,
  getCurrentConversation: () => currentConversation.value
})
</script>

<style scoped>
/* 主容器 */
.chat-history-container {
  display: flex;
  flex-direction: column;
  height: 100%;
  min-height: 700px;
  overflow: hidden;
  background: #ffffff;
  border: 1px solid #d0d0d0;
  border-radius: 12px;
  position: relative;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

/* Tab容器 */
.chat-tabs {
  height: 100%;
  min-height: 700px;
  display: flex;
  flex-direction: column;
  background: transparent;
  border: none;
}

.tech-tabs :deep(.el-tabs__header) {
  background: #f8f9fa;
  border: 1px solid #e0e0e0;
  border-radius: 8px 8px 0 0;
  margin: 0;
}

.tech-tabs :deep(.el-tabs__nav-wrap) {
  background: transparent;
}

.tech-tabs :deep(.el-tabs__item) {
  color: #666;
  border: none;
  background: transparent;
  transition: all 0.3s ease;
}

.tech-tabs :deep(.el-tabs__item:hover) {
  color: #00d4ff;
}

.tech-tabs :deep(.el-tabs__item.is-active) {
  color: #00ff88;
  background: linear-gradient(135deg, rgba(0, 255, 136, 0.1), rgba(0, 212, 255, 0.05));
  border-bottom: 2px solid #00ff88;
}

.chat-tabs :deep(.el-tabs__content) {
  flex: 1;
  overflow: hidden;
  padding: 0;
  min-height: 650px;
  background: #ffffff;
  border: 1px solid #e0e0e0;
  border-top: none;
  border-radius: 0 0 8px 8px;
}

.chat-tabs :deep(.el-tab-pane) {
  height: 100%;
  min-height: 650px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

/* Tab标签样式 */
.tab-label {
  display: flex;
  align-items: center;
  gap: 6px;
  font-weight: 500;
}

.tech-badge :deep(.el-badge__content) {
  background: linear-gradient(135deg, #00d4ff, #0099cc);
  border: none;
  box-shadow: 0 2px 8px rgba(0, 212, 255, 0.3);
  color: white;
}

/* Tab面板 */
.tab-pane {
  height: 100%;
  overflow: hidden;
}

/* 当前对话区域 */
.current-chat {
  height: 100%;
  min-height: 650px;
  display: flex;
  flex-direction: column;
  padding: 16px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .chat-history-container {
    min-height: 600px;
  }
  
  .chat-tabs {
    min-height: 600px;
  }
  
  .chat-tabs :deep(.el-tabs__content) {
    min-height: 550px;
  }
  
  .chat-tabs :deep(.el-tab-pane) {
    min-height: 550px;
  }
  
  .current-chat {
    min-height: 550px;
    padding: 12px;
  }
}

/* 动画效果 */
@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.chat-history-container {
  animation: slideIn 0.3s ease-out;
}
</style>