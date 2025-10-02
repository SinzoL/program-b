<template>
  <div 
    class="history-item tech-item"
    :class="{ 'expanded': isExpanded }"
  >
    <div class="item-header" @click="toggleExpansion">
      <div class="item-info">
        <div class="item-title">{{ truncateText(chat.prompt, 60) }}</div>
        <div class="item-meta">
          <el-tag size="small" type="info" class="tech-tag">{{ chat.model }}</el-tag>
          <span class="item-time">{{ formatTime(chat.timestamp) }}</span>
          <span class="item-cost">${{ chat.cost.toFixed(4) }}</span>
          <span class="item-tokens">{{ chat.tokens }} tokens</span>
        </div>
      </div>
      <TechIcons 
        name="chip" 
        :size="16" 
        color="#00d4ff" 
        class="expand-icon" 
        :class="{ 'rotated': isExpanded }"
      />
    </div>
    
    <!-- 展开的详细内容 -->
    <el-collapse-transition>
      <div v-if="isExpanded" class="item-content">
        <div class="content-section">
          <div class="section-header">
            <TechIcons name="analytics" :size="14" color="#00d4ff" />
            <span>问题</span>
          </div>
          <div class="section-content question-content">{{ chat.prompt }}</div>
        </div>
        
        <div class="content-section">
          <div class="section-header">
            <TechIcons name="robot" :size="14" color="#00d4ff" />
            <span>回答</span>
          </div>
          <div class="section-content answer-content" v-html="formatResponse(chat.response)"></div>
        </div>
      </div>
    </el-collapse-transition>
  </div>
</template>

<script setup>
import TechIcons from '../icons/TechIcons.vue'

const props = defineProps({
  chat: {
    type: Object,
    required: true
  },
  isExpanded: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['toggle-expansion'])

const toggleExpansion = () => {
  emit('toggle-expansion', props.chat.id)
}

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
  if (!response || typeof response !== 'string') {
    return '暂无回复内容'
  }
  
  return response
    .replace(/```(\w+)?\n([\s\S]*?)```/g, '<pre class="code-block"><code>$2</code></pre>')
    .replace(/`([^`]+)`/g, '<code class="inline-code">$1</code>')
    .replace(/\n/g, '<br>')
}
</script>

<style scoped>
.history-item {
  border: 1px solid rgba(0, 212, 255, 0.3);
  border-radius: 8px;
  margin-bottom: 12px;
  background: linear-gradient(135deg, rgba(15, 15, 35, 0.05), rgba(0, 212, 255, 0.02));
  transition: all 0.3s ease;
  overflow: hidden;
  position: relative;
}

.history-item::before {
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

.history-item:hover {
  border-color: #00d4ff;
  box-shadow: 0 4px 16px rgba(0, 212, 255, 0.2);
  transform: translateY(-2px);
}

.history-item:hover::before {
  opacity: 1;
}

.history-item.expanded {
  border-color: #00ff88;
  box-shadow: 0 6px 20px rgba(0, 255, 136, 0.2);
  background: linear-gradient(135deg, rgba(0, 255, 136, 0.05), rgba(0, 212, 255, 0.02));
}

.item-header {
  display: flex;
  align-items: center;
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

.item-cost {
  color: #ff6b6b;
  font-weight: 500;
  text-shadow: 0 0 4px rgba(255, 107, 107, 0.5);
}

.item-tokens {
  color: #00ff88;
  font-weight: 500;
  text-shadow: 0 0 4px rgba(0, 255, 136, 0.5);
}

.expand-icon {
  transition: transform 0.3s ease;
  margin-left: 12px;
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
  color: #00d4ff;
  font-size: 13px;
}

.section-content {
  line-height: 1.6;
  font-size: 14px;
  word-break: break-word;
  padding: 12px;
  border-radius: 6px;
  background: linear-gradient(135deg, rgba(0, 212, 255, 0.05), rgba(0, 255, 136, 0.02));
  border: 1px solid rgba(0, 212, 255, 0.2);
}

.question-content {
  max-height: 200px;
  overflow-y: auto;
}

.answer-content {
  max-height: 300px;
  overflow-y: auto;
}

/* 滚动条样式 */
.question-content::-webkit-scrollbar,
.answer-content::-webkit-scrollbar {
  width: 4px;
}

.question-content::-webkit-scrollbar-track,
.answer-content::-webkit-scrollbar-track {
  background: rgba(0, 212, 255, 0.1);
  border-radius: 2px;
}

.question-content::-webkit-scrollbar-thumb,
.answer-content::-webkit-scrollbar-thumb {
  background: rgba(0, 212, 255, 0.5);
  border-radius: 2px;
}

/* 代码样式 */
:deep(.code-block) {
  background: linear-gradient(135deg, rgba(15, 15, 35, 0.1), rgba(0, 212, 255, 0.05));
  border: 1px solid rgba(0, 212, 255, 0.2);
  padding: 8px;
  border-radius: 4px;
  overflow-x: auto;
  margin: 8px 0;
  font-family: 'Monaco', 'Consolas', monospace;
  font-size: 12px;
}

:deep(.inline-code) {
  background: rgba(0, 212, 255, 0.1);
  color: #00d4ff;
  padding: 2px 4px;
  border-radius: 3px;
  font-family: 'Monaco', 'Consolas', monospace;
  font-size: 12px;
  border: 1px solid rgba(0, 212, 255, 0.2);
}
</style>