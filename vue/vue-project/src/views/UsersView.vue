<!-- views/UsersView.vue -->
<template>
    <div>
        <h2>Users:</h2>

        <div v-if="loading">Loading users...</div>

        <div v-else-if="error" class="error">{{ error }}</div>

        <div v-else>
            {{ user.username }}
        </div>
    </div>
</template>

<script setup>
    import {ref, onMounted } from 'vue'
    import { apiService } from '@/services/api.js'

    const user = ref([])
    const loading = ref(true)
    const error = ref('')
    const authenticated = ref(false)
        
   onMounted(async () => {
    await fetchUsers()
   })

    const fetchUsers = async () => {
        try {
            const data = await apiService.getUsers()
            user.value = data.users || data // adjust based on API
        } catch (err) {
            error.value = 'Failed to fetch users'
        } finally {
            loading.value = false
        }
    }
</script>