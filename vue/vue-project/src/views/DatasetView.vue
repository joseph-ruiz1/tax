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
            <button @click="showForm = !showForm">
                {{ showForm ? 'Cancel' : 'Create New Dataset' }}
            </button>

            <form v-if="showForm" @submit.prevent="createDataset">
                <div>
                    <label>Name:</label>
                    <input v-model="form.name" type="text" required>
                </div>
                <div>
                    <label>Max Elected Farm Income:</label>
                    <input v-model="form.max_elected_farm_income" type="number" step="0.01" required>
                </div>
                <div>
                    <label>Qualified Farm Income:</label>
                    <input v-model="form.qualified_farm_income" type="number" step="0.01" required>
                </div>
                <button type="submit">Create</button>
            </form>
        </div>  
    </div>
</template>

<script setup>
import {ref, onMounted} from 'vue'
import { apiService } from '@/services/api.js'

const loading = ref(true)
const error = ref('')
const datasets = ref([])
const showForm = ref(false)
const form = ref({
    name: '',
    max_elected_farm_income: '',
    qualified_farm_income: '',
})

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
        await apiService.createDataset(form.value)
        showForm.value = false
        form.value = { name: '', max_elected_farm_income: '', qualified_farm_income: ''}
    } catch (err) {
        error.value = 'Failed to create dataset'
    }
}

</script>

<style scoped>

</style>