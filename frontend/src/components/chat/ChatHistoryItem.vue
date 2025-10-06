<template>
  <div 
    class="conversation-item tech-item"
    :class="{ 
      'expanded': isExpanded,
      'current': isCurrentConversation
    }"
  >
    <div class="item-header" @click="toggleExpansion">
      <div class="item-info">
        <div class="item-title">{{ conversation.title || '新对话' }}</div>
        <div class="item-meta">
          <el-tag size="small" type="info" class="tech-tag">
            {{ getUserQuestionCount() }} 个问题
          </el-tag>
          <span class="item-time">{{ formatTime(conversation.updatedAt) }}</span>
          <span class="item-tokens">{{ getTotalTokens() }} tokens</span>
          <span class="item-cost">${{ getTotalCost().toFixed(4) }}</span>
        </div>
        <div class="conversation-preview">
          {{ getConversationPreview() }}
        </div>
      </div>
      <div class="item-actions">
        <el-button 
          v-if="!isCurrentConversation"
          type="text" 
          size="small"
          @click.stop="switchToConversation"
          class="action-btn switch-btn"
        >
          <TechIcons name="brain" :size="14" color="#00ff88" />
        </el-button>
        <el-button 
          type="text" 
          size="small"
          @click.stop="deleteConversation"
          class="action-btn delete-btn"
        >
          <TechIcons name="settings" :size="14" color="#ff6b6b" />
        </el-button>
        <TechIcons 
          name="chip" 
          :size="16" 
          color="#00d4ff" 
          class="expand-icon" 
          :class="{ 'rotated': isExpanded }"
        />
      </div>
    </div>
    
    <!-- 展开的详细内容 -->
    <el-collapse-transition>
      <div v-if="isExpanded" class="item-content">
        <div class="conversation-details">
          <div class="details-header">
            <span class="conversation-id">对话ID: {{ conversation.id.substring(0, 12) }}</span>
            <span class="created-time">创建于: {{ formatFullTime(conversation.createdAt) }}</span>
          </div>
          
          <!-- 消息列表预览 -->
          <div class="messages-preview">
            <div 
              v-for="(message, index) in getPreviewMessages()" 
              :key="message.id || index"
              class="message-preview"
              :class="{ 
                'user-preview': message.role === 'user' || message.type === 'user',
                'assistant-preview': message.role === 'assistant' || message.type === 'assistant'
              }"
            >
              <div class="preview-header">
                <TechIcons 
                  :name="(message.role === 'user' || message.type === 'user') ? 'analytics' : 'robot'" 
                  :size="12" 
                  :color="(message.role === 'user' || message.type === 'user') ? '#00d4ff' : '#00ff88'" 
                />
                <span class="preview-role">
                  {{ (message.role === 'user' || message.type === 'user') ? '用户' : (message.model || 'AI助手') }}
                </span>
                <span class="preview-time">{{ formatTime(message.timestamp) }}</span>
              </div>
              <div class="preview-content">
                {{ truncateText(message.content, 100) }}
              </div>
            </div>
            
            <div v-if="conversation.messages && conversation.messages.length > 4" class="more-messages">
              还有 {{ conversation.messages.length - 4 }} 条消息...
            </div>
          </div>
        </div>
      </div>
    </el-collapse-transition>
  </div>
</template>

<script setup>
import TechIcons from '../icons/TechIcons.vue'

const props = defineProps({
  conversation: {
    type: Object,
    required: true
  },
  isExpanded: {
    type: Boolean,
    default: false
  },
  isCurrentConversation: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['toggle-expansion', 'switch-conversation', 'delete-conversation'])

const toggleExpansion = () => {
  emit('toggle-expansion', props.conversation.id)
}

const switchToConversation = () => {
  emit('switch-conversation', props.conversation.id)
}

const deleteConversation = () => {
  emit('delete-conversation', props.conversation.id)
}

const truncateText = (text, maxLength) => {
  if (!text) return ''
  if (text.length <= maxLength) return text
  return text.substring(0, maxLength) + '...'
}

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
  
  return date.toLocaleDateString()
}

const formatFullTime = (timestamp) => {
  if (!timestamp) return ''
  const date = new Date(timestamp)
  return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})
}

const getTotalTokens = () => {
  if (!props.conversation.messages) return 0
  return props.conversation.messages.reduce((total, message) => {
    return total + (message.tokens || 0)
  }, 0)
}

const getTotalCost = () => {
  if (!props.conversation.messages) return 0
  return props.conversation.messages.reduce((total, message) => {
    return total + (message.cost || 0)
  }, 0)
}

const getUserQuestionCount = () => {
  if (!props.conversation || !props.conversation.messages) return 0
  return props.conversation.messages.filter(msg => 
    msg.role === 'user' || msg.type === 'user'
  ).length
}

const getConversationPreview = () => {
  if (!props.conversation.messages || props.conversation.messages.length === 0) {
    return '空对话'
  }
  
  // 查找第一条用户消息作为预览
  const firstUserMessage = props.conversation.messages.find(msg => 
    msg.role === 'user' || msg.type === 'user'
  )
  if (firstUserMessage) {
    return truncateText(firstUserMessage.content, 80)
  }
  
  // 如果没有用户消息，显示第一条消息
  const firstMessage = props.conversation.messages[0]
  return truncateText(firstMessage.content, 80)
}

const getPreviewMessages = () => {
  // 显示最多4条消息的预览，包含完整的对话流程
  if (!props.conversation.messages || props.conversation.messages.length === 0) {
    return []
  }
  
  // 显示前4条消息，确保用户能看到完整的问答对
  return props.conversation.messages.slice(0, 4)
}
</script>

