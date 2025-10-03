<template>
  <el-card class="current-chat-card tech-card" shadow="hover">
    <template #header>
      <div class="current-header">
        <div class="current-title">
          <TechIcons name="brain" :size="20" color="#00ff88" />
          <span>当前对话</span>
          <el-tag size="small" type="success" class="tech-tag">{{ chat.model }}</el-tag>
        </div>
        <div class="current-meta">
          <span class="chat-time">{{ formatTime(chat.timestamp) }}</span>
          <span class="chat-cost">${{ chat.cost.toFixed(4) }}</span>
        </div>
      </div>
    </template>
    
    <div class="current-content">
      <!-- 问题区域 -->
      <div class="content-section">
        <div class="section-header">
          <TechIcons name="analytics" :size="16" color="#00ff88" />
          <span>问题</span>
        </div>
        <div class="section-content question-content">
          {{ chat.prompt }}
        </div>
      </div>
      
      <!-- 回答区域 -->
      <div class="content-section">
        <div class="section-header">
          <TechIcons name="robot" :size="16" color="#00ff88" />
          <span>回答 ({{ chat.tokens }} tokens)</span>
        </div>
        <div class="section-content answer-content" v-html="formatResponse(chat.response)"></div>
      </div>
    </div>
  </el-card>
</template>

<script setup>
import TechIcons from '../icons/TechIcons.vue'

const props = defineProps({
  chat: {
    type: Object,
    required: true
  }
})

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

.current-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 12px;
}

.chat-time {
  color: #00d4ff;
  font-weight: 500;
}

.chat-cost {
  color: #ff6b6b;
  font-weight: 500;
  text-shadow: 0 0 4px rgba(255, 107, 107, 0.5);
}

.current-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0;
  padding: 0;
  height: 100%;
  min-height: 600px;
}

.content-section {
  display: flex;
  flex-direction: column;
  border-bottom: 1px solid rgba(0, 255, 136, 0.2);
}

.content-section:first-child {
  flex: 0 0 auto;
  min-height: 120px;
}

.content-section:last-child {
  flex: 1;
  border-bottom: none;
}

.section-header {
  flex-shrink: 0;
  padding: 12px 16px;
  background: linear-gradient(135deg, rgba(0, 255, 136, 0.1), rgba(0, 255, 136, 0.05));
  border-bottom: 1px solid rgba(0, 255, 136, 0.2);
  display: flex;
  align-items: center;
  gap: 8px;
  color: #00ff88;
  font-weight: 500;
}

.section-content {
  flex: 1;
  margin: 0;
}

.question-content {
  background: linear-gradient(135deg, rgba(0, 255, 136, 0.05), rgba(0, 212, 255, 0.05));
  border: 1px solid rgba(0, 255, 136, 0.3);
  color: #303133;
  min-height: 100px;
  max-height: 300px;
  height: auto;
  padding: 16px;
  line-height: 1.6;
  word-break: break-word;
  overflow-y: auto;
  overflow-x: hidden;
  box-sizing: border-box;
  white-space: pre-wrap;
  font-size: 14px;
  border-radius: 6px;
  flex: 1;
}

.answer-content {
  background: linear-gradient(135deg, rgba(0, 212, 255, 0.05), rgba(0, 255, 136, 0.05));
  border: 1px solid rgba(0, 212, 255, 0.3);
  color: #303133;
  height: 300px;
  max-height: 1000px;
  min-height: 1000px;
  padding: 16px;
  line-height: 1.6;
  word-break: break-word;
  overflow-y: auto;
  overflow-x: hidden;
  box-sizing: border-box;
  white-space: pre-wrap;
  font-size: 14px;
  border-radius: 6px;
  flex-shrink: 0;
}

/* 滚动条样式 */
.question-content::-webkit-scrollbar,
.answer-content::-webkit-scrollbar {
  width: 6px;
}

.question-content::-webkit-scrollbar-track,
.answer-content::-webkit-scrollbar-track {
  background: rgba(0, 212, 255, 0.1);
  border-radius: 3px;
}

.question-content::-webkit-scrollbar-thumb,
.answer-content::-webkit-scrollbar-thumb {
  background: rgba(0, 212, 255, 0.5);
  border-radius: 3px;
}

.question-content::-webkit-scrollbar-thumb:hover,
.answer-content::-webkit-scrollbar-thumb:hover {
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
</style>