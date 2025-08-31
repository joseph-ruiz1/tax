<!-- ResultsView.vue -->
<template>
    <div class="results-container" v-if="!loading">
        <!-- Left Panel - Form -->
        <div class="form-panel">
            <div class="dataset-header">
                <h1>General info</h1>
                <form class="dataset-form">
                    <p class="title">Title</p>
                    <input v-model="form.name" placeholder="Enter Calculation Name">
                    <p class="title">Max Elected Farm Income</p>
                    <input v-model="form.max_elected_farm_income" placeholder="Enter Farm income">
                    <p class="title">Qualified Farm Income</p>
                    <input v-model="form.qualified_farm_income" placeholder="Farm income cap gains">
                </form>
            </div>

            <!-- Year Navigation-->
            <div class="year-tabs" v-if="form.tax_years.length > 0">
                <button
                v-for="(year, index) in form.tax_years"
                :key="year.year"
                @click="currentYearIndex = index"
                :class="{ active: index === currentYearIndex }"
                >
                    {{ year.year }}
                </button>
            </div>

            <!-- Current Year Form -->
            <div class="year-form" v-if="form.tax_years[currentYearIndex]">
                <h3>Tax Year {{ form.tax_years[currentYearIndex].year }}</h3>
                <form>
                    <p class="title">Filing Status</p>
                    <select v-model="form.tax_years[currentYearIndex].filing_status">
                        <option disabled value="">Filing Status</option>
                        <option>Single</option>
                        <option>Married Filing Jointly</option>
                    </select>
                    <p class="title">Taxable Income</p>
                    <input
                    v-model.number="form.tax_years[currentYearIndex].taxable_income"
                    placeholder="Taxable income"
                    >
                    <p class="title">Qualified Income</p>
                    <input
                    v-model.number="form.tax_years[currentYearIndex].qualified_income"
                    placeholder="Qualified income"
                    >
                </form>
            </div>
            
            <button @click="submitForm" class="submit-btn">Update Calculation</button>
        </div>

        <!-- Right Panel - Results -->
        <div class="results-panel">
            <div class="results-header">
                <h1>Results</h1>
                <div class="last-updated">
                    Last updated: {{ lastUpdated }}
                </div>
            </div>

           
            <!-- Chart Area -->
            <div class="chart-section">
                <div class="section-header">
                    <h3>Tax Comparison by Year</h3>
                    <div class="chart-controls">
                        <button class="chart-toggle active">Bar Chart</button>
                        <button class="chart-toggle">Line Chart</button>
                    </div>
                </div>
                <div class="chart-placeholder">
                    <div class="chart-icon">📊</div>
                    <apexchart
                        type="line"
                        height="350"
                        :options="chartOptions"
                        :series="series"
                      ></apexchart>
                    <p class="chart-subtitle">Comparing baseline vs optimized tax calculations</p>
                  </div>
              </div>
          </div>
      </div>
    <div v-else>
        loading...
    </div>
</template>

<script setup>
import {ref, onMounted, computed} from 'vue'
import { apiService } from '@/services/api.js'
import { useRouter } from 'vue-router'
import { useRoute } from 'vue-router'
import VueApexCharts from 'vue3-apexcharts'

const route = useRoute()
const router = useRouter()
const loading = ref(true)
const error = ref('')
const inputs = ref(null)
const outputs = ref(null)

const currentYearIndex = ref(0)
const lastUpdated = ref(new Date().toLocaleString())

const form = ref({
    name: '',
    max_elected_farm_income: 0,
    qualified_farm_income: 0,
    tax_years: [],
})

const submitForm = async () => {
    try {
        const id = route.params.id
        const filingstatusMapping = {
            'Single': 'single',
            'Married Filing Jointly': 'MFJ'
        }
        form.value.tax_years?.forEach(year => {
            if (filingstatusMapping[year.filing_status]) {
                year.filing_status = filingstatusMapping[year.filing_status]
            }
        })
        const response = await apiService.patchDataset(id, form.value)
        // Update results after successful save
        updateResults()
    } catch (err) {
        console.error('Failed to update dataset:', err)
    }
}

const series = ref([
  {
    name: 'Sales',
    data: [30, 40, 35, 50, 49, 60, 70, 91, 125]
  }
])

const chartOptions = ref({
  chart: {
    id: 'simple-line-chart'
  },
  xaxis: {
    categories: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep']
  },
  title: {
    text: 'Simple Line Chart'
  }
})

const fetchResults = async () => {
    try {
        const id = route.params.id
        const data = await apiService.getResults(id)
        inputs.value = data.form
        outputs.value = data.outputs

        // Reverse mapping for filing status
        const reverseFilingStatusMapping = {
            'single': 'Single',
            'MFJ': 'Married Filing Jointly'
        }

        const taxYears = inputs.value?.tax_years?.map(year => ({
          ...year,
          filing_status: reverseFilingStatusMapping[year.filing_status] || year.filing_status
        })) || []

        // Initilize form with API data
        form.value = {
          name: inputs.value?.name || '',
          max_elected_farm_income: inputs.value?.max_elected_farm_income || 0,
          qualified_farm_income: inputs.value?.qualified_farm_income || 0,
          tax_years: taxYears
        }
    } catch (err) {
        error.value = 'Failed to fetch results'
    } finally {
        loading.value = false
    }
}


onMounted(async () => {
    await fetchResults()
})
</script>

