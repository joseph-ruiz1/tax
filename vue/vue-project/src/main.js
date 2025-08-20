import './assets/main.css'

import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import axios from 'axios'

axios.defaults.baseURL = 'http://localhost:8000/tax/api/'
axios.defaults.withCredentials = true

createApp(App).use(router).mount('#app')

