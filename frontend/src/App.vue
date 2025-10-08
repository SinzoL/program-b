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
  background: 
    radial-gradient(circle at 20% 80%, rgba(120, 119, 198, 0.3) 0%, transparent 50%),
    radial-gradient(circle at 80% 20%, rgba(255, 119, 198, 0.3) 0%, transparent 50%),
    radial-gradient(circle at 40% 40%, rgba(120, 219, 255, 0.2) 0%, transparent 50%),
    linear-gradient(135deg, #0f0f23 0%, #1a1a2e 25%, #16213e 50%, #0f3460 75%, #533483 100%);
  position: relative;
  overflow: hidden;
}

.app-container::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: 
    linear-gradient(90deg, transparent 0%, rgba(255, 255, 255, 0.02) 50%, transparent 100%),
    linear-gradient(0deg, transparent 0%, rgba(255, 255, 255, 0.02) 50%, transparent 100%);
  background-size: 100px 100px, 100px 100px;
  animation: grid-move 20s linear infinite;
  pointer-events: none;
}

@keyframes grid-move {
  0% { transform: translate(0, 0); }
  100% { transform: translate(100px, 100px); }
}

.app-header {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
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
  color: white;
  font-size: 20px;
  font-weight: bold;
}

.logo-icon {
  margin-right: 12px;
  filter: drop-shadow(0 2px 4px rgba(74, 144, 226, 0.3));
}

.logo-text {
  background: linear-gradient(45deg, #fff, #e0e7ff);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
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
  background: linear-gradient(135deg, 
    rgba(0, 212, 255, 0.1) 0%, 
    rgba(0, 255, 136, 0.1) 50%, 
    rgba(255, 107, 107, 0.1) 100%) !important;
  border: 1px solid rgba(0, 212, 255, 0.3) !important;
  backdrop-filter: blur(10px) !important;
  box-shadow: 
    0 8px 32px rgba(0, 212, 255, 0.2),
    inset 0 1px 0 rgba(255, 255, 255, 0.1) !important;
  border-radius: 8px !important;
}

.tech-notification .el-notification__title {
  color: #00d4ff !important;
  font-weight: bold !important;
  text-shadow: 0 0 10px rgba(0, 212, 255, 0.5) !important;
}

.tech-notification .el-notification__content {
  color: #e8e8e8 !important;
}

.tech-notification .el-notification__icon {
  color: #00ff88 !important;
  filter: drop-shadow(0 0 8px rgba(0, 255, 136, 0.6)) !important;
}

.tech-notification::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(45deg, 
    transparent 30%, 
    rgba(0, 212, 255, 0.1) 50%, 
    transparent 70%);
  animation: tech-notification-scan 2s ease-in-out infinite;
  pointer-events: none;
  border-radius: 8px;
}

@keyframes tech-notification-scan {
  0%, 100% { transform: translateX(-100%); opacity: 0; }
  50% { transform: translateX(100%); opacity: 1; }
}
</style>
