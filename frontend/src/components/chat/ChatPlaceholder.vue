<template>
  <el-card class="placeholder-chat tech-card" shadow="hover">
    <template #header>
      <div class="placeholder-header">
        <div class="placeholder-title">
          <TechIcons name="brain" :size="20" color="#00d4ff" />
          <span>对话区域</span>
          <el-tag size="small" type="info" class="tech-tag">等待输入</el-tag>
        </div>
      </div>
    </template>
    
    <div class="placeholder-content">
      <!-- 问题占位符 -->
      <div class="content-section">
        <div class="section-header">
          <TechIcons name="analytics" :size="16" color="#00d4ff" />
          <span>问题</span>
        </div>
        <div class="section-content placeholder-text">
          <div class="placeholder-message">
            <CubeLogo :size="32" color="#00d4ff" variant="default" class="placeholder-icon" />
            <span>在左侧输入问题，分析后选择合适模型解答</span>
          </div>
        </div>
      </div>
      
      <!-- 回答占位符 -->
      <div class="content-section">
        <div class="section-header">
          <TechIcons name="robot" :size="16" color="#00d4ff" />
          <span>回答</span>
        </div>
        <div class="section-content placeholder-text">
          <div class="placeholder-message">
            <CubeLogo :size="32" color="#00d4ff" variant="default" :animate="true" class="placeholder-icon loading-pulse" />
            <span>模型的回答将在此展示</span>
          </div>
        </div>
      </div>
    </div>
  </el-card>
</template>

<script setup>
import TechIcons from '../icons/TechIcons.vue'
import CubeLogo from '../icons/CubeLogo.vue'
</script>

<style scoped>
.placeholder-chat {
  height: 100%;
  min-height: 650px;
  border: 2px dashed #00d4ff;
  background: linear-gradient(135deg, rgba(0, 212, 255, 0.05) 0%, rgba(0, 212, 255, 0.1) 100%);
  box-shadow: 0 4px 20px rgba(0, 212, 255, 0.2);
  display: flex;
  flex-direction: column;
  position: relative;
  overflow: hidden;
}

.placeholder-chat::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(0, 212, 255, 0.1), transparent);
  animation: shimmer 3s infinite;
}

@keyframes shimmer {
  0% { left: -100%; }
  100% { left: 100%; }
}

.placeholder-chat :deep(.el-card__body) {
  flex: 1;
  min-height: 600px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background: rgba(15, 15, 35, 0.02);
}

.placeholder-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.placeholder-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: bold;
  color: #00d4ff;
}

.tech-tag {
  background: linear-gradient(135deg, #00d4ff, #0099cc);
  color: white;
  border: none;
  box-shadow: 0 2px 8px rgba(0, 212, 255, 0.3);
}

.placeholder-content {
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
  border-bottom: 1px solid rgba(0, 212, 255, 0.2);
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
  background: linear-gradient(135deg, rgba(0, 212, 255, 0.1), rgba(0, 212, 255, 0.05));
  border-bottom: 1px solid rgba(0, 212, 255, 0.2);
  display: flex;
  align-items: center;
  gap: 8px;
  color: #00d4ff;
  font-weight: 500;
}

.section-content {
  flex: 1;
  margin: 0;
}

.placeholder-text {
  background: linear-gradient(135deg, rgba(15, 15, 35, 0.05), rgba(0, 212, 255, 0.02));
  border: none;
  color: #666;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0;
}

.placeholder-message {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  text-align: center;
}

.placeholder-icon {
  opacity: 0.6;
}

.loading-pulse {
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 0.6; }
  50% { opacity: 1; }
}

.placeholder-message span {
  font-size: 14px;
  line-height: 1.5;
  max-width: 300px;
  color: #888;
}
</style>