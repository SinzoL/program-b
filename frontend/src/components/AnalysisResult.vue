<template>
  <el-card v-if="analysis" class="analysis-card tech-card" shadow="hover">
    <template #header>
      <div class="card-header">
        <TechIcons name="analytics" :size="20" color="#00d4ff" />
        <span>P2L智能分析</span>
      </div>
    </template>
    
    <div class="analysis-content">
      <!-- 任务特征 -->
      <div class="task-info">
        <div class="tech-table">
          <div class="table-row">
            <div class="table-cell label">类型</div>
            <div class="table-cell value">
              <el-tooltip :content="analysis?.task_analysis?.task_type || '未知'" placement="top">
                <el-tag class="tech-tag">{{ analysis?.task_analysis?.task_type || '未知' }}</el-tag>
              </el-tooltip>
            </div>
            <div class="table-cell label">复杂度</div>
            <div class="table-cell value">
              <el-tooltip :content="analysis?.task_analysis?.complexity || '未知'" placement="top">
                <el-tag class="tech-tag" :type="getComplexityType(analysis.complexity)">
                  {{ analysis?.task_analysis?.complexity || '未知' }}
                </el-tag>
              </el-tooltip>
            </div>
          </div>
          <div class="table-row">
            <div class="table-cell label">语言</div>
            <div class="table-cell value">
              <el-tooltip :content="analysis?.task_analysis?.language || '未知'" placement="top">
                <el-tag class="tech-tag" type="info">{{ analysis?.task_analysis?.language || '未知' }}</el-tag>
              </el-tooltip>
            </div>
            <div class="table-cell label">推荐模型</div>
            <div class="table-cell value">
              <el-tooltip :content="analysis.recommended_model" placement="top">
                <el-tag class="tech-tag recommended-model">{{ analysis.recommended_model }}</el-tag>
              </el-tooltip>
            </div>
          </div>
        </div>
      </div>

      <!-- 模型排名 -->
      <div class="rankings">
        <div class="rankings-header">
          <TechIcons name="performance" :size="18" color="#00ff88" />
          <h4>模型智能排名</h4>
        </div>
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
import { computed } from 'vue'
import TechIcons from './icons/TechIcons.vue'

const props = defineProps({
  analysis: { type: Object, default: null },
  recommendations: { type: Array, default: () => [] },
  enabledModels: { type: Array, default: () => [] },
  loading: { type: Boolean, default: false },
  getModelInfo: { type: Function, required: true }
})

const emit = defineEmits(['call-llm'])

const sortedRecommendations = computed(() => {
  return [...props.recommendations]
    .filter(rec => props.enabledModels.includes(rec.model))
    .sort((a, b) => b.score - a.score)
})

const getComplexityType = (complexity) => {
  const types = { '简单': 'success', '中等': 'warning', '复杂': 'danger' }
  return types[complexity] || 'info'
}

const getScoreColor = (score) => {
  if (score >= 0.8) return '#67c23a'
  if (score >= 0.6) return '#e6a23c'
  return '#f56c6c'
}

const handleCallLLM = (modelName) => emit('call-llm', modelName)
</script>

<style scoped>
.analysis-card {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 700px;
  height: 100%;
  overflow: visible;
  border: 2px solid #00d4ff;
  background: linear-gradient(135deg, rgba(0, 212, 255, 0.05) 0%, rgba(0, 255, 136, 0.05) 100%);
  box-shadow: 0 4px 20px rgba(0, 212, 255, 0.2);
  position: relative;
}

.analysis-card::before {
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

.analysis-card :deep(.el-card__header) {
  background: linear-gradient(135deg, rgba(0, 212, 255, 0.1), rgba(0, 255, 136, 0.05));
  border-bottom: 1px solid rgba(0, 212, 255, 0.3);
}

.analysis-card :deep(.el-card__body) {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 20px;
  overflow: visible;
  min-height: 600px;
  background: rgba(15, 15, 35, 0.02);
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: bold;
  color: #00d4ff;
}

.analysis-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
  height: 100%;
  min-height: 600px;
}

.task-info {
  flex-shrink: 0;
  margin-bottom: 20px;
}

.tech-table {
  border: 1px solid rgba(0, 212, 255, 0.3);
  border-radius: 8px;
  background: linear-gradient(135deg, rgba(0, 212, 255, 0.05), rgba(0, 255, 136, 0.02));
  overflow: hidden;
  position: relative;
}

.tech-table::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 2px;
  background: linear-gradient(90deg, transparent, #00d4ff, transparent);
  animation: scan 3s linear infinite;
}

.table-row {
  display: grid;
  grid-template-columns: 120px 1fr 120px 1fr;
  border-bottom: 1px solid rgba(0, 212, 255, 0.2);
}

.table-row:last-child {
  border-bottom: none;
}

.table-cell {
  padding: 12px 16px;
  display: flex;
  align-items: center;
  gap: 6px;
  border-right: 1px solid rgba(0, 212, 255, 0.2);
  transition: all 0.3s ease;
}

.table-cell:last-child {
  border-right: none;
}

.table-cell.label {
  background: linear-gradient(135deg, rgba(0, 212, 255, 0.1), rgba(0, 255, 136, 0.05));
  font-weight: bold;
  color: #00d4ff;
  font-size: 14px;
  justify-content: flex-start;
  text-align: left;
}

.table-cell.value {
  background: linear-gradient(135deg, rgba(15, 15, 35, 0.02), rgba(0, 212, 255, 0.01));
  color: #333;
}

.table-cell.label:hover {
  background: linear-gradient(135deg, rgba(0, 212, 255, 0.15), rgba(0, 255, 136, 0.08));
  transform: translateY(-1px);
  box-shadow: inset 0 1px 3px rgba(0, 212, 255, 0.2);
}

