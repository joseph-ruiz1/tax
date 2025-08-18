<!-- src/views/LoginView.vue -->
<template>
  <div class="login-container">
    <h2>Login</h2>

    <div v-if="isAuthenticated">
      <h3>Welcome, {{ user.username }}</h3>
      <p>You're logged in</p>
      <button @click="handleLogout" class="logout-btn">Logout</button>
    </div>

    <div v-else>
      <div @submit.prevent="handleLogin">
        <div class="form-group">
         <label>username:</label>
         <input
         v-model="username"
         type="text"
         required
         :disabled="loading"
         />
        </div>
        
        <div class="form-group">
          <label>password:</label>
          <input
          v-model="password"
          type="text"
          required
          :disabled="loading"
          />
        </div>

        <button
        type="submit"
        :disabled="loading"
        @click="handleLogin"
        class="login-btn"
        >
      {{ loading ? 'Logging in...' : 'Login' }}
      </button>

        <div v-if="error" class="error">
          {{ error }}
        </div>
    </div>
   </div>

   <div class="api-info">
    <h3>DRF ViewSet Endponits:</h3>
    <ul>
      <li><code>POST /api/auth/login/</code> - Login with session</li>
      <li><code>POST /api/auth/logout/</code> - Logout</li>
      <li><code>GET /api/auth/check/</code> - Check auth status</li>
      <li><code>GET /api/users/</code> - List users (authenticated)</li>
    </ul>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '@/composables/useAuth.js'

const router = useRouter()
const { user, isAuthenticated, loading, error, login, logout, checkAuth } = useAuth()

const username = ref('')
const password = ref('')

onMounted(() => {
  checkAuth()
})

const handleLogin = async () => {
  const success = await login(username.value, password.value)
  if (success) {
    // redirect
    // router.push('/page')
  }
}

const handleLogout = async () => {
  await logout(),
  username.value = ''
  password.value = ''
}
</script>

<style scoped>
.login-container {
  max-width: 400px;
  margin: 2rem auto;
  padding: 2rem;
  border: 1px solid #ddd;
  border-radius: 8px;
}

.login-container div {
  margin-bottom: 1rem;
}

.login-container label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: bold;
}

.login-container input {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #ccc;
  border-radius: 4px;
}

.login-container button {
  width: 100%;
  padding: 0.75rem;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.login-container button:disabled {
  background-color: #6c757d;
  cursor: not-allowed;
}

.error {
  color: #dc3545;
  background-color: #f8d7da;
  padding: 0.5rem;
  border-radius: 4px;
  border: 1px solid #f5c6cb;
}
</style>