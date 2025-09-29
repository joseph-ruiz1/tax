<!-- DatasetView.vue -->
<template>
    <div class="dashboard-container">
        <!-- Header -->
        <h2>Datasets:</h2>
        <div class="dashboard-header">
            <div class="dashboard-title">
                <h1>Welcome back, {{ user?.username || 'user' }}</h1>
                <div class="user-menu">
                    <button class="logout-btn" @click="handleLogout">Logout</button>
                </div>
            </div>
        </div>
    </div>

    <!-- Quick Actions -->
    <div class="quick-actions">
      <h2>Quick Actions</h2>
      <div class="actions-grid">
        <button class="action-btn success" @click="createNewDataset">
          <div class="action-text">
            <h4>New Tax Calculation</h4>
          </div>
        </button>
        <router-link to="/datasets" class="action-btn">
          <div class="action-text">
            <h4>View Datasets</h4>
            <p>Access your saved datasets</p>
          </div>
        </router-link>
      </div>
    </div>

    <!-- Recent Datasets -->
    <div class="datasets-section">
      <div class="section-header">
        <h2>Recent Datasets</h2>
        <router-link to="/datasets" class="view-all-btn">
          View All →
        </router-link>
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
            <p>Start your first analysis</p>
          </div>
        </button>
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
const form = ref({})
const user = ref(null)
const showDatasets = ref(false)

// Computed property for recent datasets (first 6)
const recentDatasets = computed(() => {
  return datasets.value.slice(0, 6)
})

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

onMounted(async () => {
    await Promise.all([
        fetchUser(),
        fetchDatasets()
    ])
})

</script>

<style scoped>
.dashboard-container {
  max-width: 1800px;
  margin: 0 auto;
  padding: 2rem;
  background: linear-gradient(135deg, #434b6f 0%, #2e2735 100%);
  min-height: 100vh;
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

/* Stats Grid */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.stat-card {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  padding: 2rem;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  text-align: center;
  transition: all 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
}

.stat-icon {
  font-size: 2.5rem;
  margin-bottom: 1rem;
}

.stat-card h3 {
  color: #1a202c;
  font-size: 2rem;
  font-weight: 700;
  margin-bottom: 0.5rem;
}

.stat-card p {
  color: #718096;
  font-size: 1rem;
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
  margin-bottom: 1.5rem;
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

.action-text h4 {
  font-size: 1rem;
  font-weight: 600;
  margin-bottom: 0.25rem;
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

.dataset-status {
  background: rgba(72, 187, 120, 0.1);
  color: #38a169;
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