<template>
  <el-card class="status-card" shadow="hover">
    <template #header>
      <div class="card-header">
        <el-icon class="header-icon"><Monitor /></el-icon>
        <span>系统状态</span>
        <div class="header-actions">
          <ModelSelector
            :available-models="availableModels"
            :enabled-models="enabledModels"
            @update:enabled-models="handleEnabledModelsChange"
          />
        </div>
      </div>
    </template>
    <div class="status-content">
      <el-tag :type="backendHealth ? 'success' : 'danger'" size="large">
        <el-icon><CircleCheck v-if="backendHealth" /><CircleClose v-else /></el-icon>
        {{ backendHealth ? 'P2L服务正常' : 'P2L服务离线' }}
      </el-tag>
      <el-button 
        type="primary" 
        @click="handleCheckHealth" 
        :loading="loading"
        size="small"
      >
        重新检测
      </el-button>
    </div>
  </el-card>
</template>

<script setup>
import { defineProps, defineEmits } from 'vue'
import ModelSelector from './ModelSelector.vue'

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
  }
})

const emit = defineEmits(['check-health', 'update:enabled-models'])

const handleCheckHealth = () => {
  emit('check-health')
}

const handleEnabledModelsChange = (enabledModels) => {
  emit('update:enabled-models', enabledModels)
}
</script>

<style scoped>
.status-card {
  margin-bottom: 20px;
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

.header-actions {
  margin-left: auto;
}

.status-content {
  display: flex;
  align-items: center;
  gap: 15px;
}
</style>