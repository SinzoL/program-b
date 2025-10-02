<template>
  <el-card shadow="hover" class="tech-card">
    <template #header>
      <div class="card-header">
        <TechIcons name="brain" :size="20" color="#00d4ff" />
        <span>智能提问</span>
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
        P2L智能分析
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
    </div>
  </el-card>
</template>

<script setup>
import { defineProps, defineEmits } from 'vue'
import TechIcons from './icons/TechIcons.vue'

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

const emit = defineEmits(['update:prompt', 'update:selectedMode', 'analyze', 'clear', 'show-examples'])

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
  gap: 8px;
  font-weight: bold;
  color: #00d4ff;
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
  opacity: 1;
  animation-duration: 2s;
}

.tech-input-wrapper:focus-within::before {
  opacity: 1;
  animation-duration: 1.5s;
  box-shadow: 0 0 20px rgba(0, 212, 255, 0.5);
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

.tech-input :deep(.el-textarea .el-textarea__inner) {
  position: relative;
  z-index: 1;
  background: rgba(255, 255, 255, 0.8) !important;
}

.tech-input :deep(.el-textarea__inner) {
  background: 
    linear-gradient(135deg, rgba(15, 15, 35, 0.05), rgba(0, 212, 255, 0.02)),
    linear-gradient(45deg, 
      rgba(0, 212, 255, 0.04) 0%, 
      rgba(0, 255, 136, 0.03) 25%, 
      rgba(0, 212, 255, 0.02) 50%, 
      rgba(0, 255, 136, 0.03) 75%, 
      rgba(0, 212, 255, 0.04) 100%
    ) !important;
  background-size: 100% 100%, 300% 300% !important;
  background-position: 0 0, 0% 0% !important;
  border: none !important;
  border-radius: 6px;
  color: #e8e8e8 !important;
  font-size: 14px;
  line-height: 1.6;
  padding: 12px 16px;
  transition: color 0.3s ease, box-shadow 0.3s ease;
  box-shadow: inset 0 2px 8px rgba(0, 0, 0, 0.05);
  animation: backgroundFlow 6s ease-in-out infinite !important;
  position: relative;
  overflow: hidden;
}



.tech-input :deep(.el-textarea__inner):hover {
  background: 
    linear-gradient(135deg, rgba(15, 15, 35, 0.05), rgba(0, 212, 255, 0.02)),
    linear-gradient(45deg, 
      rgba(0, 212, 255, 0.06) 0%, 
      rgba(0, 255, 136, 0.04) 25%, 
      rgba(0, 212, 255, 0.03) 50%, 
      rgba(0, 255, 136, 0.04) 75%, 
      rgba(0, 212, 255, 0.06) 100%
    );
  background-size: 100% 100%, 300% 300%;
  animation-duration: 4s;
}

.tech-input :deep(.el-textarea__inner):focus {
  background: 
    linear-gradient(135deg, rgba(0, 212, 255, 0.08), rgba(0, 255, 136, 0.03)),
    linear-gradient(45deg, 
      rgba(0, 212, 255, 0.08) 0%, 
      rgba(0, 255, 136, 0.05) 25%, 
      rgba(0, 212, 255, 0.04) 50%, 
      rgba(0, 255, 136, 0.05) 75%, 
      rgba(0, 212, 255, 0.08) 100%
    );
  background-size: 100% 100%, 300% 300%;
  color:rgb(221, 221, 221) !important;
  box-shadow: 
    inset 0 2px 12px rgba(0, 212, 255, 0.1),
    inset 0 0 0 1px rgba(0, 212, 255, 0.2);
  animation-duration: 3s;
}

@keyframes backgroundFlow {
  0%, 100% { 
    background-position: 0 0, 0% 0%; 
  }
  25% { 
    background-position: 0 0, 100% 25%; 
  }
  50% { 
    background-position: 0 0, 50% 100%; 
  }
  75% { 
    background-position: 0 0, 0% 75%; 
  }
}

.tech-input :deep(.el-textarea__inner)::placeholder {
  color: rgba(0, 0, 0, 0.6);
  font-style: italic;
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
</style>