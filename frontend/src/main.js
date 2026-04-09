import { createApp } from 'vue'
import App from './App.vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import axios from 'axios'
import { createPinia } from 'pinia'
import router from './router/index.js'

const app = createApp(App)

axios.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = 'Bearer ' + token
  }
  return config
})

app.use(ElementPlus)
app.use(createPinia())
app.use(router)
app.mount('#app')