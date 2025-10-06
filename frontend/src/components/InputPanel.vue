<template>
  <el-card shadow="hover" class="tech-card">
    <template #header>
      <div class="card-header">
        <div class="header-left">
          <TechIcons name="brain" :size="20" color="#00d4ff" />
          <span>智能提问</span>
        </div>
        <div class="header-right">
          <div class="model-info" v-if="p2lModelInfo">
            <el-tooltip :content="getModelTooltip()" placement="top">
              <div class="model-badge">
                <TechIcons name="chip" :size="14" color="#10b981" />
                <span class="model-text">{{ p2lModelInfo.model_name }}</span>
                <span class="model-params" v-if="p2lModelInfo.parameters_display">
                  {{ p2lModelInfo.parameters_display }}
                </span>
              </div>
            </el-tooltip>
          </div>
        </div>
      </div>
    </template>
    
    <!-- 优先模式选择 -->
    <div class="priority-section">
      <label class="section-label">优先模式：</label>
      <el-radio-group :model-value="selectedMode" @change="handleModeChange" class="tech-radio-group">
        <el-radio-button label="performance" class="tech-radio-button">
          <TechIcons name="performance" :size="16" color="#00ff88" />
          性能优先
        </el-radio-button>
        <el-radio-button label="cost" class="tech-radio-button">
          <TechIcons name="cost" :size="16" color="#ffaa00" />
          成本优先
        </el-radio-button>
        <el-radio-button label="speed" class="tech-radio-button">
          <TechIcons name="speed" :size="16" color="#ff6b6b" />
          速度优先
        </el-radio-button>
        <el-radio-button label="balanced" class="tech-radio-button">
          <TechIcons name="balanced" :size="16" color="#00d4ff" />
          平衡模式
        </el-radio-button>
      </el-radio-group>
    </div>

    <!-- 问题输入 -->
    <div class="input-section">
      <div class="tech-input-wrapper">
        <el-input
          :model-value="prompt"
          @input="handlePromptChange"
          type="textarea"
          :rows="4"
          placeholder="请输入您的问题，例如：展示js实现字符串中下划线转化为驼峰"
          maxlength="1000"
          show-word-limit
          @keydown.ctrl.enter="handleAnalyze"
          class="tech-input"
        />
        <div class="input-border-effect"></div>
        <div class="input-scan-line"></div>
      </div>
    </div>

    <!-- 操作按钮 -->
    <div class="action-buttons">
      <el-button 
        type="primary" 
        size="large"
        @click="handleAnalyze"
        :loading="loading"
        :disabled="!prompt.trim() || !backendHealth"
        class="tech-button primary-button"
      >
        <TechIcons name="analytics" :size="18" color="#ffffff" />
        智能分析
      </el-button>
      <el-button 
        @click="handleClear"
        :disabled="loading"
        class="tech-button"
      >
        <TechIcons name="settings" :size="16" color="#909399" />
        清空输入
      </el-button>
      <el-button 
        @click="handleShowExamples"
        :disabled="loading"
        class="tech-button"
      >
        <TechIcons name="database" :size="16" color="#409eff" />
        示例问题
      </el-button>
      <el-button 
        @click="handleNewConversation"
        :disabled="loading"
        class="tech-button new-conversation-button"
      >
        <TechIcons name="brain" :size="16" color="#10b981" />
        新建对话
      </el-button>
    </div>
  </el-card>
</template>

<script setup>
import { defineProps, defineEmits, ref, onMounted } from 'vue'
import { ElNotification } from 'element-plus'
import TechIcons from './icons/TechIcons.vue'
import { p2lApi } from '@/utils/api'
import { conversationManager } from '@/utils/conversationManager'

