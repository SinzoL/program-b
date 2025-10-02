<template>
  <el-dialog 
    v-model="visible" 
    width="600px" 
    @close="handleClose"
    class="tech-dialog"
  >
    <template #header>
      <div class="dialog-header">
        <TechIcons name="database" :size="20" color="#00d4ff" />
        <span>示例问题</span>
      </div>
    </template>
    <div class="examples-list">
      <div 
        v-for="example in exampleQuestions" 
        :key="example.id"
        class="example-item"
        @click="handleUseExample(example.prompt)"
      >
        <div class="example-header">
          <TechIcons name="chip" :size="16" color="#00ff88" />
          <div class="example-category">{{ example.category }}</div>
        </div>
        <div class="example-prompt">{{ example.prompt }}</div>
        <div class="example-description">{{ example.description }}</div>
      </div>
    </div>
  </el-dialog>
</template>

<script setup>
import { ref, defineProps, defineEmits, watch } from 'vue'
import TechIcons from './icons/TechIcons.vue'

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
    category: '技术解释',
    prompt: '你是谁？',
    description: '解释类问题，测试知识整理能力'
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
  },
  {
    id: 5,
    category: '编程开发',
    prompt: '展示js实现字符串中下划线转化为驼峰',
    description: '代码实现类问题，适合测试编程能力'
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
.dialog-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: bold;
  color: #00d4ff;
}

.examples-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
  max-height: 400px;
  overflow-y: auto;
  padding-right: 8px;
}

/* 自定义滚动条 */
.examples-list::-webkit-scrollbar {
  width: 6px;
}

.examples-list::-webkit-scrollbar-track {
  background: rgba(0, 212, 255, 0.1);
  border-radius: 3px;
}

.examples-list::-webkit-scrollbar-thumb {
  background: rgba(0, 212, 255, 0.5);
  border-radius: 3px;
}

.examples-list::-webkit-scrollbar-thumb:hover {
  background: rgba(0, 212, 255, 0.7);
}

.example-item {
  padding: 15px;
  border: 1px solid rgba(0, 212, 255, 0.3);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
  background: linear-gradient(135deg, rgba(0, 212, 255, 0.05), rgba(0, 255, 136, 0.02));
  position: relative;
  overflow: hidden;
}

.example-item::before {
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

.example-item:hover {
  border-color: #00d4ff;
  box-shadow: 0 4px 16px rgba(0, 212, 255, 0.2);
  transform: translateY(-2px);
  background: linear-gradient(135deg, rgba(0, 212, 255, 0.1), rgba(0, 255, 136, 0.05));
}

.example-item:hover::before {
  opacity: 1;
}

.example-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.example-category {
  font-size: 12px;
  color: #00ff88;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.example-prompt {
  font-weight: bold;
  color: #00d4ff;
  margin-bottom: 8px;
  line-height: 1.4;
}

.example-description {
  font-size: 13px;
  color: #666;
  line-height: 1.4;
}
</style>

<style>
.tech-dialog .el-dialog {
  background: linear-gradient(135deg, rgba(0, 212, 255, 0.05), rgba(0, 255, 136, 0.02));
  border: 1px solid rgba(0, 212, 255, 0.3);
  box-shadow: 0 8px 32px rgba(0, 212, 255, 0.2);
}

.tech-dialog .el-dialog__header {
  background: linear-gradient(135deg, rgba(0, 212, 255, 0.1), rgba(0, 255, 136, 0.05));
  border-bottom: 1px solid rgba(0, 212, 255, 0.3);
}

.tech-dialog .el-dialog__body {
  background: rgba(15, 15, 35, 0.02);
}
</style>