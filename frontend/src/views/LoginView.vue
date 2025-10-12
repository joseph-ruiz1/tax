<template>
  <div class="auth-container">
    <div class="auth-card">
      <div class="auth-header">
        <h1>Schedule J Optimizer</h1>
      </div>

      <div class="auth-tabs">
        <button 
          class="auth-tab" 
          :class="{ active: currentTab === 'login' }" 
          @click="switchTab('login')"
        >
          Login
        </button>
        <button 
          class="auth-tab" 
          :class="{ active: currentTab === 'register' }" 
          @click="switchTab('register')"
        >
          Register
        </button>
      </div>

      <div v-if="successMessage" class="success-message">
        {{ successMessage }}
      </div>

      <!-- Login Form -->
      <form v-if="currentTab === 'login'" @submit.prevent="handleLogin" class="auth-form">
        <div class="form-group">
          <label class="form-label" for="login-username">Username</label>
          <input 
            v-model="loginForm.username"
            type="text" 
            id="login-username" 
            class="form-input"
            :class="{ error: errors.username }"
            required
            autocomplete="username"
          >
          <div v-if="errors.username" class="error-message">{{ errors.username }}</div>
        </div>

        <div class="form-group">
          <label class="form-label" for="login-password">Password</label>
          <input 
            v-model="loginForm.password"
            type="password" 
            id="login-password" 
            class="form-input"
            :class="{ error: errors.password }"
            required
            autocomplete="current-password"
          >
          <div v-if="errors.password" class="error-message">{{ errors.password }}</div>
        </div>

        <button type="submit" class="submit-btn" :disabled="loading">
          <span v-if="loading" class="loading"></span>
          <span>{{ loading ? 'Signing In...' : 'Sign In' }}</span>
        </button>
      </form>

      <!-- Register Form -->
      <form v-if="currentTab === 'register'" @submit.prevent="handleRegister" class="auth-form">
        <div class="form-group">
          <label class="form-label" for="register-username">Username</label>
          <input 
            v-model="registerForm.username"
            type="text" 
            id="register-username" 
            class="form-input"
            :class="{ error: errors.username }"
            required
            autocomplete="username"
          >
          <div v-if="errors.username" class="error-message">{{ errors.username }}</div>
        </div>

        <div class="form-group">
          <label class="form-label" for="register-password">Password</label>
          <input 
            v-model="registerForm.password"
            type="password" 
            id="register-password" 
            class="form-input"
            :class="{ error: errors.password }"
            required
            autocomplete="new-password"
            minlength="4"
          >
          <div v-if="errors.password" class="error-message">{{ errors.password }}</div>
        </div>

        <div class="form-group">
          <label class="form-label" for="register-password-confirm">Confirm Password</label>
          <input 
            v-model="registerForm.password_confirm"
            type="password" 
            id="register-password-confirm" 
            class="form-input"
            :class="{ error: errors.password_confirm }"
            required
            autocomplete="new-password"
          >
          <div v-if="errors.password_confirm" class="error-message">{{ errors.password_confirm }}</div>
        </div>

        <button type="submit" class="submit-btn" :disabled="loading">
          <span v-if="loading" class="loading"></span>
          <span>{{ loading ? 'Creating Account...' : 'Create Account' }}</span>
        </button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { apiService } from '@/services/api.js'

const router = useRouter()
const currentTab = ref('login')
const loading = ref(false)
const successMessage = ref('')
const errors = ref({})

const loginForm = reactive({
  username: '',
  password: ''
})

const registerForm = reactive({
  username: '',
  password: '',
  password_confirm: ''
})

const switchTab = (tab) => {
  currentTab.value = tab
  clearErrors()
  clearSuccessMessage()
}

const clearErrors = () => {
  errors.value = {}
}

const clearSuccessMessage = () => {
  successMessage.value = ''
}

const showError = (field, message) => {
  errors.value[field] = message
}

const handleLogin = async () => {
  clearErrors()
  loading.value = true
  try {
    const response = await apiService.login(loginForm)
    if (response.success) {
      successMessage.value = 'Login successful. Redirecting...'
      router.push('/')
    }
  } catch (error) {
    console.error('Login error:', error)
    // Handle server errors
    if (error.response && error.response.status >= 500) {
      showError('username', 'Server error. Please try again later.')
    } else if (error.response && error.response.status >= 400) {
      showError('username', 'Invalid credentials. Please try again.')
    } else {
      showError('username', 'Please check your connection and try again.')
    }
  } finally {
    loading.value = false
  }
}