<style scoped>
/* Main Layout */
.results-container {
  display: grid;
  grid-template-columns: 1fr 2fr;
  gap: 2rem;
  max-width: 1800px;
  margin: 0 auto;
  padding: 2rem;
  background: linear-gradient(135deg, #434b6f 0%, #2e2735 100%);
  min-height: 100vh;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

/* Left Panel - Form (copied from your original) */
.form-panel {
  max-width: 500px;
}

.dataset-header {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  padding: 2rem;
  margin-bottom: 2rem;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.dataset-header h1 {
  color: #1a202c;
  font-size: 1.5rem;
  font-weight: 700;
  margin: 0 0 .5rem 0;
  text-align: center;
}

.dataset-form {
  display: grid;
  gap: .5rem;
}

.title {
    color: #1a202c;
    font-size: 1rem;
    font-weight: 700;
    text-align: left;
    margin: 0.5rem 0 0.25rem 0;
}

.year-tabs {
  display: flex;
  justify-content: center;
  gap: 0.5rem;
  margin-bottom: 2rem;
  flex-wrap: wrap;
}

.year-tabs button {
  padding: 0.75rem 1.5rem;
  background: rgba(255, 255, 255, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 50px;
  color: white;
  font-weight: 600;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
}

.year-tabs button:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.year-tabs button.active {
  background: rgba(255, 255, 255, 0.9);
  color: #4c51bf;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
  transform: translateY(-2px);
}

.year-form {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  padding: 2rem;
  margin-bottom: 2rem;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.year-form h3 {
  color: #1a202c;
  font-size: 1.25rem;
  font-weight: 700;
  margin: 0 0 1rem 0;
  text-align: center;
}

.year-form form {
  display: grid;
  gap: .5rem;
}

input, select {
  padding: .5rem 1.25rem;
  border: 2px solid #e2e8f0;
  border-radius: 12px;
  font-size: 1rem;
  background: white;
  color: #1a202c;
  transition: all 0.3s ease;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  width: 100%;
}

input:focus, select:focus {
  outline: none;
  border-color: #4c51bf;
  box-shadow: 0 0 0 3px rgba(76, 81, 191, 0.1);
  transform: translateY(-1px);
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
  width: 100%;
}

.submit-btn:hover {
  transform: translateY(-3px);
  box-shadow: 0 6px 20px rgba(72, 187, 120, 0.5);
}

/* Right Panel - Results */
.results-panel {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.results-header {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  padding: 2rem;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  text-align: center;
}

.results-header h1 {
  color: #1a202c;
  font-size: 2rem;
  font-weight: 700;
  margin: 0 0 0.5rem 0;
}

.last-updated {
  color: #718096;
  font-size: 0.9rem;
  font-style: italic;
}

/* Summary Cards */
.summary-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
}

.summary-card {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  padding: 1.5rem;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  transition: transform 0.3s ease;
}

.summary-card:hover {
  transform: translateY(-4px);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.card-header h3 {
  color: #4a5568;
  font-size: 0.9rem;
  font-weight: 600;
  margin: 0;
}

.card-icon {
  font-size: 1.5rem;
}

.card-value {
  color: #1a202c;
  font-size: 2rem;
  font-weight: 700;
  margin-bottom: 0.5rem;
}

.card-change {
  font-size: 0.8rem;
  font-weight: 600;
}

.card-change.positive { color: #48bb78; }
.card-change.negative { color: #f56565; }
.card-change.neutral { color: #718096; }

/* Chart Section */
.chart-section {
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

.section-header h3 {
  color: #1a202c;
  font-size: 1.25rem;
  font-weight: 700;
  margin: 0;
}

.chart-controls {
  display: flex;
  gap: 0.5rem;
}

.chart-toggle {
  padding: 0.5rem 1rem;
  border: 2px solid #e2e8f0;
  background: white;
  border-radius: 8px;
  font-size: 0.8rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.chart-toggle.active {
  background: #4c51bf;
  color: white;
  border-color: #4c51bf;
}

.chart-placeholder {
  background: #f7fafc;
  border: 2px dashed #e2e8f0;
  border-radius: 12px;
  padding: 4rem 2rem;
  text-align: center;
  color: #718096;
}

.chart-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
}

.chart-subtitle {
  font-size: 0.9rem;
  margin-top: 0.5rem;
}

/* Table Section */
.table-section {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  padding: 2rem;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.results-table {
  border-radius: 12px;
  overflow: hidden;
  border: 1px solid #e2e8f0;
}

.table-header, .table-row {
  display: grid;
  grid-template-columns: 1fr 1.2fr 1.2fr 1fr 1fr;
  gap: 1rem;
}

.table-header {
  background: #f7fafc;
  font-weight: 700;
  color: #4a5568;
}

.table-row {
  background: white;
  border-top: 1px solid #e2e8f0;
}

.table-row:hover {
  background: #f9fafb;
}

.table-cell {
  padding: 1rem;
  display: flex;
  align-items: center;
  font-size: 0.9rem;
}

.font-medium {
  font-weight: 600;
}

.savings {
  color: #48bb78;
  font-weight: 600;
}

.reduction {
  color: #48bb78;
  font-weight: 600;
}

/* Responsive Design */
@media (max-width: 1200px) {
  .results-container {
    grid-template-columns: 1fr;
    gap: 1rem;
  }
  
  .form-panel {
    max-width: none;
  }
}

@media (max-width: 768px) {
  .summary-cards {
    grid-template-columns: 1fr;
  }
  
  .table-header, .table-row {
    grid-template-columns: 1fr;
    gap: 0.5rem;
  }
  
  .table-cell {
    padding: 0.75rem;
  }
}
</style>