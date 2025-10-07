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

// 初始化网络监控
console.log('🌐 初始化网络监控器...')
networkMonitor.addListener((event) => {
  if (event.type === 'offline') {
    console.warn('⚠️ 网络连接已断开')
  } else if (event.type === 'online') {
    console.log('✅ 网络连接已恢复')
  } else if (event.type === 'quality-update') {
    console.log(`📊 网络质量: ${event.quality} (${Math.round(event.latency)}ms)`)
  }
})

app.mount('#app')