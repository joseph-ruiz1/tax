import { ref, computed } from 'vue'
import { apiService } from '@/services/api.js'

const user = ref(null)
const loading = ref(false)
const error = ref('')

export function useAuth() {
    const isAuthenticated = computed(() => !!user.value)

    const login = async (username, password) => {
        loading.value = true
        error.value = ''

        try {
            const response = await apiService.login(username, password)
            if (response.success) {
                user.value = response
                return true
            }
        } catch (err) {
            
            'Login failed'
            return false
        } finally {
            loading.value = false
        }
    }

    const logout = async () => {
        try {
            await apiService.logout()
            user.value = null
        } catch (err) {
            console.error('Logout error', err)
        }
    }

    const checkAuth = async () => {
        try {
            const response = await apiService.checkAuth()
            if (response.authenticated) {
                user.value = response.user
            } 
        } catch (err) {
            console.error('Authentication error', err)
            user.value = null
        }
    }
    return {
        user: computed(() => user.value),
        isAuthenticated,
        loading: computed(() => loading.value),
        error: computed(() => error.value),
        login,
        logout,
        checkAuth
    }
}