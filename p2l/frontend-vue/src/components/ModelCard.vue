<template>
  <el-card class="model-card" shadow="hover">
    <template #header>
      <div class="model-header">
        <div class="model-title">
          <el-icon class="model-icon"><Cpu /></el-icon>
          <span>{{ model.name }}</span>
        </div>
        <el-tag :type="getProviderType(model.provider)" size="small">
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
        >
          选择模型
        </el-button>
        <el-button 
          @click="$emit('info', model)"
          size="small"
        >
          详细信息
        </el-button>
      </div>
    </div>
  </el-card>
</template>

<script setup>
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
}

.model-icon {
  font-size: 18px;
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
  padding: 10px;
  background: #f8f9fa;
  border-radius: 6px;
}

.score-label {
  font-size: 12px;
  color: #909399;
  margin-bottom: 8px;
}

.score-value {
  text-align: center;
  font-weight: bold;
  color: #409eff;
  margin-top: 5px;
}

.model-actions {
  display: flex;
  gap: 8px;
}
</style>