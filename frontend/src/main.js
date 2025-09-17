import './assets/main.css'

import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import axios from 'axios'
import VueApexCharts from "vue3-apexcharts";

const getApiUrl = () => {
  // Check if we have an explicit env var first
  if (import.meta.env.VITE_API_URL) {
    return import.meta.env.VITE_API_URL;
  }
  
  // Fallback to automatic detection
  if (import.meta.env.PROD) {
    return 'https://tax-khxl.onrender.com/api/';
  } else {
    return 'http://localhost:8000/api';
  }
};

axios.defaults.baseURL = getApiUrl();

axios.defaults.baseURL = import.meta.env.VITE_API_URL;
axios.defaults.withCredentials = true;
axios.defaults.withXSRFToken = true;
axios.defaults.xsrfCookieName = 'csrftoken';
axios.defaults.xsrfHeaderName = 'X-CSRFTOKEN';



createApp(App).use(router).use(VueApexCharts).mount('#app')