defineProps({
  prompt: {
    type: String,
    default: ''
  },
  selectedMode: {
    type: String,
    default: 'balanced'
  },
  loading: {
    type: Boolean,
    default: false
  },
  backendHealth: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:prompt', 'update:selectedMode', 'analyze', 'clear', 'show-examples', 'new-conversation'])

// P2L模型信息
const p2lModelInfo = ref(null)

// 获取P2L模型信息 - 兼容Docker和本地开发环境
const fetchP2LModelInfo = async () => {
  try {
    const response = await p2lApi.getModelInfo()
    if (response.data.status === 'success') {
      p2lModelInfo.value = response.data.model_info
      console.log('✅ P2L模型信息获取成功:', response.data.model_info.model_name)
    }
  } catch (error) {
    console.warn('获取P2L模型信息失败:', error)
    // 设置默认信息 - 使用当前配置的默认模型
    p2lModelInfo.value = {
      model_name: 'P2L-135M-GRK',
      model_type: '未知',
      is_loaded: false
    }
    console.log('🔄 使用默认模型信息:', p2lModelInfo.value.model_name)
  }
}

// 生成模型提示信息
const getModelTooltip = () => {
  if (!p2lModelInfo.value) return ''
  
  const info = p2lModelInfo.value
  let tooltip = `P2L推理模型信息:\n`
  tooltip += `• 模型: ${info.model_name}\n`
  tooltip += `• 架构: ${info.architecture || info.model_type}\n`
  
  if (info.parameters_display) {
    tooltip += `• 参数量: ${info.parameters_display}\n`
  }
  
  if (info.hidden_size) {
    tooltip += `• 隐藏层: ${info.hidden_size}维\n`
  }
  
  if (info.num_layers) {
    tooltip += `• 层数: ${info.num_layers}层\n`
  }
  
  tooltip += `• 设备: ${info.device}\n`
  tooltip += `• 状态: ${info.is_loaded ? '已加载' : '未加载'}`
  
  return tooltip
}

// 组件挂载时获取模型信息
onMounted(() => {
  fetchP2LModelInfo()
})

const handlePromptChange = (value) => {
  emit('update:prompt', value)
}

const handleModeChange = (mode) => {
  emit('update:selectedMode', mode)
}

const handleAnalyze = () => {
  emit('analyze')
}

const handleClear = () => {
  emit('clear')
}

const handleShowExamples = () => {
  emit('show-examples')
}

const handleNewConversation = async () => {
  try {
    // 检查当前对话是否为空
    const currentConversation = conversationManager.getCurrentConversation()
    
    // 如果当前对话存在且为空（没有消息），则不创建新对话
    if (currentConversation && (!currentConversation.messages || currentConversation.messages.length === 0)) {
      console.log('🔄 当前对话为空，无需创建新对话')
      ElNotification({
        title: '对话状态',
        message: '当前对话为空，无需创建新对话',
        type: 'info',
        customClass: 'tech-notification',
        duration: 3000
      })
      return
    }
    
    // 创建新的临时对话（不保存到历史记录）
    const newConversation = await conversationManager.createNewConversation()
    console.log('✅ 创建临时对话:', newConversation.id, '(暂不保存到历史记录)')
    
    // 通知父组件切换到新对话
    emit('new-conversation', newConversation)
    
    // 清空当前输入
    emit('clear')
    
    ElNotification({
      title: '新对话',
      message: '已准备新对话，开始提问后将自动保存',
      type: 'success',
      customClass: 'tech-notification',
      duration: 3000
    })
  } catch (error) {
    console.error('❌ 创建新对话失败:', error)
    ElNotification({
      title: '操作失败',
      message: '创建新对话失败，请重试',
      type: 'error',
      customClass: 'tech-notification',
      duration: 4000
    })
  }
}
</script>

<style scoped>
.tech-card {
  border: 2px solid #00d4ff;
  background: linear-gradient(135deg, rgba(0, 212, 255, 0.05), rgba(0, 255, 136, 0.05));
  box-shadow: 0 4px 20px rgba(0, 212, 255, 0.2);
  position: relative;
  overflow: hidden;
}

.tech-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: linear-gradient(90deg, transparent, #00d4ff, transparent);
  animation: scan 3s infinite;
}

@keyframes scan {
  0% { transform: translateX(-100%); }
  100% { transform: translateX(100%); }
}

.tech-card :deep(.el-card__header) {
  background: linear-gradient(135deg, rgba(0, 212, 255, 0.1), rgba(0, 255, 136, 0.05));
  border-bottom: 1px solid rgba(0, 212, 255, 0.3);
}

.tech-card :deep(.el-card__body) {
  background: rgba(15, 15, 35, 0.02);
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-weight: bold;
  color: #00d4ff;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 8px;
}

.header-right {
  display: flex;
  align-items: center;
}

.model-info {
  margin-left: 16px;
}

.model-badge {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 4px 8px;
  background: linear-gradient(135deg, rgba(16, 185, 129, 0.1), rgba(16, 185, 129, 0.05));
  border: 1px solid rgba(16, 185, 129, 0.3);
  border-radius: 12px;
  font-size: 12px;
  color: #10b981;
  cursor: help;
  transition: all 0.3s ease;
}

.model-badge:hover {
  background: linear-gradient(135deg, rgba(16, 185, 129, 0.15), rgba(16, 185, 129, 0.08));
  border-color: #10b981;
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(16, 185, 129, 0.2);
}

.model-text {
  font-weight: 600;
  font-size: 11px;
}

.model-params {
  font-size: 10px;
  opacity: 0.8;
  background: rgba(16, 185, 129, 0.2);
  padding: 1px 4px;
  border-radius: 4px;
  margin-left: 2px;
}

.priority-section, .input-section {
  margin-bottom: 20px;
}

.section-label {
  display: block;
  margin-bottom: 10px;
  font-weight: bold;
  color: #00d4ff;
}

.tech-radio-group :deep(.el-radio-button) {
  margin-right: 8px;
  margin-bottom: 8px;
}

.tech-radio-button {
  display: flex;
  align-items: center;
  gap: 6px;
}

.tech-radio-group :deep(.el-radio-button__inner) {
  display: flex;
  align-items: center;
  gap: 6px;
  background: linear-gradient(135deg, rgba(0, 212, 255, 0.05), rgba(0, 255, 136, 0.02));
  border: 1px solid rgba(0, 212, 255, 0.3);
  transition: all 0.3s ease;
}

.tech-radio-group :deep(.el-radio-button__inner:hover) {
  background: linear-gradient(135deg, rgba(0, 212, 255, 0.1), rgba(0, 255, 136, 0.05));
  border-color: #00d4ff;
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(0, 212, 255, 0.2);
}

.tech-radio-group :deep(.el-radio-button.is-active .el-radio-button__inner) {
  background: linear-gradient(135deg, #00d4ff, #00ff88);
  border-color: #00d4ff;
  color: white;
  box-shadow: 0 4px 12px rgba(0, 212, 255, 0.3);
}

.action-buttons {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.tech-button {
  display: flex;
  align-items: center;
  gap: 6px;
  transition: all 0.3s ease;
  border: 1px solid rgba(0, 212, 255, 0.3);
  background: linear-gradient(135deg, rgba(0, 212, 255, 0.05), rgba(0, 255, 136, 0.02));
}

.tech-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0, 212, 255, 0.2);
  border-color: #00d4ff;
}

.primary-button {
  background: linear-gradient(135deg, #00d4ff, #00ff88);
  border: none;
  box-shadow: 0 4px 15px rgba(0, 212, 255, 0.3);
}

.primary-button:hover {
  background: linear-gradient(135deg, #00ff88, #00d4ff);
  box-shadow: 0 8px 25px rgba(0, 212, 255, 0.4);
}

.new-conversation-button {
  background: linear-gradient(135deg, rgba(16, 185, 129, 0.1), rgba(16, 185, 129, 0.05));
  border-color: rgba(16, 185, 129, 0.3);
  color: #10b981;
}

.new-conversation-button:hover {
  background: linear-gradient(135deg, rgba(16, 185, 129, 0.15), rgba(16, 185, 129, 0.08));
  border-color: #10b981;
  color: #10b981;
  box-shadow: 0 6px 20px rgba(16, 185, 129, 0.2);
}

/* 科技风格输入框 */
.tech-input-wrapper {
  position: relative;
  overflow: hidden;
  border-radius: 6px;
}

.tech-input-wrapper::before {
  content: '';
  position: absolute;
  top: -2px;
  left: -2px;
  right: -2px;
  bottom: -2px;
  background: linear-gradient(45deg, #00d4ff, #00ff88, #00d4ff, #ff6b6b);
  background-size: 400% 400%;
  border-radius: 8px;
  z-index: -1;
  animation: techBorderFlow 4s ease-in-out infinite;
  opacity: 0.6;
}

.tech-input-wrapper:hover::before {
  opacity: 0.8;
  animation-duration: 3s;
}

.tech-input-wrapper:focus-within::before {
  opacity: 1;
  animation-duration: 2s;
  box-shadow: 0 0 30px rgba(0, 212, 255, 0.6);
}

@keyframes techBorderFlow {
  0%, 100% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
}

.input-border-effect {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  border: 1px solid rgba(0, 212, 255, 0.3);
  border-radius: 6px;
  pointer-events: none;
  transition: all 0.3s ease;
}

.tech-input-wrapper:hover .input-border-effect {
  border-color: rgba(0, 212, 255, 0.6);
  box-shadow: 
    inset 0 0 10px rgba(0, 212, 255, 0.1),
    0 0 15px rgba(0, 212, 255, 0.2);
}

.tech-input-wrapper:focus-within .input-border-effect {
  border-color: #00d4ff;
  box-shadow: 
    inset 0 0 15px rgba(0, 212, 255, 0.15),
    0 0 25px rgba(0, 212, 255, 0.3);
}

.input-scan-line {
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 2px;
  background: linear-gradient(90deg, transparent, #00d4ff, transparent);
  pointer-events: none;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.tech-input-wrapper:focus-within .input-scan-line {
  opacity: 1;
  animation: inputScan 2s ease-in-out infinite;
}

@keyframes inputScan {
  0% { left: -100%; }
  50% { left: 100%; }
  100% { left: -100%; }
}

.tech-input :deep(.el-textarea) {
  position: relative;
  z-index: 1;
  background: transparent;
}

.tech-input :deep(.el-textarea__inner) {
  background: 
    linear-gradient(135deg, rgba(15, 23, 42, 0.95), rgba(30, 41, 59, 0.92)),
    linear-gradient(45deg, 
      rgba(0, 212, 255, 0.08) 0%, 
      rgba(15, 23, 42, 0.95) 20%, 
      rgba(15, 23, 42, 0.95) 80%, 
      rgba(0, 255, 136, 0.08) 100%
    ) !important;
  background-size: 100% 100%, 200% 200% !important;
  backdrop-filter: blur(15px);
  border: none !important;
  border-radius: 6px;
  color: #e2e8f0 !important;
  font-size: 14px;
  line-height: 1.6;
  padding: 12px 16px;
  height: 200px;
  transition: all 0.3s ease;
  box-shadow: 
    inset 0 2px 8px rgba(0, 212, 255, 0.1),
    inset 0 1px 0 rgba(255, 255, 255, 0.1),
    0 4px 12px rgba(0, 0, 0, 0.15);
  position: relative;
  overflow: hidden;
  font-weight: 500;
  text-shadow: 0 1px 3px rgba(0, 0, 0, 0.5);
  animation: subtleBackgroundFlow 8s ease-in-out infinite !important;
}

.tech-input :deep(.el-textarea__inner):hover {
  background: 
    linear-gradient(135deg, rgba(15, 23, 42, 0.97), rgba(30, 41, 59, 0.94)),
    linear-gradient(45deg, 
      rgba(0, 212, 255, 0.12) 0%, 
      rgba(15, 23, 42, 0.97) 20%, 
      rgba(15, 23, 42, 0.97) 80%, 
      rgba(0, 255, 136, 0.12) 100%
    ) !important;
  background-size: 100% 100%, 200% 200% !important;
  color: #f1f5f9 !important;
  box-shadow: 
    inset 0 2px 12px rgba(0, 212, 255, 0.15),
    inset 0 1px 0 rgba(255, 255, 255, 0.15),
    0 6px 20px rgba(0, 212, 255, 0.2);
  transform: translateY(-1px);
  animation-duration: 6s !important;
}

.tech-input :deep(.el-textarea__inner):focus {
  background: 
    linear-gradient(135deg, rgba(15, 23, 42, 0.98), rgba(30, 41, 59, 0.96)),
    linear-gradient(45deg, 
      rgba(0, 212, 255, 0.15) 0%, 
      rgba(15, 23, 42, 0.98) 25%, 
      rgba(15, 23, 42, 0.98) 75%, 
      rgba(0, 255, 136, 0.15) 100%
    ) !important;
  background-size: 100% 100%, 150% 150% !important;
  color: #ffffff !important;
  box-shadow: 
    inset 0 2px 15px rgba(0, 212, 255, 0.2),
    inset 0 0 0 2px rgba(0, 212, 255, 0.4),
    inset 0 1px 0 rgba(255, 255, 255, 0.2),
    0 8px 25px rgba(0, 212, 255, 0.3);
  transform: translateY(-2px);
  animation: focusBackgroundFlow 4s ease-in-out infinite !important;
}

.tech-input :deep(.el-textarea__inner)::placeholder {
  color: #94a3b8;
  opacity: 0.9;
  font-style: italic;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
}

.tech-input :deep(.el-input__count) {
  background: linear-gradient(135deg, rgba(0, 212, 255, 0.1), rgba(0, 255, 136, 0.05));
  color: #00d4ff;
  border: 1px solid rgba(0, 212, 255, 0.3);
  border-radius: 4px;
  padding: 2px 6px;
  font-size: 12px;
  font-weight: bold;
  backdrop-filter: blur(5px);
}

/* 输入框聚焦时的额外效果 */
.tech-input-wrapper:focus-within {
  transform: translateY(-1px);
}

.tech-input-wrapper:focus-within::after {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  width: 0;
  height: 0;
  background: radial-gradient(circle, rgba(0, 212, 255, 0.1) 0%, transparent 70%);
  border-radius: 50%;
  pointer-events: none;
  animation: focusPulse 0.6s ease-out;
  transform: translate(-50%, -50%);
}

@keyframes focusPulse {
  0% {
    width: 0;
    height: 0;
    opacity: 0.8;
  }
  100% {
    width: 200%;
    height: 200%;
    opacity: 0;
  }
}

@keyframes subtleBackgroundFlow {
  0%, 100% { 
    background-position: 0 0, 0% 0%; 
  }
  50% { 
    background-position: 0 0, 100% 100%; 
  }
}

@keyframes focusBackgroundFlow {
  0%, 100% { 
    background-position: 0 0, 0% 0%; 
  }
  25% { 
    background-position: 0 0, 50% 25%; 
  }
  75% { 
    background-position: 0 0, 50% 75%; 
  }
}

/* 用户偏好：减少动画 */
@media (prefers-reduced-motion: reduce) {
  .tech-input-wrapper::before,
  .input-scan-line,
  .tech-input :deep(.el-textarea__inner) {
    animation: none !important;
  }
}

/* 为有视觉障碍的用户提供高对比度选项 */
@media (prefers-contrast: high) {
  .tech-input :deep(.el-textarea__inner) {
    background: linear-gradient(135deg, #000000, #1a1a1a) !important;
    color: #ffffff !important;
    border: 2px solid #ffffff !important;
    text-shadow: none !important;
  }
  
  .tech-input :deep(.el-textarea__inner)::placeholder {
    color: #cccccc !important;
  }
}
</style>