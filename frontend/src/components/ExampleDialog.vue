<template>
  <el-dialog 
    v-model="visible" 
    width="650px"
    @close="handleClose"
    class="tech-dialog"
    :close-on-click-modal="false"
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
    category: '数据分析',
    prompt: '分析一下2024年全球AI发展趋势，包括主要技术突破和市场变化',
    description: '分析类问题，测试数据整理和趋势分析能力'
  },
  {
    id: 2,
    category: '创意写作',
    prompt: '为一个智能家居产品写一份吸引人的营销文案',
    description: '营销文案类问题，测试创意表达和商业思维'
  },
  {
    id: 3,
    category: '编程开发',
    prompt: '用Python实现一个简单的文件加密解密工具',
    description: '实用编程问题，测试算法设计和代码实现能力'
  },
  {
    id: 4,
    category: '问题解决',
    prompt: '如何优化一个电商网站的用户体验，提高转化率？',
    description: '业务优化问题，测试系统性思考和解决方案设计'
  },
  {
    id: 5,
    category: '学习辅导',
    prompt: '用通俗易懂的方式解释机器学习中的"过拟合"现象',
    description: '教学解释类问题，测试知识传达和简化表达能力'
  },
  {
    id: 6,
    category: '创意策划',
    prompt: '设计一个环保主题的社区活动方案，包括具体执行步骤',
    description: '策划类问题，测试创意思维和项目规划能力'
  },
  {
    id: 7,
    category: '技术咨询',
    prompt: '对比分析Vue.js和React在大型项目中的优缺点',
    description: '技术对比问题，测试深度分析和客观评估能力'
  },
  {
    id: 8,
    category: '生活助手',
    prompt: '制定一个适合上班族的健康饮食计划，包含一周菜谱',
    description: '生活规划问题，测试实用建议和个性化定制能力'
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
  max-height: 60vh;
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
  padding: 16px;
  border: 1px solid rgba(0, 212, 255, 0.4);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
  background: rgba(255, 255, 255, 0.95);
  position: relative;
  overflow: visible;
  margin-bottom: 4px;
  min-height: auto;
  height: auto;
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
  box-shadow: 0 4px 16px rgba(0, 212, 255, 0.3);
  transform: translateY(-2px);
  background: rgba(240, 248, 255, 0.98);
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
  font-weight: 600;
  color: #1a73e8 !important;
  margin-bottom: 8px;
  line-height: 1.5;
  font-size: 14px !important;
  word-wrap: break-word;
  display: block !important;
  visibility: visible !important;
  opacity: 1 !important;
  height: auto !important;
  max-height: none !important;
  overflow: visible !important;
}

.example-description {
  font-size: 12px !important;
  color: #5f6368 !important;
  line-height: 1.4;
  word-wrap: break-word;
  display: block !important;
  visibility: visible !important;
  opacity: 1 !important;
  height: auto !important;
  max-height: none !important;
  overflow: visible !important;
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
  background: rgba(255, 255, 255, 0.98) !important;
  color: #333 !important;
  overflow: visible !important;
}

.tech-dialog .el-dialog__body * {
  color: inherit !important;
}
</style>