.table-cell.value:hover {
  background: linear-gradient(135deg, rgba(0, 212, 255, 0.08), rgba(0, 255, 136, 0.05));
  transform: translateY(-1px);
  box-shadow: inset 0 1px 3px rgba(0, 212, 255, 0.1);
}

.tech-tag {
  border: 1px solid rgba(0, 212, 255, 0.3) !important;
  background: linear-gradient(135deg, rgba(0, 212, 255, 0.1), rgba(0, 255, 136, 0.05)) !important;
  color: #00d4ff !important;
  font-weight: bold;
  transition: all 0.3s ease;
  max-width: 100px !important;
  overflow: hidden !important;
  text-overflow: ellipsis !important;
  white-space: nowrap !important;
  display: inline-flex !important;
  align-items: center !important;
  justify-content: flex-start !important;
  line-height: 1 !important;
  padding-left: 8px !important;
  padding-right: 8px !important;
}

.tech-tag:hover {
  border-color: #00d4ff !important;
  box-shadow: 0 2px 8px rgba(0, 212, 255, 0.3);
  transform: translateY(-1px);
}

.recommended-model {
  background: linear-gradient(135deg, rgba(0, 255, 136, 0.2), rgba(0, 212, 255, 0.1)) !important;
  border-color: rgba(0, 255, 136, 0.5) !important;
  color: #00ff88 !important;
  box-shadow: 0 0 8px rgba(0, 255, 136, 0.3);
}

.recommended-model:hover {
  box-shadow: 0 2px 12px rgba(0, 255, 136, 0.5);
}

.rankings {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
}

.rankings-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 15px;
  flex-shrink: 0;
}

.rankings-header h4 {
  margin: 0;
  color: #00ff88;
  font-weight: bold;
}

.ranking-list {
  height: 440px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  overflow-y: auto;
  padding: 12px;
  padding-right: 8px;
  border: 1px solid rgba(0, 212, 255, 0.3);
  border-radius: 8px;
  background: linear-gradient(135deg, rgba(15, 15, 35, 0.05), rgba(0, 212, 255, 0.02));
}

.ranking-list::-webkit-scrollbar {
  width: 6px;
}

.ranking-list::-webkit-scrollbar-track {
  background: rgba(0, 212, 255, 0.1);
  border-radius: 3px;
}

.ranking-list::-webkit-scrollbar-thumb {
  background: rgba(0, 212, 255, 0.5);
  border-radius: 3px;
}

.ranking-list::-webkit-scrollbar-thumb:hover {
  background: rgba(0, 212, 255, 0.7);
}

.ranking-item {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 15px;
  border: 1px solid rgba(0, 212, 255, 0.3);
  border-radius: 8px;
  transition: all 0.3s;
  min-height: 80px;
  height: 80px;
  overflow: hidden;
  position: relative;
  background: linear-gradient(135deg, rgba(15, 15, 35, 0.05), rgba(0, 212, 255, 0.02));
}

.ranking-item::before {
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

.ranking-item:hover {
  border-color: #00d4ff;
  box-shadow: 0 4px 16px rgba(0, 212, 255, 0.2);
  transform: translateY(-2px);
}

.ranking-item:hover::before {
  opacity: 1;
}

.top-recommendation {
  border-color: #00ff88;
  background: linear-gradient(135deg, rgba(0, 255, 136, 0.1), rgba(0, 212, 255, 0.05));
}

.top-recommendation::before {
  background: linear-gradient(90deg, transparent, #00ff88, transparent);
}

.rank-badge {
  width: 30px;
  height: 30px;
  border-radius: 50%;
  background: linear-gradient(135deg, #00d4ff, #0099cc);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  flex-shrink: 0;
  box-shadow: 0 2px 8px rgba(0, 212, 255, 0.3);
  border: 1px solid rgba(0, 212, 255, 0.5);
}

.top-recommendation .rank-badge {
  background: linear-gradient(135deg, #00ff88, #00cc66);
  box-shadow: 0 2px 8px rgba(0, 255, 136, 0.3);
  border: 1px solid rgba(0, 255, 136, 0.5);
}

.model-info {
  flex: 1;
}

.model-name {
  font-weight: bold;
  margin-bottom: 5px;
  color: #00d4ff;
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
  width: 120px;
  flex-shrink: 0;
  position: absolute !important;
  right: 118px !important;
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
  color: #00ff88;
  line-height: 1;
  text-shadow: 0 0 4px rgba(0, 255, 136, 0.5);
}

.score-label {
  font-size: 12px;
  color: #00d4ff;
}

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

/* 按钮基础样式 */
.call-model-btn,
.call-model-btn.el-button,
.call-model-btn.el-button--primary,
.call-model-btn.el-button--small,
.call-model-btn.is-loading,
.call-model-btn[loading="true"] {
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

.call-model-btn.is-loading,
.call-model-btn[loading="true"] {
  pointer-events: none !important;
}

/* 按钮文本样式 */
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

/* 按钮图标样式 */
.call-model-btn :deep(.el-icon.is-loading),
.call-model-btn :deep(.el-icon) {
  margin: 0 4px 0 0 !important;
  font-size: 12px !important;
  animation: rotating 2s linear infinite !important;
}

/* 按钮悬停状态 */
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

@keyframes rotating {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.ranking-item > .call-model-btn {
  position: absolute !important;
  right: 15px !important;
  top: 50% !important;
  transform: translateY(-50%) !important;
  z-index: 1 !important;
}

.ranking-item {
  padding-right: 253px !important;
}
</style>