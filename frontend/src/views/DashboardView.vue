<!-- DatasetView.vue -->
<template>
    <div class="dashboard-container">
        <!-- Header -->
        <div class="dashboard-header">
            <div class="dashboard-title">
                <h1>Welcome back, {{ user?.username || 'user' }}</h1>
                <div class="user-menu">
                    <button class="logout-btn" @click="handleLogout">Logout</button>
                </div>
            </div>
        </div>

    <!-- Quick Actions -->
    <div class="quick-actions">
      <h2>Quick Actions</h2>
      <div class="actions-grid">
        <button class="action-btn success" @click="createNewDataset">
          <div class="action-text">
            <h3>New Tax Calculation</h3>
          </div>
        </button>
        <button 
        v-if="lastDataset"
        class="action-btn" 
        @click="navigateToDataset(lastDataset.id)">
          <div class="action-text">
            <h3>Jump to most recently created dataset</h3>
            <h4>{{ lastDataset.name }} - {{ lastDataset.max_elected_farm_income }}</h4>
          </div>
        </button>
      </div>
    </div>

    <!-- Recent Datasets -->
    <div class="datasets-section">
      <div class="section-header">
        <h2>Recent Datasets</h2>
        <button
        v-if="hasMoreDatasets"
        @click="toggleShowAll"
        class="view-all-btn">
          {{ showAllDatasets ? 'Show less': `Show all (${datasets.length})` }}
        </button>
      </div>
      
      <div v-if="loading" class="loading-state">
        Loading datasets...
      </div>
      
      <div v-else-if="error" class="error-state">
        {{ error }}
      </div>

      <div v-else-if="datasets.length === 0" class="empty-state">
        <h3>No datasets yet</h3>
        <p>Create your first dataset</p>
        <button class="action-btn success" @click="createNewDataset">
          <div class="action-icon">➕</div>
          <div class="action-text">
            <h4>Create Dataset</h4>
            <p>Start your first calculation</p>
          </div>
        </button>
      </div>

      <div v-else class="dataset-grid">
        <div
        v-for="dataset in displayedDatasets"
        :key="dataset.id"
        class="dataset-card"
        @click="navigateToDataset(dataset.id)"
        >
        <h3>{{ dataset.name }}</h3> 
        <div class="dataset-meta">
            <span>Created {{ formatDate(dataset.created_at) }}</span>
            <button 
            @click.stop="deleteDataset(dataset.id)" 
            class="dataset-delete" 
            title="Delete">
                x
            </button>
          </div> 
        </div>
      </div>
    </div>
  </div>

</template>

<script setup>
import {ref, onMounted, computed} from 'vue'
import { apiService } from '@/services/api.js'
import { useRouter } from 'vue-router'

const router = useRouter()
const loading = ref(true)
const error = ref('')
const datasets = ref([])
const form = ref('')
const user = ref(null)
const showAllDatasets = ref(false)

const displayedDatasets = computed(() => {
    if (showAllDatasets.value) {
        return datasets.value
    }
  return datasets.value.slice(-6)
})

const lastDataset = computed(() => {
  const datasets = displayedDatasets.value
  return datasets.length > 0 ? datasets[datasets.length - 1] : null
})

const hasMoreDatasets = computed(() => {
    return datasets.value.length > 5
})

const toggleShowAll = () => {
    showAllDatasets.value = !showAllDatasets.value
}

const handleLogout = async () => {
    try {
        await apiService.logout()
        router.push('/login')
    } catch (err) {
        console.error('Logout error:', err)
        router.push('/login')
    }
}

const fetchUser = async () => {
    try {
        const userData = await apiService.getCurrentUser()
        user.value = userData
    } catch (err) {
        console.error('Failed to fetch user:', err)
    }
}

const fetchDatasets = async () => {
    try {
        const data = await apiService.getDatasetList()
        datasets.value = data
    } catch (err) {
        error.value = 'Failed to fetch datsets'
        console.error('Error fetching dataset:', err)
    } finally {
        loading.value = false
    }
}

const createNewDataset = async () => {
    try {
        const response = await apiService.createDataset(form.value)
        router.push(`/datasets/${response.dataset_id}/new`)
    } catch (err) {
        error.value = 'Failed to create dataset'
        console.error('Error creating dataset:', err)
    }
}

const deleteDataset = async (id) => {
   if (!confirm('Are you sure you want to delete this dataset?')) {
    return
  }
    try {
        await apiService.deleteDataset(id)
        datasets.value = datasets.value.filter(d => d.id !== id)
    } catch (err) {
        error.value = 'Failed to delete dataset'
        console.log('Error delting dataset', err)
    }
}

const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

const navigateToDataset = async (id) => {
  try {
    const response = await apiService.getResults(id)
    router.push(`/datasets/${id}/results`)
  } catch (err) {
    error.value = 'Failed to load results'
    console.log('Error loading results', err)
  }
}

onMounted(async () => {
    await Promise.all([
        fetchUser(),
        fetchDatasets()
    ])
})

