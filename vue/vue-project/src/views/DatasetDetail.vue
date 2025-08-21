<!-- DatasetDetail.vue -->
 <template>
    <div>
        <h2>Details:</h2>

        <div v-if="loading">Loading datasets...</div>

        <div v-else-if="error" class="error">{{ error }}</div>

        <div v-else>
            
            {{ dataset }}
        </div>
    </div>

 </template>


<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { apiService } from '@/services/api.js'

const loading = ref(false)
const error = ref('')
const route = useRoute()
const dataset = ref(null)

onMounted(async () => {
  const id = route.params.id
  const data = await apiService.getDatasetDetail(id) // New API method needed
  dataset.value = data
})
</script>