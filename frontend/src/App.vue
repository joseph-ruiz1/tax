<!-- App.vue -->
<template>
  <main id="app">
    <!-- Show loading while checking authentication -->
    <div v-if="loading" class="loading-container">
      <div>Loading...</div>
    </div>
    
    <!-- Show error if auth check failed -->
    <div v-else-if="error" class="error-container">
      <div>{{ error }}</div>
    </div>
    
    <!-- Show app once auth is verified -->
    <router-view v-else />
  </main>
</template>

<script setup>
// check auth
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { apiService } from './services/api'

const router = useRouter()
const loading = ref(true)
const error = ref('')
const user = ref(null)

onMounted(async () => {
  await checkAuth()
})

const checkAuth = async () => {
 try {
  const response = await apiService.checkAuth()

  if (response.authenticated) {
    user.value = response.user
    // authenticated
  } else {
    // Not authenticated, go to login
    router.push('/login')
  }
 } catch (err) {
  console.error('Authentication error', err)
  error.value = 'Authentication failed'
 } finally {
  loading.value = false
 }
}
</script>

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
