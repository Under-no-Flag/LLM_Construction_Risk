<template>
  <div class="home">
    <div class="dashboard">
      <h1>建筑施工安全风险管控与隐患治理系统</h1>
      <div class="modules-grid">
        <router-link 
          v-for="(module, index) in modules" 
          :key="index" 
          :to="module.path"
          class="module-card"
        >
          <div class="card-icon">
            <span class="icon">{{ module.icon }}</span>
          </div>
          <h3>{{ module.title }}</h3>
          <p>{{ module.description }}</p>
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
const modules = [
  {
    title: '知识图谱管理',
    path: '/kg-management',
    icon: '📚',
    description: '构建和管理建筑施工安全知识图谱'
  },
  {
    title: '安全风险与隐患识别',
    path: '/risk-identification',
    icon: '⚠️',
    description: '实时识别施工安全风险与隐患'
  },
  {
    title: '风险管控与隐患治理',
    path: '/hazard-control',
    icon: '🔧',
    description: '跟踪处理施工安全风险与安全隐患'
  },
  {
    title: '历史溯源与反馈',
    path: '/history-tracking',
    icon: '🕰️',
    description: '追溯风险管控与隐患治理历史记录'
  }
]
</script>

<style scoped>
.home {
  padding: 2rem;
}

.dashboard {
  max-width: 1200px;
  margin: 0 auto;
}

h1 {
  text-align: center;
  color: #2c3e50;
  margin-bottom: 2rem;
}

.modules-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr); /* 两列布局 */
  gap: 2rem;
  padding: 1rem;
}

.module-card {
  background: white;
  border-radius: 12px;
  padding: 2rem;
  text-align: center;
  text-decoration: none;
  color: #2c3e50;
  transition: transform 0.2s, box-shadow 0.2s;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

/* 以下样式保持不变 */
.module-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
}

.card-icon {
  font-size: 3.5rem;
  margin-bottom: 1rem;
}

.module-card h3 {
  margin: 1rem 0;
  color: #3498db;
}

.module-card p {
  color: #7f8c8d;
  font-size: 0.9rem;
  line-height: 1.5;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .modules-grid {
    grid-template-columns: 1fr; /* 手机端单列显示 */
  }
  
  .dashboard {
    padding: 1rem;
  }
  
  h1 {
    font-size: 1.5rem;
  }
}
</style>