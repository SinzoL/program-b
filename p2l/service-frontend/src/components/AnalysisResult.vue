
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
  overflow: hidden; /* 防止内容溢出影响布局 */
  position: relative; /* 为绝对定位做准备 */
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
  position: absolute !important;
  right: 118px !important; /* 按钮宽度88px + 右边距15px + 分数区域右边距15px */
  top: 50% !important;
  transform: translateY(-50%) !important;
  z-index: 1 !important;
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

/* 超级强制固定按钮样式 - 完全锁定尺寸和位置 */
.call-model-btn {
  width: 88px !important;
  height: 32px !important;
  min-width: 88px !important;
  max-width: 88px !important;
  min-height: 32px !important;
  max-height: 32px !important;
  flex-shrink: 0 !important;
  flex-grow: 0 !important;
  flex-basis: 88px !important;
  text-align: center !important;
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
  box-sizing: border-box !important;
  padding: 0 8px !important;
  margin: 0 !important;
  border: 1px solid #409eff !important;
  background-color: #409eff !important;
  color: white !important;
  border-radius: 4px !important;
  font-size: 12px !important;
  line-height: 1 !important;
  position: relative !important;
  overflow: hidden !important;
}

/* 强制覆盖Element Plus的所有按钮样式 */
.call-model-btn.el-button,
.call-model-btn.el-button--primary,
.call-model-btn.el-button--small {
  width: 88px !important;
  height: 32px !important;
  min-width: 88px !important;
  max-width: 88px !important;
  min-height: 32px !important;
  max-height: 32px !important;
  padding: 0 8px !important;
  margin: 0 !important;
  border: 1px solid #409eff !important;
  background-color: #409eff !important;
  font-size: 12px !important;
  line-height: 1 !important;
}

/* 按钮内容完全固定 */
.call-model-btn :deep(.el-button__text),
.call-model-btn :deep(span) {
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
  width: 100% !important;
  height: 100% !important;
  white-space: nowrap !important;
  overflow: hidden !important;
  text-overflow: ellipsis !important;
  font-size: 12px !important;
  line-height: 1 !important;
  margin: 0 !important;
  padding: 0 !important;
}

/* 加载状态样式 */
.call-model-btn.is-loading,
.call-model-btn[loading="true"] {
  width: 88px !important;
  height: 32px !important;
  background-color: #409eff !important;
  border-color: #409eff !important;
  pointer-events: none !important;
}

/* 加载图标样式 */
.call-model-btn :deep(.el-icon.is-loading),
.call-model-btn :deep(.el-icon) {
  margin-right: 4px !important;
  margin-left: 0 !important;
  margin-top: 0 !important;
  margin-bottom: 0 !important;
  font-size: 12px !important;
  animation: rotating 2s linear infinite !important;
}

/* 悬停和焦点状态 */
.call-model-btn:hover,
.call-model-btn:focus,
.call-model-btn:active,
.call-model-btn.is-loading:hover,
.call-model-btn.is-loading:focus {
  width: 88px !important;
  height: 32px !important;
  background-color: #337ecc !important;
  border-color: #337ecc !important;
  transform: none !important;
  box-shadow: none !important;
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

/* 确保按钮容器也是固定的 */
.ranking-item > .call-model-btn {
  position: absolute !important;
  right: 15px !important;
  top: 50% !important;
  transform: translateY(-50%) !important;
  z-index: 1 !important;
}

/* 为了给绝对定位的按钮和分数区域留出空间，调整ranking-item的padding */
.ranking-item {
  padding-right: 253px !important; /* 15px + 120px + 15px + 88px + 15px (分数区域 + 按钮区域) */
}
</style>