<!-- DatasetView.vue -->
<template>
    <div>
        <h2>Datasets:</h2>

        <div v-if="loading">Loading datasets...</div>

        <div v-else-if="error" class="error">{{ error }}</div>

        <div v-else>
            <li v-for="dataset in datasets" :key="dataset.id">
                <router-link :to="`/datasets/${dataset.id}`">
                    {{ dataset.id }}
                 </router-link>
            </li>
        </div>

        
        <div>
            <form @submit.prevent="createDataset">
                <button type="submit">Create</button>
            </form>
        </div>  
    </div>
</template>

<script setup>
import {ref, onMounted} from 'vue'
import { apiService } from '@/services/api.js'
import { useRouter } from 'vue-router'

const router = useRouter()
const loading = ref(true)
const error = ref('')
const datasets = ref([])
const form = ref({})

onMounted(async () => {
    await fetchDatasets ()
})

const fetchDatasets = async () => {
    try {
        const data = await apiService.getDatasetList()
        datasets.value = data
    } catch (err) {
        error.value = 'Failed to fetch datsets'
    } finally {
        loading.value = false
    }
}

const createDataset = async () => {
    try {
        const response = await apiService.createDataset(form.value)
        router.push(`/datasets/${response.id}/new`)
    } catch (err) {
        error.value = 'Failed to create dataset'
    }
}

</script>

<style scoped>

</style>