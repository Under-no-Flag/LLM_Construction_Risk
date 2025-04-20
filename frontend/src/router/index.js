
import { createRouter, createWebHistory } from 'vue-router'

// 确保所有页面组件已正确导入
const routes = [
  {
    path: '/',
    redirect: '/kg-management'
  },
  {
    path: '/kg-management',
    component: () => import('@/components/KGManage.vue') // 推荐使用懒加载
  },
  {
    path: '/risk-identification',
    component: () => import('@/components/RiskIdentify.vue') //
  }
  // 其他路由配置保持相同结构
]

const router = createRouter({
    history: createWebHistory(),
    routes
  })

  export default router