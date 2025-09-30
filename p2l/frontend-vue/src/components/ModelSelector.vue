<template>
  <el-popover
    placement="bottom-end"
    :width="400"
    trigger="click"
    popper-class="model-selector-popover"
  >
    <template #reference>
      <el-button type="primary" size="small" class="model-selector-btn">
        <el-icon><Setting /></el-icon>
        已加载模型 ({{ enabledModelsCount }}/{{ totalModelsCount }})
      </el-button>
    </template>

    <div class="model-selector-content">
      <div class="selector-header">
        <h4>模型选择器</h4>
        <div class="header-actions">
          <el-button size="small" @click="selectAll">全选</el-button>
          <el-button size="small" @click="selectNone">全不选</el-button>
          <el-button size="small" type="primary" @click="selectRecommended">推荐配置</el-button>
        </div>
      </div>

      <div class="provider-groups">
        <div 
          v-for="(models, provider) in groupedModels" 
          :key="provider"
          class="provider-group"
        >
          <div class="provider-header">
            <el-checkbox
              :model-value="isProviderFullySelected(provider)"
              :indeterminate="isProviderPartiallySelected(provider)"
              @change="toggleProvider(provider, $event)"
            >
              <strong>{{ provider }}</strong>
            </el-checkbox>
            <el-tag size="small" type="info">
              {{ getProviderEnabledCount(provider) }}/{{ models.length }}
            </el-tag>
          </div>

          <div class="models-list">
            <div 
              v-for="model in models" 
              :key="model.name"
              class="model-item"
              :class="{ 'disabled': !modelStates[model.name] }"
            >
              <el-checkbox
                :model-value="modelStates[model.name]"
                @change="toggleModel(model.name, $event)"
              >
                <div class="model-info">
                  <span class="model-name">{{ model.name }}</span>
                  <div class="model-tags">
                    <el-tag size="small" :type="getModelTypeColor(model.type)">
                      {{ model.type }}
                    </el-tag>
                    <el-tag v-if="model.hasApiKey" size="small" type="success">
                      有API
                    </el-tag>
                    <el-tag v-else size="small" type="warning">
                      无API
                    </el-tag>
                  </div>
                </div>
              </el-checkbox>
            </div>
          </div>
        </div>
      </div>

      <div class="selector-footer">
        <el-alert
          title="提示"
          type="info"
          :closable="false"
          show-icon
        >
          <template #default>
            <span>取消勾选的模型将不会出现在智能推荐排名中。建议保留有API密钥的模型以获得真实响应。</span>
          </template>
        </el-alert>
      </div>
    </div>
  </el-popover>
</template>

<script setup>
import { ref, computed, watch, defineProps, defineEmits } from 'vue'

const props = defineProps({
  availableModels: {
    type: Array,
    default: () => []
  },
  enabledModels: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['update:enabledModels'])

// 模型状态管理
const modelStates = ref({})

// 初始化模型状态
const initializeModelStates = () => {
  const states = {}
  props.availableModels.forEach(model => {
    states[model.name] = props.enabledModels.includes(model.name)
  })
  modelStates.value = states
}

// 监听props变化
watch(() => props.availableModels, initializeModelStates, { immediate: true })
watch(() => props.enabledModels, initializeModelStates, { immediate: true })

// 计算属性
const totalModelsCount = computed(() => props.availableModels.length)

const enabledModelsCount = computed(() => {
  return Object.values(modelStates.value).filter(Boolean).length
})

const groupedModels = computed(() => {
  const groups = {}
  props.availableModels.forEach(model => {
    if (!groups[model.provider]) {
      groups[model.provider] = []
    }
    groups[model.provider].push(model)
  })
  return groups
})

// 提供商相关方法
const isProviderFullySelected = (provider) => {
  const models = groupedModels.value[provider]
  return models.every(model => modelStates.value[model.name])
}

const isProviderPartiallySelected = (provider) => {
  const models = groupedModels.value[provider]
  const selectedCount = models.filter(model => modelStates.value[model.name]).length
  return selectedCount > 0 && selectedCount < models.length
}

const getProviderEnabledCount = (provider) => {
  const models = groupedModels.value[provider]
  return models.filter(model => modelStates.value[model.name]).length
}

const toggleProvider = (provider, enabled) => {
  const models = groupedModels.value[provider]
  models.forEach(model => {
    modelStates.value[model.name] = enabled
  })
  emitEnabledModels()
}

// 模型操作方法
const toggleModel = (modelName, enabled) => {
  modelStates.value[modelName] = enabled
  emitEnabledModels()
}

const selectAll = () => {
  props.availableModels.forEach(model => {
    modelStates.value[model.name] = true
  })
  emitEnabledModels()
}

const selectNone = () => {
  props.availableModels.forEach(model => {
    modelStates.value[model.name] = false
  })
  emitEnabledModels()
}

const selectRecommended = () => {
  // 推荐配置：选择有API密钥的模型
  props.availableModels.forEach(model => {
    modelStates.value[model.name] = model.hasApiKey || false
  })
  emitEnabledModels()
}

// 辅助方法
const getModelTypeColor = (type) => {
  const colors = {
    'GPT': 'success',
    'Claude': 'primary',
    'Gemini': 'warning',
    'LLaMA': 'info',
    'Qwen': 'danger'
  }
  return colors[type] || 'info'
}

const emitEnabledModels = () => {
  const enabled = Object.keys(modelStates.value).filter(
    modelName => modelStates.value[modelName]
  )
  emit('update:enabledModels', enabled)
}
</script>

<style scoped>
.model-selector-btn {
  display: flex;
  align-items: center;
  gap: 5px;
}

.model-selector-content {
  max-height: 500px;
  overflow-y: auto;
}

.selector-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
  padding-bottom: 10px;
  border-bottom: 1px solid #ebeef5;
}

.selector-header h4 {
  margin: 0;
  color: #303133;
}

.header-actions {
  display: flex;
  gap: 5px;
}

.provider-groups {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.provider-group {
  border: 1px solid #ebeef5;
  border-radius: 8px;
  padding: 12px;
}

.provider-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.models-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-left: 20px;
}

.model-item {
  padding: 8px;
  border-radius: 6px;
  transition: background-color 0.3s;
}

.model-item:hover {
  background-color: #f5f7fa;
}

.model-item.disabled {
  opacity: 0.6;
}

.model-info {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.model-name {
  font-weight: 500;
  color: #303133;
}

.model-tags {
  display: flex;
  gap: 5px;
}

.selector-footer {
  margin-top: 15px;
  padding-top: 15px;
  border-top: 1px solid #ebeef5;
}

.selector-footer :deep(.el-alert) {
  border-radius: 6px;
}
</style>

<style>
.model-selector-popover {
  padding: 16px !important;
}
</style>