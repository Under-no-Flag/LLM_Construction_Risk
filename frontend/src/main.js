import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
// import VueCytoscape from 'vue-cytoscape'   // ← ① 引入组件（或插件）

const app = createApp(App)
app.use(router)
// app.use(VueCytoscape)

app.mount('#app')