<template>
  <el-dialog v-model="visible" title="示例问题" width="600px" @close="handleClose">
    <div class="examples-list">
      <div 
        v-for="example in exampleQuestions" 
        :key="example.id"
        class="example-item"
        @click="handleUseExample(example.prompt)"
      >
        <div class="example-category">{{ example.category }}</div>
        <div class="example-prompt">{{ example.prompt }}</div>
        <div class="example-description">{{ example.description }}</div>
      </div>
    </div>
  </el-dialog>
</template>

<script setup>
import { ref, defineProps, defineEmits, watch } from 'vue'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:modelValue', 'use-example'])

const visible = ref(props.modelValue)

// 示例问题
const exampleQuestions = ref([
  {
    id: 1,
    category: '编程开发',
    prompt: '展示js实现字符串中下划线转化为驼峰',
    description: '代码实现类问题，适合测试编程能力'
  },
  {
    id: 2,
    category: '创意写作',
    prompt: '写一首关于人工智能的现代诗',
    description: '创意类问题，测试文学创作能力'
  },
  {
    id: 3,
    category: '数据分析',
    prompt: '分析电商网站用户行为数据的关键指标',
    description: '分析类问题，测试逻辑推理能力'
  },
  {
    id: 4,
    category: '技术解释',
    prompt: '解释什么是区块链技术及其应用场景',
    description: '解释类问题，测试知识整理能力'
  }
])

watch(() => props.modelValue, (newVal) => {
  visible.value = newVal
})

watch(visible, (newVal) => {
  emit('update:modelValue', newVal)
})

const handleClose = () => {
  visible.value = false
}

const handleUseExample = (prompt) => {
  emit('use-example', prompt)
  visible.value = false
}
</script>

<style scoped>
.examples-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.example-item {
  padding: 15px;
  border: 1px solid #ebeef5;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
}

.example-item:hover {
  border-color: #409eff;
  background: #f0f9ff;
}

.example-category {
  font-size: 12px;
  color: #909399;
  margin-bottom: 5px;
}

.example-prompt {
  font-weight: bold;
  margin-bottom: 5px;
}

.example-description {
  font-size: 14px;
  color: #606266;
}
</style>