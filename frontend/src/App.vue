<template>
  <div id="app">
    <el-container class="app-container">
      <!-- 顶部导航 -->
      <el-header class="app-header">
        <div class="header-content">
          <div class="logo">
            <CubeLogo 
              :size="28" 
              color="#4A90E2" 
              variant="light"
              class="logo-icon"
            />
            <span class="logo-text">P2L智能路由系统</span>
          </div>
        </div>
      </el-header>

      <!-- 主要内容区域 -->
      <el-main class="app-main">
        <router-view />
      </el-main>

      <!-- 底部Footer -->
      <el-footer class="app-footer-container">
        <AppFooter />
      </el-footer>
    </el-container>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useP2LStore } from './stores/p2l'
import CubeLogo from './components/icons/CubeLogo.vue'
import AppFooter from './components/AppFooter.vue'

const p2lStore = useP2LStore()

onMounted(() => {
  // 初始化检查后端服务状态
  p2lStore.checkBackendHealth()
})
</script>

<style scoped>
.app-container {
  min-height: 100vh;
  background: #f5f5f5;
  position: relative;
  overflow: hidden;
}

.app-header {
  background: #ffffff;
  border-bottom: 1px solid #d0d0d0;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 100%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

.logo {
  display: flex;
  align-items: center;
  color: #2c3e50;
  font-size: 20px;
  font-weight: bold;
}

.logo-icon {
  margin-right: 12px;
}

.logo-text {
  color: #2c3e50;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 15px;
}

.model-badge :deep(.el-badge__content) {
  background-color: #67c23a;
}

.app-main {
  padding: 0;
  max-width: 1200px;
  margin: 0 auto;
  flex: 1;
}

.app-footer-container {
  padding: 0;
  height: auto;
}
</style>

<!-- 全局样式 - 科技风通知 -->
<style>
.tech-notification {
  background: rgba(108, 117, 125, 0.95) !important;
  border: 1px solid #6c757d !important;
  backdrop-filter: blur(10px) !important;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2) !important;
  border-radius: 8px !important;
}

.tech-notification .el-notification__title {
  color: #ffffff !important;
  font-weight: bold !important;
}

.tech-notification .el-notification__content {
  color: #f8f9fa !important;
}

.tech-notification .el-notification__icon {
  color: #ffffff !important;
}
</style>