const handleRegister = async () => {
  clearErrors()

  if (registerForm.password !== registerForm.password_confirm) {
    showError('password_confirm', 'Passwords do not match')
    return
  }

  if (registerForm.password.length < 4) {
    showError('password', 'Password must be at least 4 characters long')
    return
  }

  loading.value = true

    try {
      const response = await apiService.register(registerForm)
      
      if (response.success) {
        successMessage.value = 'Account created successfully! Redirecting...'
        router.push('/')
      }
    } catch (error) {
      console.error('Registration error:', error)
      if (error.response && error.response.data) {
        const data = error.response.data

        if (data.errors) {
          Object.keys(data.errors).forEach(field => {
          if (field === 'non_field_errors') {
            showError('password_confirm', data.errors[field][0])
          } else {
            const errorMsg = Array.isArray(data.errors[field]) 
              ? data.errors[field][0] 
              : data.errors[field]
            showError(field, errorMsg)
          }
        })
        } else {
          showError('username', 'Registration failed. Please try again.')
        } 
      } else {
      // Generic error fallback for network issues
      showError('username', 'Registration failed. Please try again.')
      }
    } finally {
      loading.value = false
    }
  }
</script>

<style scoped>
.auth-container {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  background: linear-gradient(135deg, #434b6f 0%, #2e2735 100%);
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
}

.auth-card {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  padding: 3rem;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  width: 100%;
  max-width: 450px;
}

.auth-header {
  text-align: center;
  margin-bottom: 2rem;
}

.auth-header h1 {
  color: #1a202c;
  font-size: 2rem;
  font-weight: 700;
  margin-bottom: 0.5rem;
}

.auth-header p {
  color: #718096;
  font-size: 1rem;
}

.auth-tabs {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 2rem;
  background: rgba(255, 255, 255, 0.5);
  padding: 0.5rem;
  border-radius: 12px;
}

.auth-tab {
  flex: 1;
  padding: 0.75rem 1.5rem;
  background: transparent;
  border: none;
  border-radius: 8px;
  color: #718096;
  font-weight: 600;
  font-size: 0.95rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.auth-tab.active {
  background: white;
  color: #4c51bf;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.auth-form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-label {
  color: #1a202c;
  font-weight: 600;
  font-size: 0.9rem;
}

.form-input {
  padding: 0.75rem 1.25rem;
  border: 2px solid #e2e8f0;
  border-radius: 12px;
  font-size: 1rem;
  background: white;
  color: #1a202c;
  transition: all 0.3s ease;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.form-input:focus {
  outline: none;
  border-color: #4c51bf;
  box-shadow: 0 0 0 3px rgba(76, 81, 191, 0.1);
  transform: translateY(-1px);
}

.form-input.error {
  border-color: #e53e3e;
  box-shadow: 0 0 0 3px rgba(229, 62, 62, 0.1);
}

.error-message {
  color: #e53e3e;
  font-size: 0.85rem;
}

.success-message {
  background: rgba(72, 187, 120, 0.1);
  border: 1px solid rgba(72, 187, 120, 0.3);
  color: #38a169;
  padding: 0.75rem 1rem;
  border-radius: 8px;
  font-size: 0.9rem;
  margin-bottom: 1rem;
}

.submit-btn {
  background: linear-gradient(135deg, #48bb78 0%, #38a169 100%);
  color: white;
  padding: 1rem 2rem;
  border-radius: 12px;
  border: none;
  font-weight: 700;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(72, 187, 120, 0.4);
  margin-top: 1rem;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.submit-btn:hover {
  transform: translateY(-3px);
  box-shadow: 0 6px 20px rgba(72, 187, 120, 0.5);
}

.submit-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
  box-shadow: 0 4px 15px rgba(72, 187, 120, 0.4);
}

.loading {
  display: inline-block;
  width: 20px;
  height: 20px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  border-top-color: white;
  animation: spin 1s ease-in-out infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

@media (max-width: 768px) {
  .auth-card {
    padding: 2rem 1.5rem;
    margin: 1rem;
  }

  .auth-header h1 {
    font-size: 1.75rem;
  }
}
</style>