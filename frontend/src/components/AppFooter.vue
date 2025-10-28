<template>
  <footer class="app-footer">
    <div class="footer-content">
      <!-- 单行布局：GitHub + 头像 + 版权信息 -->
      <div class="footer-inline">
        <!-- GitHub链接 -->
        <a 
          href="https://github.com/SinzoL" 
          target="_blank" 
          rel="noopener noreferrer"
          class="github-link"
          @click="handleGitHubClick"
        >
          <svg class="github-icon" viewBox="0 0 24 24" fill="currentColor">
            <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
          </svg>
          <span>GitHub</span>
        </a>

        <!-- 分隔符 -->
        <span class="separator">•</span>

        <!-- 开发者头像和姓名 -->
        <div class="developer-info">
          <img 
            :src="avatarUrl" 
            alt="SinzoL Avatar" 
            class="developer-avatar"
            @error="handleAvatarError"
          />
          <span class="developer-name">SinzoL</span>
        </div>

        <!-- 分隔符 -->
        <span class="separator">•</span>

        <!-- 版权信息 -->
        <div class="copyright">
          © {{ currentYear }} Using Vue.js & FastAPI
        </div>
      </div>
    </div>
  </footer>
</template>

<script>
export default {
  name: 'AppFooter',
  data() {
    return {
      avatarUrl: '/SinzoL.png',
      currentYear: new Date().getFullYear()
    }
  },
  methods: {
    handleGitHubClick() {
      console.log('🔗 访问GitHub: https://github.com/SinzoL')
    },
    handleAvatarError() {
      console.warn('⚠️ 头像加载失败，使用默认头像')
      this.avatarUrl = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNDAiIGhlaWdodD0iNDAiIHZpZXdCb3g9IjAgMCA0MCA0MCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPGNpcmNsZSBjeD0iMjAiIGN5PSIyMCIgcj0iMjAiIGZpbGw9IiM2MzY2ZjEiLz4KPHN2ZyB4PSI4IiB5PSI4IiB3aWR0aD0iMjQiIGhlaWdodD0iMjQiIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0id2hpdGUiPgo8cGF0aCBkPSJNMTIgMTJjMi4yMSAwIDQtMS43OSA0LTRzLTEuNzktNC00LTQtNCAxLjc5LTQgNCAxLjc5IDQgNCA0em0wIDJjLTIuNjcgMC04IDEuMzQtOCA0djJoMTZ2LTJjMC0yLjY2LTUuMzMtNC04LTR6Ii8+Cjwvc3ZnPgo8L3N2Zz4K'
    }
  }
}
</script>

<style scoped>
.app-footer {
  background: #6c757d;
  padding: 24px 0 16px;
  margin-top: auto;
  box-shadow: 0 -4px 20px rgba(0, 0, 0, 0.1);
}

.footer-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 24px;
  display: flex;
  justify-content: center;
  align-items: center;
}

/* 单行布局容器 */
.footer-inline {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 16px 24px;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-radius: 50px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

/* GitHub链接 */
.github-link {
  display: flex;
  align-items: center;
  gap: 8px;
  color: white;
  text-decoration: none;
  padding: 8px 12px;
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.15);
  transition: all 0.3s ease;
  font-size: 14px;
}

.github-link:hover {
  background: rgba(255, 255, 255, 0.25);
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

.github-icon {
  width: 18px;
  height: 18px;
}

/* 分隔符 */
.separator {
  color: rgba(255, 255, 255, 0.5);
  font-size: 16px;
  font-weight: bold;
}

/* 开发者信息 */
.developer-info {
  display: flex;
  align-items: center;
  gap: 10px;
}

.developer-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  border: 2px solid rgba(255, 255, 255, 0.3);
  object-fit: cover;
  transition: all 0.3s ease;
}

.developer-avatar:hover {
  transform: scale(1.1);
  border-color: rgba(255, 255, 255, 0.6);
}

.developer-name {
  font-size: 14px;
  font-weight: 600;
  color: #ffffff;
}

/* 版权信息 */
.copyright {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.8);
  margin: 0;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .footer-inline {
    flex-direction: column;
    gap: 12px;
    padding: 16px 20px;
    border-radius: 20px;
  }

  .separator {
    display: none;
  }

  .github-link,
  .developer-info,
  .copyright {
    font-size: 13px;
  }
}

@media (max-width: 480px) {
  .app-footer {
    padding: 16px 0 12px;
  }

  .footer-content {
    padding: 0 16px;
  }

  .footer-inline {
    padding: 12px 16px;
    gap: 10px;
  }

  .developer-avatar {
    width: 28px;
    height: 28px;
  }

  .github-icon {
    width: 16px;
    height: 16px;
  }

  .copyright {
    font-size: 12px;
  }
}

/* 深色模式适配 */
@media (prefers-color-scheme: dark) {
  .app-footer {
    background: #4a5568;
  }
}

/* 动画效果 */
.app-footer {
  animation: slideUp 0.5s ease-out;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>