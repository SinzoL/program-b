<template>
  <el-card class="status-card tech-card" shadow="hover">
    <template #header>
      <div class="card-header">
        <TechIcons name="network" :size="20" color="#00d4ff" />
        <span>系统状态</span>
        <div class="header-actions">
          <!-- 智能路由开关 -->
          <div class="smart-routing-control">
            <el-tooltip content="开启后将自动选择评分最高的模型进行回答" placement="top">
              <div class="routing-switch-wrapper">
                <TechIcons name="brain" :size="16" :color="smartRoutingEnabled ? '#00ff88' : '#909399'" />
                <span class="switch-label">智能路由</span>
                <el-switch
                  :model-value="smartRoutingEnabled"
                  @change="handleSmartRoutingChange"
                  active-color="#00ff88"
                  inactive-color="#909399"
                  size="small"
                />
              </div>
            </el-tooltip>
          </div>
          <ModelSelector
            :available-models="availableModels"
            :enabled-models="enabledModels"
            @update:enabled-models="handleEnabledModelsChange"
          />
        </div>
      </div>
    </template>
    <div class="status-content">
      <div class="status-indicator" :class="{ 'online': backendHealth, 'offline': !backendHealth }">
        <div class="status-dot"></div>
        <span class="status-text">{{ backendHealth ? 'P2L服务正常' : 'P2L服务离线' }}</span>
        <div class="status-pulse" v-if="backendHealth"></div>
      </div>
      <el-button 
        type="primary" 
        @click="handleCheckHealth" 
        :loading="loading"
        size="small"
        class="tech-button"
      >
        <TechIcons name="analytics" :size="14" color="#ffffff" />
        重新检测
      </el-button>
    </div>
  </el-card>
</template>

<script setup>
import { defineProps, defineEmits } from 'vue'
import ModelSelector from './ModelSelector.vue'
import TechIcons from './icons/TechIcons.vue'

defineProps({
  backendHealth: {
    type: Boolean,
    default: false
  },
  loading: {
    type: Boolean,
    default: false
  },
  availableModels: {
    type: Array,
    default: () => []
  },
  enabledModels: {
    type: Array,
    default: () => []
  },
  smartRoutingEnabled: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['check-health', 'update:enabled-models', 'update:smart-routing'])

const handleCheckHealth = () => {
  emit('check-health')
}

const handleEnabledModelsChange = (enabledModels) => {
  emit('update:enabled-models', enabledModels)
}

const handleSmartRoutingChange = (enabled) => {
  emit('update:smart-routing', enabled)
}
</script>

<style scoped>
.status-card {
  margin-bottom: 20px;
}

.tech-card {
  border: 2px solid #00d4ff;
  background: linear-gradient(135deg, rgba(0, 212, 255, 0.05), rgba(0, 255, 136, 0.05));
  box-shadow: 0 4px 20px rgba(0, 212, 255, 0.2);
  position: relative;
  overflow: hidden;
}

.tech-card::before {
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

.tech-card :deep(.el-card__header) {
  background: linear-gradient(135deg, rgba(0, 212, 255, 0.1), rgba(0, 255, 136, 0.05));
  border-bottom: 1px solid rgba(0, 212, 255, 0.3);
}

.tech-card :deep(.el-card__body) {
  background: rgba(15, 15, 35, 0.02);
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: bold;
  color: #00d4ff;
}

.header-actions {
  margin-left: auto;
  display: flex;
  align-items: center;
  gap: 16px;
}

.smart-routing-control {
  display: flex;
  align-items: center;
}

.routing-switch-wrapper {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 12px;
  background: linear-gradient(135deg, rgba(0, 212, 255, 0.05), rgba(0, 255, 136, 0.02));
  border: 1px solid rgba(0, 212, 255, 0.2);
  border-radius: 20px;
  transition: all 0.3s ease;
  cursor: pointer;
}

.routing-switch-wrapper:hover {
  background: linear-gradient(135deg, rgba(0, 212, 255, 0.1), rgba(0, 255, 136, 0.05));
  border-color: rgba(0, 212, 255, 0.4);
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(0, 212, 255, 0.2);
}

.switch-label {
  font-size: 12px;
  font-weight: 500;
  color: #00d4ff;
  white-space: nowrap;
}

.routing-switch-wrapper:hover .switch-label {
  color: #00ff88;
}

/* 智能路由开关激活状态 */
.routing-switch-wrapper:has(.el-switch.is-checked) {
  background: linear-gradient(135deg, rgba(0, 255, 136, 0.1), rgba(0, 255, 136, 0.05));
  border-color: rgba(0, 255, 136, 0.4);
  box-shadow: 0 2px 12px rgba(0, 255, 136, 0.2);
}

.routing-switch-wrapper:has(.el-switch.is-checked) .switch-label {
  color: #00ff88;
}

.status-content {
  display: flex;
  align-items: center;
  gap: 15px;
}

.status-indicator {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 16px;
  border-radius: 20px;
  position: relative;
  transition: all 0.3s ease;
}

.status-indicator.online {
  background: linear-gradient(135deg, rgba(0, 255, 136, 0.1), rgba(0, 255, 136, 0.2));
  border: 1px solid rgba(0, 255, 136, 0.3);
  color: #00ff88;
}

.status-indicator.offline {
  background: linear-gradient(135deg, rgba(255, 107, 107, 0.1), rgba(255, 107, 107, 0.2));
  border: 1px solid rgba(255, 107, 107, 0.3);
  color: #ff6b6b;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  position: relative;
}

.online .status-dot {
  background: #00ff88;
  box-shadow: 0 0 10px rgba(0, 255, 136, 0.5);
}

.offline .status-dot {
  background: #ff6b6b;
  box-shadow: 0 0 10px rgba(255, 107, 107, 0.5);
}

.status-pulse {
  position: absolute;
  left: 24px;
  top: 50%;
  transform: translateY(-50%);
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: rgba(0, 255, 136, 0.4);
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0% {
    transform: translateY(-50%) scale(1);
    opacity: 1;
  }
  100% {
    transform: translateY(-50%) scale(2.5);
    opacity: 0;
  }
}

.status-text {
  font-weight: 500;
  font-size: 14px;
}

.tech-button {
  display: flex;
  align-items: center;
  gap: 6px;
  transition: all 0.3s ease;
  background: linear-gradient(135deg, #00d4ff, #00ff88);
  border: none;
  box-shadow: 0 4px 15px rgba(0, 212, 255, 0.3);
}

.tech-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 212, 255, 0.4);
  background: linear-gradient(135deg, #00ff88, #00d4ff);
}
</style>