<style scoped>
.conversation-item {
  border: 1px solid rgba(0, 212, 255, 0.3);
  border-radius: 8px;
  margin-bottom: 12px;
  background: linear-gradient(135deg, rgba(15, 15, 35, 0.05), rgba(0, 212, 255, 0.02));
  transition: all 0.3s ease;
  overflow: hidden;
  position: relative;
}

.conversation-item::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, #00d4ff, transparent);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.conversation-item:hover {
  border-color: #00d4ff;
  box-shadow: 0 4px 16px rgba(0, 212, 255, 0.2);
  transform: translateY(-2px);
}

.conversation-item:hover::before {
  opacity: 1;
}

.conversation-item.expanded {
  border-color: #00ff88;
  box-shadow: 0 6px 20px rgba(0, 255, 136, 0.2);
  background: linear-gradient(135deg, rgba(0, 255, 136, 0.05), rgba(0, 212, 255, 0.02));
}

.conversation-item.current {
  border-color: #00ff88;
  background: linear-gradient(135deg, rgba(0, 255, 136, 0.1), rgba(0, 212, 255, 0.05));
  box-shadow: 0 4px 16px rgba(0, 255, 136, 0.3);
}

.conversation-item.current::before {
  background: linear-gradient(90deg, transparent, #00ff88, transparent);
  opacity: 1;
}

.item-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  padding: 16px;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
}

.item-header:hover {
  background: linear-gradient(135deg, rgba(0, 212, 255, 0.05), rgba(0, 255, 136, 0.02));
}

.item-info {
  flex: 1;
  min-width: 0;
}

.item-title {
  font-weight: 600;
  color: #fff;
  margin-bottom: 8px;
  line-height: 1.4;
  word-break: break-word;
  font-size: 15px;
}

.item-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  flex-wrap: wrap;
  margin-bottom: 8px;
}

.tech-tag {
  background: linear-gradient(135deg, #00d4ff, #0099cc);
  color: white;
  border: none;
  box-shadow: 0 2px 6px rgba(0, 212, 255, 0.3);
}

.item-time {
  color: #00d4ff;
  font-weight: 500;
}

.item-tokens {
  color: #00ff88;
  font-weight: 500;
  text-shadow: 0 0 4px rgba(0, 255, 136, 0.5);
}

.item-cost {
  color: #ff6b6b;
  font-weight: 500;
  text-shadow: 0 0 4px rgba(255, 107, 107, 0.5);
}

.conversation-preview {
  color: #aaa;
  font-size: 13px;
  line-height: 1.4;
  font-style: italic;
}

.item-actions {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-left: 12px;
  flex-shrink: 0;
}

.action-btn {
  padding: 4px;
  border-radius: 4px;
  transition: all 0.3s ease;
  border: 1px solid transparent;
}

.switch-btn {
  background: linear-gradient(135deg, rgba(0, 255, 136, 0.1), rgba(0, 255, 136, 0.05));
  border-color: rgba(0, 255, 136, 0.3);
}

.switch-btn:hover {
  background: linear-gradient(135deg, rgba(0, 255, 136, 0.2), rgba(0, 255, 136, 0.1));
  border-color: #00ff88;
  box-shadow: 0 2px 8px rgba(0, 255, 136, 0.3);
}

.delete-btn {
  background: linear-gradient(135deg, rgba(255, 107, 107, 0.1), rgba(255, 107, 107, 0.05));
  border-color: rgba(255, 107, 107, 0.3);
}

.delete-btn:hover {
  background: linear-gradient(135deg, rgba(255, 107, 107, 0.2), rgba(255, 107, 107, 0.1));
  border-color: #ff6b6b;
  box-shadow: 0 2px 8px rgba(255, 107, 107, 0.3);
}

.expand-icon {
  transition: transform 0.3s ease;
  flex-shrink: 0;
}

.expand-icon.rotated {
  transform: rotate(180deg);
}

.item-content {
  border-top: 1px solid rgba(0, 212, 255, 0.2);
  padding: 16px;
  background: linear-gradient(135deg, rgba(15, 15, 35, 0.02), rgba(0, 212, 255, 0.01));
}

.conversation-details {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.details-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
  color: #888;
  font-family: 'Monaco', 'Consolas', monospace;
}

.messages-preview {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.message-preview {
  padding: 8px 12px;
  border-radius: 6px;
  border-left: 3px solid;
}

.user-preview {
  background: linear-gradient(135deg, rgba(0, 212, 255, 0.05), rgba(0, 212, 255, 0.02));
  border-left-color: #00d4ff;
}

.assistant-preview {
  background: linear-gradient(135deg, rgba(0, 255, 136, 0.05), rgba(0, 255, 136, 0.02));
  border-left-color: #00ff88;
}

.preview-header {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 4px;
  font-size: 11px;
}

.preview-role {
  font-weight: 500;
  color: #fff;
}

.preview-time {
  color: #888;
  margin-left: auto;
}

.preview-content {
  font-size: 12px;
  color: #ccc;
  line-height: 1.4;
}

.more-messages {
  text-align: center;
  color: #888;
  font-size: 12px;
  font-style: italic;
  padding: 8px;
  background: linear-gradient(135deg, rgba(0, 212, 255, 0.02), rgba(0, 255, 136, 0.02));
  border-radius: 4px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .item-header {
    flex-direction: column;
    gap: 12px;
    align-items: flex-start;
  }
  
  .item-actions {
    align-self: flex-end;
    margin-left: 0;
  }
  
  .details-header {
    flex-direction: column;
    gap: 4px;
    align-items: flex-start;
  }
}
</style>