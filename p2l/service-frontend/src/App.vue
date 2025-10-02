<template>
  <div id="app">
    <el-container class="app-container">
      <!-- 顶部导航 -->
      <el-header class="app-header">
        <div class="header-content">
          <div class="logo">
            <el-icon class="logo-icon"><Cpu /></el-icon>
            <span class="logo-text">P2L智能路由系统</span>
          </div>
        </div>
      </el-header>

      <!-- 主要内容区域 -->
      <el-main class="app-main">
        <router-view />
      </el-main>
    </el-container>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useP2LStore } from './stores/p2l'

const p2lStore = useP2LStore()
const modelCount = ref(9)

onMounted(() => {
  // 初始化检查后端服务状态
  p2lStore.checkBackendHealth()
})
</script>

<style scoped>
.app-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
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
  font-size: 24px;
  margin-right: 10px;
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
}
</style>
