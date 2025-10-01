
<template>
  <el-card v-if="analysis" class="analysis-card" shadow="hover">
    <template #header>
      <div class="card-header">
        <el-icon class="header-icon"><DataAnalysis /></el-icon>
        <span>P2L智能分析</span>
      </div>
    </template>
    
    <div class="analysis-content">
      <!-- 任务特征 -->
      <div class="task-info">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="任务类型">
            <el-tag>{{ analysis?.task_analysis?.task_type || '未知' }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="复杂度">
            <el-tag :type="getComplexityType(analysis.complexity)">
              {{ analysis?.task_analysis?.complexity || '未知' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="语言">
            <el-tag type="info">{{ analysis?.task_analysis?.language || '未知' }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="推荐模型">
            <el-tag type="success">{{ analysis.recommended_model }}</el-tag>
          </el-descriptions-item>
        </el-descriptions>
      </div>

      <!-- 模型排名 -->
      <div class="rankings">
        <h4>🏆 模型智能排名</h4>
        <div class="ranking-list">
          <div 
            v-for="(rec, index) in sortedRecommendations" 
            :key="rec.model"
            class="ranking-item"
            :class="{ 'top-recommendation': index === 0 }"
          >
            <div class="rank-badge">{{ index + 1 }}</div>
            <div class="model-info">
              <div class="model-name">{{ rec.model }}</div>
              <div class="model-details">
                <el-tag size="small">{{ getModelInfo(rec.model)?.provider }}</el-tag>
                <el-tag size="small" type="info">成本: {{ getModelInfo(rec.model)?.cost }}</el-tag>
                <el-tag size="small" type="warning">速度: {{ getModelInfo(rec.model)?.speed }}</el-tag>
              </div>
            </div>
            <div class="score-section">
              <div class="score-display">
                <div class="score-number">{{ Math.round(rec.score) }}</div>
                <div class="score-label">分</div>
              </div>
              <el-progress 
                :percentage="Math.round(rec.score)" 
                :color="getScoreColor(rec.score / 100)"
                :stroke-width="6"
                :show-text="false"
              />
            </div>
            <el-button 
              type="primary" 
              size="small"
              @click="handleCallLLM(rec.model)"
              :loading="loading"
              class="call-model-btn"
            >
              调用模型
            </el-button>
          </div>
        </div>
      </div>
    </div>
  </el-card>
</template>

<script setup>
import { defineProps, defineEmits, computed } from 'vue'

const props = defineProps({
  analysis: {
    type: Object,
    default: null
  },
  recommendations: {
    type: Array,
    default: () => []
  },
  enabledModels: {
    type: Array,
    default: () => []
  },
  loading: {
    type: Boolean,
    default: false
  },
  getModelInfo: {
    type: Function,
    required: true
  }
})

const emit = defineEmits(['call-llm'])

const sortedRecommendations = computed(() => {
  // 过滤出启用的模型，然后按分数排序
  return [...props.recommendations]
    .filter(rec => props.enabledModels.includes(rec.model))
    .sort((a, b) => b.score - a.score)
})

const getComplexityType = (complexity) => {
  const types = {
    '简单': 'success',
    '中等': 'warning', 
    '复杂': 'danger'
  }
  return types[complexity] || 'info'
}

const getScoreColor = (score) => {
  if (score >= 0.8) return '#67c23a'
  if (score >= 0.6) return '#e6a23c'
  return '#f56c6c'
}

const handleCallLLM = (modelName) => {
  emit('call-llm', modelName)
}
</script>

<style scoped>
.analysis-card {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 700px; /* 设置最小高度确保有足够显示空间 */
  height: 100%;
  overflow: visible; /* 允许内容超出显示 */
}

.analysis-card :deep(.el-card__body) {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 20px;
  overflow: visible; /* 允许内容超出显示 */
  min-height: 600px; /* 确保卡片体有足够高度 */
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: bold;
}

.header-icon {
  font-size: 18px;
}

.analysis-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
  height: 100%;
  min-height: 600px; /* 确保内容区域有足够高度 */
}

.task-info {
  flex-shrink: 0;
  margin-bottom: 20px;
}

.rankings {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
}

.rankings h4 {
  margin: 0 0 15px 0;
  color: #303133;
  flex-shrink: 0;
}

.ranking-list {
  /* 增加高度显示更多模型，每个模型约80px高度 + 间距 */
  height: 440px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  overflow-y: auto;
  padding: 12px;
  padding-right: 8px;
  border: 1px solid #ebeef5;
  border-radius: 8px;
  background: #fafafa;
}

/* 自定义滚动条样式 */
.ranking-list::-webkit-scrollbar {
  width: 6px;
}

.ranking-list::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.ranking-list::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.ranking-list::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

.ranking-item {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 15px;
  border: 1px solid #ebeef5;
  border-radius: 8px;
  transition: all 0.3s;
  min-height: 80px; /* 固定最小高度 */
  height: 80px; /* 固定高度 */
}

.ranking-item:hover {
  border-color: #409eff;
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.1);
}

.top-recommendation {
  border-color: #67c23a;
  background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
}

.rank-badge {
  width: 30px;
  height: 30px;
  border-radius: 50%;
  background: #409eff;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  flex-shrink: 0;
}

.top-recommendation .rank-badge {
  background: #67c23a;
}

.model-info {
  flex: 1;
}

.model-name {
  font-weight: bold;
  margin-bottom: 5px;
}

.model-details {
  display: flex;
  gap: 5px;
}

.score-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  min-width: 120px;
  width: 120px; /* 固定宽度 */
  flex-shrink: 0; /* 防止被压缩 */
}

.score-display {
  display: flex;
  align-items: baseline;
  gap: 2px;
}

.score-number {
  font-size: 24px;
  font-weight: bold;
  color: #409eff;
  line-height: 1;
}

.score-label {
  font-size: 12px;
  color: #909399;
}

/* 固定按钮宽度和高度，防止加载状态时位置偏移 */
.call-model-btn {
  width: 88px !important; /* 固定宽度，稍微增加一点 */
  height: 32px !important; /* 固定高度 */
  flex-shrink: 0; /* 防止被压缩 */
  text-align: center;
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
  box-sizing: border-box !important;
}

/* 确保加载状态时按钮内容不会改变布局 */
.call-model-btn :deep(.el-button__text) {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
  white-space: nowrap; /* 防止文字换行 */
}

/* 加载图标样式优化 */
.call-model-btn :deep(.el-icon.is-loading) {
  margin-right: 4px;
  animation: rotating 2s linear infinite;
}

/* 加载动画 */
@keyframes rotating {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

/* 确保按钮在不同状态下保持一致的外观 */
.call-model-btn:hover,
.call-model-btn:focus,
.call-model-btn:active {
  width: 88px !important;
  height: 32px !important;
}
</style>