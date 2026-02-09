<!-- App.vue -->
<template>
  <main id="app">
    <div v-if="loading" class="loading-container">
      <div>Loading...</div>
    </div>
    
    <div v-else-if="error" class="error-container">
      <div>{{ error }}</div>
    </div>
    
    <router-view v-else />
  </main>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { apiService } from './services/api'

const router = useRouter()
const route = useRoute()
const loading = ref(true)
const error = ref('')
const user = ref(null)

const publicRoutes = ['/login', '/register']

onMounted(async () => {
  await checkAuth()
})

const checkAuth = async () => {
  try {
    if (publicRoutes.includes(route.path)) {
      loading.value = false
      return
    }

    const response = await apiService.checkAuth()

    if (response.authenticated) {
      user.value = response.user
    } else {
      if (!publicRoutes.includes(route.path)) {
        router.push('/login')
      }
    }
  } catch (err) {
    console.error('Authentication error', err)
    if (!publicRoutes.includes(route.path)) {
      router.push('/login')
    }
    error.value = ''
  } finally {
    loading.value = false
  }
}
</script>

<style>
.loading-container,
.error-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  font-size: 1.2rem;
}

.error-container {
  color: #d32f2f;
}
</style>

<style>
#app {
  flex: 1;
  width: 100%;
  min-height: 100vh;
}

.loading-container {
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 18px;
}

.error-container {
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 18px;
  color: #ef4444;
}
</style>
