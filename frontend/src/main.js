import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import App from './App.vue'
import router from './router'
import { networkMonitor } from './utils/networkMonitor'

const app = createApp(App)

// 注册所有图标
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

app.use(createPinia())
app.use(router)
app.use(ElementPlus)

// 初始化网络监控 - 优化日志输出
console.log('🌐 网络监控器已启动')
networkMonitor.addListener((event) => {
  if (event.type === 'offline') {
    console.warn('⚠️ 网络连接已断开')
  } else if (event.type === 'online') {
    console.log('✅ 网络连接已恢复')
  } else if (event.type === 'quality-update' && event.quality !== 'unknown') {
    // 只在有明确质量评估时输出，避免unknown状态的噪音
    if (event.latency !== Infinity) {
      console.log(`📊 网络质量: ${event.quality} (${Math.round(event.latency)}ms)`)
    }
  }
})

app.mount('#app')