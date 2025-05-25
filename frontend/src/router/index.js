import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  // 新增主页路由
  {
    path: '/',
    name: 'Home',
    component: () => import('@/Home.vue') // 使用懒加载
  },
  // 保留原有路由配置
  {
    path: '/kg-management',
    name: 'KGManagement',
    component: () => import('@/components/KG2.vue')
  },
  {
    path: '/risk-identification',
    name: 'RiskIdentification',
    component: () => import('@/components/RiskIdentify.vue')
  },
  {
    path: '/hazard-control',
    component: () => import('@/components/SecurityIssueProcess.vue') //
  },
  {
    path: '/hazards/:id/process',
    name: 'hazard-process',
    component: () => import('@/components/HazardDetails.vue'), //
    props: true,
  },
  {
    path:'/history-tracking',
    component: () => import('@/components/HistoryFeedback.vue'), //
  }
  // 补充缺失的两个路由
  // {
  //   path: '/hazard-control',
  //   name: 'HazardControl',
  //   component: () => import('@/components/HazardControl.vue')
  // },
  // {
  //   path: '/history-tracking',
  //   name: 'HistoryTracking',
  //   component: () => import('@/components/HistoryTracking.vue')
  // }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router