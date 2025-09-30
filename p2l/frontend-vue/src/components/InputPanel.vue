<template>
  <el-card shadow="hover">
    <template #header>
      <div class="card-header">
        <el-icon class="header-icon"><EditPen /></el-icon>
        <span>智能提问</span>
      </div>
    </template>
    
    <!-- 优先模式选择 -->
    <div class="priority-section">
      <label class="section-label">优先模式：</label>
      <el-radio-group :model-value="selectedMode" @change="handleModeChange">
        <el-radio-button label="performance">🏆 性能优先</el-radio-button>
        <el-radio-button label="cost">💰 成本优先</el-radio-button>
        <el-radio-button label="speed">⚡ 速度优先</el-radio-button>
        <el-radio-button label="balanced">⚖️ 平衡模式</el-radio-button>
      </el-radio-group>
    </div>

    <!-- 问题输入 -->
    <div class="input-section">
      <el-input
        :model-value="prompt"
        @input="handlePromptChange"
        type="textarea"
        :rows="4"
        placeholder="请输入您的问题，例如：展示js实现字符串中下划线转化为驼峰"
        maxlength="1000"
        show-word-limit
        @keydown.ctrl.enter="handleAnalyze"
      />
    </div>

    <!-- 操作按钮 -->
    <div class="action-buttons">
      <el-button 
        type="primary" 
        size="large"
        @click="handleAnalyze"
        :loading="loading"
        :disabled="!prompt.trim() || !backendHealth"
      >
        <el-icon><MagicStick /></el-icon>
        P2L智能分析
      </el-button>
      <el-button 
        @click="handleClear"
        :disabled="loading"
      >
        <el-icon><Delete /></el-icon>
        清空结果
      </el-button>
      <el-button 
        @click="handleShowExamples"
        :disabled="loading"
      >
        <el-icon><QuestionFilled /></el-icon>
        示例问题
      </el-button>
    </div>
  </el-card>
</template>

<script setup>
import { defineProps, defineEmits } from 'vue'

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
.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: bold;
}

.header-icon {
  font-size: 18px;
}

.priority-section, .input-section {
  margin-bottom: 20px;
}

.section-label {
  display: block;
  margin-bottom: 10px;
  font-weight: bold;
  color: #606266;
}

.action-buttons {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}
</style>