</script>

<style scoped>
.dashboard-container {
  margin: 0 auto;
  padding: 2rem;
  background: linear-gradient(135deg, #434b6f 0%, #2e2735 100%);
  min-height: 20vh;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

/* Header */
.dashboard-header {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  padding: 2rem;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  margin-bottom: 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.dashboard-title h1 {
  color: #1a202c;
  font-size: 2rem;
  font-weight: 700;
  margin-bottom: 0.5rem;
}

.dashboard-title p {
  color: #718096;
  font-size: 1rem;
}

.user-menu {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.user-info {
  text-align: right;
}

.user-info h3 {
  color: #1a202c;
  font-weight: 600;
  font-size: 1rem;
}

.user-info p {
  color: #718096;
  font-size: 0.85rem;
}

.logout-btn {
  background: rgba(229, 62, 62, 0.1);
  border: 1px solid rgba(229, 62, 62, 0.3);
  color: #e53e3e;
  padding: 0.5rem 1rem;
  border-radius: 8px;
  font-weight: 600;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.logout-btn:hover {
  background: rgba(229, 62, 62, 0.2);
  transform: translateY(-1px);
}

/* Quick Actions */
.quick-actions {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  padding: 2rem;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  margin-bottom: 2rem;
}

.quick-actions h2 {
  color: #1a202c;
  font-size: 1.5rem;
  font-weight: 700;
  margin-bottom: 1rem;
}

.actions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1rem;
}

.action-btn {
  background: linear-gradient(135deg, #4c51bf 0%, #667eea 100%);
  color: white;
  padding: 1.25rem;
  border-radius: 12px;
  border: none;
  font-weight: 600;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(76, 81, 191, 0.4);
  text-align: left;
  display: flex;
  align-items: center;
  gap: 1rem;
  text-decoration: none;
}

.action-btn:hover {
  transform: translateY(-3px);
  box-shadow: 0 6px 20px rgba(76, 81, 191, 0.5);
}

.action-btn.success {
  background: linear-gradient(135deg, #48bb78 0%, #38a169 100%);
  box-shadow: 0 4px 15px rgba(72, 187, 120, 0.4);
}

.action-btn.success:hover {
  box-shadow: 0 6px 20px rgba(72, 187, 120, 0.5);
}

.action-icon {
  font-size: 1.5rem;
}

.action-text {
  flex: 1;
}

.action-text h3 {
  font-size: 1rem;
  font-weight: 600;
  margin-bottom: 0.25rem;
}

.action-text h4 {
  font-size: 1rem;
  font-weight: 200;
  margin-bottom: 0.25rem;
  color: rgb(184, 182, 182);
}

.action-text p {
  font-size: 0.85rem;
  opacity: 0.9;
}

/* Datasets Section */
.datasets-section {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  padding: 2rem;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.section-header h2 {
  color: #1a202c;
  font-size: 1.5rem;
  font-weight: 700;
}

.view-all-btn {
  background: rgba(76, 81, 191, 0.1);
  border: 1px solid rgba(76, 81, 191, 0.3);
  color: #4c51bf;
  padding: 0.5rem 1rem;
  border-radius: 8px;
  font-weight: 600;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.3s ease;
  text-decoration: none;
}

.view-all-btn:hover {
  background: rgba(76, 81, 191, 0.2);
  transform: translateY(-1px);
}

.datasets-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.5rem;
}

.dataset-card {
  background: #f7fafc;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 1.5rem;
  transition: all 0.3s ease;
  cursor: pointer;
}

.dataset-card:hover {
  background: white;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.dataset-card h3 {
  color: #1a202c;
  font-weight: 600;
  font-size: 1.1rem;
  margin-bottom: 0.5rem;
}

.dataset-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: #718096;
  font-size: 0.85rem;
}

.dataset-delete {
  background: rgba(11, 0, 0, 0.1);
  color: #ab223b;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-weight: 600;
}

/* States */
.loading-state, .error-state {
  text-align: center;
  padding: 3rem;
  color: #718096;
  font-size: 1.1rem;
}

.error-state {
  color: #e53e3e;
}

.empty-state {
  text-align: center;
  padding: 3rem;
}

.empty-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
}

.empty-state h3 {
  color: #1a202c;
  font-size: 1.5rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
}

.empty-state p {
  color: #718096;
  font-size: 1rem;
  margin-bottom: 2rem;
}

/* Responsive */
@media (max-width: 768px) {
  .dashboard-container {
    padding: 1rem;
  }

  .dashboard-header {
    flex-direction: column;
    gap: 1.5rem;
    text-align: center;
  }

  .user-menu {
    flex-direction: column;
    gap: 0.5rem;
  }

  .stats-grid {
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1rem;
  }

  .datasets-grid {
    grid-template-columns: 1fr;
  }

  .section-header {
    flex-direction: column;
    gap: 1rem;
    text-align: center;
  }

  .actions-grid {
    grid-template-columns: 1fr;
  }
}
</style>
