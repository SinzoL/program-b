<template>
  <el-card class="model-card tech-card" shadow="hover">
    <template #header>
      <div class="model-header">
        <div class="model-title">
          <TechIcons name="cpu" :size="18" color="#409eff" />
          <span>{{ model.name }}</span>
        </div>
        <el-tag :type="getProviderType(model.provider)" size="small" class="provider-tag">
          {{ model.provider }}
        </el-tag>
      </div>
    </template>
    
    <div class="model-content">
      <div class="model-info">
        <div class="info-item">
          <span class="label">类型：</span>
          <el-tag size="small" type="info">{{ model.type }}</el-tag>
        </div>
        <div class="info-item">
          <span class="label">成本：</span>
          <el-tag size="small" :type="getCostType(model.cost)">{{ model.cost }}</el-tag>
        </div>
        <div class="info-item">
          <span class="label">速度：</span>
          <el-tag size="small" :type="getSpeedType(model.speed)">{{ model.speed }}</el-tag>
        </div>
      </div>
      
      <div v-if="score !== undefined" class="score-section">
        <div class="score-label">P2L评分</div>
        <el-progress 
          :percentage="Math.round(score * 100)" 
          :color="getScoreColor(score)"
          :stroke-width="6"
        />
        <div class="score-value">{{ (score * 100).toFixed(1) }}%</div>
      </div>
      
      <div class="model-actions">
        <el-button 
          type="primary" 
          @click="$emit('select', model.name)"
          :loading="loading"
          size="small"
          class="tech-button primary-button"
        >
          <TechIcons name="robot" :size="14" color="#ffffff" />
          选择模型
        </el-button>
        <el-button 
          @click="$emit('info', model)"
          size="small"
          class="tech-button"
        >
          <TechIcons name="analyze" :size="14" color="#409eff" />
          详细信息
        </el-button>
      </div>
    </div>
  </el-card>
</template>

<script setup>
import TechIcons from './icons/TechIcons.vue'

defineProps({
  model: {
    type: Object,
    required: true
  },
  score: {
    type: Number,
    default: undefined
  },
  loading: {
    type: Boolean,
    default: false
  }
})

defineEmits(['select', 'info'])

const getProviderType = (provider) => {
  const types = {
    'OpenAI': 'success',
    'Anthropic': 'warning',
    'Google': 'info',
    'Meta': 'danger',
    'Mistral': ''
  }
  return types[provider] || ''
}

const getCostType = (cost) => {
  const types = {
    '极低': 'success',
    '低': 'success',
    '中': 'warning',
    '高': 'danger'
  }
  return types[cost] || 'info'
}

const getSpeedType = (speed) => {
  const types = {
    '极快': 'success',
    '快': 'success',
    '中': 'warning',
    '慢': 'danger'
  }
  return types[speed] || 'info'
}

const getScoreColor = (score) => {
  if (score >= 0.8) return '#67c23a'
  if (score >= 0.6) return '#e6a23c'
  return '#f56c6c'
}
</script>

<style scoped>
.model-card {
  height: 100%;
  transition: all 0.3s ease;
}

.tech-card {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.tech-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
  border-color: rgba(64, 158, 255, 0.3);
}

.model-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.model-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: bold;
  color: #2c3e50;
}

.provider-tag {
  background: linear-gradient(135deg, rgba(64, 158, 255, 0.1), rgba(103, 194, 58, 0.1));
  border: 1px solid rgba(64, 158, 255, 0.3);
  color: #409eff;
}

.model-content {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.model-info {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.label {
  font-size: 14px;
  color: #606266;
  min-width: 40px;
}

.score-section {
  padding: 12px;
  background: linear-gradient(135deg, rgba(64, 158, 255, 0.05), rgba(103, 194, 58, 0.05));
  border-radius: 8px;
  border: 1px solid rgba(64, 158, 255, 0.1);
  position: relative;
  overflow: hidden;
}

.score-section::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  animation: shimmer 2s infinite;
}

@keyframes shimmer {
  0% { left: -100%; }
  100% { left: 100%; }
}

.score-label {
  font-size: 12px;
  color: #909399;
  margin-bottom: 8px;
  font-weight: 500;
}

.score-value {
  text-align: center;
  font-weight: bold;
  color: #409eff;
  margin-top: 5px;
  font-size: 16px;
}

.model-actions {
  display: flex;
  gap: 8px;
}

.tech-button {
  display: flex;
  align-items: center;
  gap: 6px;
  transition: all 0.3s ease;
  border: 1px solid rgba(64, 158, 255, 0.3);
  background: rgba(255, 255, 255, 0.8);
}

.tech-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(64, 158, 255, 0.2);
}

.primary-button {
  background: linear-gradient(135deg, #409eff, #67c23a);
  border: none;
  box-shadow: 0 4px 15px rgba(64, 158, 255, 0.3);
}

.primary-button:hover {
  background: linear-gradient(135deg, #66b1ff, #85ce61);
  box-shadow: 0 8px 25px rgba(64, 158, 255, 0.4);
}
</style>