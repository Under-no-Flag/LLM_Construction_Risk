[file name]: App.vue
[file content begin]
<template>
  <div class="app-container">
    <!-- 顶部导航栏 -->
    <nav class="main-nav">
      <ul class="nav-list">
        <li v-for="(item, index) in navItems" :key="index" class="nav-item">
          <router-link
            :to="item.path"
            class="nav-link"
            active-class="active"
          >
            {{ item.title }}
          </router-link>
        </li>
      </ul>
    </nav>

    <!-- 页面内容 -->
    <main class="content-area">
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </main>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const navItems = ref([
  { title: '首页', path: '/' },  // 新增首页导航项
  { title: '知识图谱管理', path: '/kg-management' },
  { title: '安全风险与隐患识别', path: '/risk-identification' },
  { title: '风险管控与隐患治理', path: '/hazard-control' },
  { title: '历史溯源与反馈', path: '/history-tracking' }
])
</script>

  <style scoped>
  .app-container {
    height: 100vh;
    display: flex;
    flex-direction: column;
  }

  .main-nav {
    background: #2c3e50;
    padding: 1rem 2rem;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    position: sticky;
    top: 0;
    z-index: 1000;
  }

  .nav-list {
    display: flex;
    list-style: none;
    padding: 0;
    margin: 0;
    gap: 2rem;
  }

  .nav-item {
    display: flex;
    align-items: center;
  }

  .nav-link {
    color: #ecf0f1;
    text-decoration: none;
    padding: 0.5rem 1rem;
    border-radius: 4px;
    transition: all 0.3s ease;
  }

  .nav-link:hover {
    background: rgba(255, 255, 255, 0.1);
  }

  .nav-link.active {
    background: #3498db;
    color: white;
  }

  .content-area {
    flex: 1;
    padding: 2rem;
    overflow-y: auto;
    background-color: #f5f6fa;
  }

  /* 页面切换动画 */
  .fade-enter-active,
  .fade-leave-active {
    transition: opacity 0.3s ease;
  }

  .fade-enter-from,
  .fade-leave-to {
    opacity: 0;
  }
  </style>