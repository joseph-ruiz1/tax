<!-- views/UsersView.vue -->
<template>
    <div>
        <h2>Users:</h2>

        <div v-if="!authenticated">
            <p>Please log in to view</p>
            <router-link to="/login">Go to Login</router-link>
        </div>
        <div v-else-if="loading">Loading users...</div>

        <div v-else-if="error" class="error">{{ error }}</div>

        <div v-else>
            <div v-for="user in users" :key="user.id">
                <h3>{{ user.username }}</h3>
            </div>
        </div>
    </div>
</template>

<script setup>
    import {ref, onMounted } from 'vue'
    import { apiService } from '@/services/api.js'

    const users = ref([])
    const loading = ref(true)
    const error = ref('')
    const authenticated = ref(false)
        
   onMounted(async () => {
      // Check if user is authenticated first
      try {
        const authData = await apiService.checkAuth()
        authenticated.value = authData.authenticated

        if (authenticated.value) {
            await fetchUsers()
        }
      } catch (err) {
        error.value = 'Failed authentication'
      } finally {
        loading.value = false
      }
    })

    const fetchUsers = async () => {
        try {
            const data = await apiService.getUsers()
            users.value = data.users || data // adjust based on API
        } catch (err) {
            if (err.response?.status === 403) {
                error.value = 'Please log in to view'
                authenticated.value = false
            } else {
                error.value = 'Failed to fetch users'
            }
        }
    }
</script>