<template>
  <el-card class="placeholder-chat tech-card" shadow="hover">
    <template #header>
      <div class="placeholder-header">
        <div class="placeholder-title">
          <TechIcons name="brain" :size="20" color="#6c757d" />
          <span>对话区域</span>
          <el-tag size="small" type="info" class="tech-tag">等待输入</el-tag>
        </div>
      </div>
    </template>
    
    <div class="placeholder-content">
      <!-- 问题占位符 -->
      <div class="content-section">
        <div class="section-header">
          <TechIcons name="analytics" :size="16" color="#6c757d" />
          <span>问题</span>
        </div>
        <div class="section-content placeholder-text">
          <div class="placeholder-message">
            <CubeLogo :size="32" color="#6c757d" variant="default" class="placeholder-icon" />
            <span>在左侧输入问题，分析后选择合适模型解答</span>
          </div>
        </div>
      </div>
      
      <!-- 回答占位符 -->
      <div class="content-section">
        <div class="section-header">
          <TechIcons name="robot" :size="16" color="#6c757d" />
          <span>回答</span>
        </div>
        <div class="section-content placeholder-text">
          <div class="placeholder-message">
            <CubeLogo :size="32" color="#6c757d" variant="default" :animate="true" class="placeholder-icon loading-pulse" />
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
  border: 2px dashed #d0d0d0;
  background: #ffffff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  position: relative;
  overflow: hidden;
}



.placeholder-chat :deep(.el-card__body) {
  flex: 1;
  min-height: 600px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background: #ffffff;
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
  color: #2c3e50;
}

.tech-tag {
  background: #6c757d;
  color: white;
  border: none;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
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
  border-bottom: 1px solid #e0e0e0;
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
  background: #f8f9fa;
  border-bottom: 1px solid #e0e0e0;
  display: flex;
  align-items: center;
  gap: 8px;
  color: #2c3e50;
  font-weight: 500;
}

.section-content {
  flex: 1;
  margin: 0;
}

.placeholder-text {
  background: #ffffff;
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