<!-- ResultsView.vue -->
<template>
    <div class="results-container" v-if="!loading">
        <!-- Left Panel - Form -->
        <div class="form-panel">
          <div class="dataset-header">
            <div class="dataset-title">
              <button class="to-dashboard-btn" @click="toDashboard">← Back</button>
              <h1>General info</h1>
            </div>

            <form class="dataset-form">
              <div class="field-container">
                <p class="title">Title</p>
                <input v-model="form.name" placeholder="Enter Calculation Name" required>
              </div>

              <div class="field-container">
                <div class="title-with-info">
                  <p class="title">Max Elected Farm Income</p>
                  <button type="button" class="open-modal-btn" @click="isOpen = true" aria-label="More information">
                    <span class="info-icon">i</span>
                    <span class="tooltip">Click for more details</span>
                  </button>
                </div>
                <input v-model="form.max_elected_farm_income" placeholder="Enter Farm income" required>
              </div>

              <div class="field-container">
                <div class="title-with-info">
                  <p class="title">Qualified Farm Income</p>
                  <button type="button" class="info-btn" aria-label="More information">
                    <span class="info-icon">i</span>
                    <span class="tooltip">The portion of the total elected farm income that is made up of capital gains. Caclulated as long term farm gains - short term farm loss. 1250 gains are currently not supported.</span>
                  </button>
                </div>
                <input v-model="form.qualified_farm_income" placeholder="Farm income cap gains" required>
              </div>
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
              <div class="dataset-title">
                <h1>Tax Year {{ form.tax_years[currentYearIndex].year }}</h1>
              </div>
        
                <form>
                  <div class="field-container">
                    <div class="title-with-info">
                      <p class="title">Filing Status</p>
                    </div>
                      <select v-model="form.tax_years[currentYearIndex].filing_status" required>
                        <option disabled value="">Filing Status</option>
                        <option v-for="opt in filingStatusOptions" :key="opt.value" :value="opt.value">
                          {{ opt.label }}
                        </option>
                      </select>
                    </div>
                    
                    <div class="field-container">
                      <div class="title-with-info">
                        <p class="title">Taxable Income</p>
                        <button type="button" class="info-btn" aria-label="More information">
                          <span class="info-icon">i</span>
                          <span class="tooltip">Taxable Income from the return. Adjustment for elected income not needed.</span>
                        </button>
                      </div>
                        <input
                          v-model.number="form.tax_years[currentYearIndex].taxable_income"
                          placeholder="Taxable income"
                          required
                        >
                    </div>
                    
                    <div class="field-container">
                      <div class="title-with-info">
                        <p class="title">Qualified Income</p>
                        <button type="button" class="info-btn" aria-label="More information">
                          <span class="info-icon">i</span>
                          <span class="tooltip">Long term capital gains + qualified dividends</span>
                        </button>
                      </div>
                        <input
                          v-model.number="form.tax_years[currentYearIndex].qualified_income"
                          placeholder="Qualified income"
                          required
                        >
                    </div>
                </form>
            </div>
            <button @click="submitForm" class="submit-btn">Update Calculation</button>
        </div>

        <!--Results -->
        <div class="results-panel">
          <!-- Chart Area -->
          <div class="chart-section">
            <div class="section-header">
                <h3>Total 2024 tax</h3>
            </div>
            <vue-apex-charts
                id="tax-savings-chart"
                v-if="series.length > 0"
                height="350"
                :options="chartOptions"
                :series="series"
              ></vue-apex-charts>
              <div v-else class="chart-placeholder">
                <p>Loading chart data...</p>
              </div>
            <div class="section-header">
              <h3>Net Tax Savings/Expense</h3>
            </div>
            <vue-apex-charts
                id="tax-delta-chart"
                v-if="series.length > 0"
                height="350"
                :options="deltaChartOptions"
                :series="delta_series"
            ></vue-apex-charts>
          </div>
        </div>
      </div>
    <div v-else>
        loading...
    </div>

    <!-- Modal - Teleported to body -->
  <Teleport to="body">
    <div v-if="isOpen">
      <modal-content
        @close="isOpen = false"
        title="Farm Income Worksheet"
        :close-on-overlay-click="true"
      >
      <!-- Main content -->
        <div>
          <div class="field-container">
            <div class="title-with-info">
              <p class="title">Filing Status</p>
            </div>
              <!-- <input v-model="exampleValue" placeholder="Enter something" /> -->
          </div>
        </div>
        
        <!-- Optional footer with action buttons -->
        <template #footer>
          <button @click="handleSave" class="btn-primary">Save</button>
          <button @click="isOpen = false" class="btn-secondary">Cancel</button>
        </template>
      </modal-content>
    </div>
  </Teleport>
</template>

<script setup>
import {ref, onMounted, computed, reactive} from 'vue'
import { apiService } from '@/services/api.js'
import { useRouter } from 'vue-router'
import { useRoute } from 'vue-router'
import { filingStatusOptions } from '@/composables/filingstatusOptions'
import VueApexCharts from 'vue3-apexcharts'
import ModalContent from './ModalContent.vue'

const route = useRoute()
const router = useRouter()
const loading = ref(true)
const error = ref('')
const inputs = ref(null)
const outputs = ref(null)
const isOpen = ref(false)
const currentYearIndex = ref(0)


const form = reactive({
    name: '',
    max_elected_farm_income: 0,
    qualified_farm_income: 0,
    tax_years: [],
})

const series = ref([])
const delta_series = ref([])
const baseOptions = {
  chart: {
    type: 'area',
    toolbar: {
      show: true,
      offsetX: 0,
      offsetY: 0,
      autoSelected: '',
      tools: {
        download: false,
        zoom: true,
        zoomin: true,
        zoomout: true,
        pan: true,
        reset: true,
      },
      reset: 'Reset Zoom',
    },
    animations: {
      enabled: true,
      easing: 'easeinout',
      speed: 800,
      animateGradually: {
        enabled: true,
        delay: 150,
      },
      dynamicAnimation: {
        enabled: true,
        speed: 350,
      },
    },
    zoom: {
      allowMouseWheelZoom: false,
    },
  },
  dataLabels: {
    enabled: false,
  },
  stroke: {
    curve: 'straight',
    width: 2,
  },
  grid: {
    padding: {
      bottom: 30,
    },
  },
  xaxis: {
    type: 'numeric',
    labels: {
      formatter: function (val) {
        val = val | 0
        return '$' + val.toLocaleString()
      },
    },
    title: {
      text: 'Amount Elected',
      offsetY: 15
    },
    categories: [],
    tickAmount: 10,
  },
  yaxis: {
    type: 'numeric',
    labels: {
      formatter: function (val) {
        return '$' + val.toLocaleString()
      },
    },
    title: {
      offsetX: -6
    }
  },
  legend: {
    position: 'top',
  },
  colors: ['#4c51bf', '#48bb78', '#f56565'],
  tooltip: {
    x: {
      show: false,
      format: 'numeric',
      formatter: function (val) {
        return '$' + val.toLocaleString()
      },
    },
    y: {
      format: 'numeric',
      formatter: function (val) {
        return '$' + val.toLocaleString()
      },
    },
    theme: 'dark',
  },
}

const chartOptions = ref({
  ...baseOptions,
  chart: {
    ...baseOptions.chart,
    id: 'tax-savings-chart',
    },
  yaxis: {
    ...baseOptions.yaxis,
    title: { ...baseOptions.yaxis.title, 
    text: 'Total Tax' },
  },
})

const deltaChartOptions = ref({
  ...baseOptions,
  chart: {
    ...baseOptions.chart,
    id: 'delta-tax-savings-chart',
  },
  yaxis: {
    ...baseOptions.yaxis,
    title: { ...baseOptions.yaxis.title, 
    text: 'Total Tax Savings/Expense' },
  },
})

const updateChartData = () => {
  if (!outputs.value) return

  const sch_j_total = outputs.value.results.map(result => parseFloat(result.form.line_23))
  const tax_delta = outputs.value.results.map(result => parseFloat(result.form.tax_delta))
  const elected = outputs.value.results.map(result => parseFloat(result.form.line_2a))
  const qualified_elected = outputs.value.results.map(result => parseFloat(result.form.line_2b))

  chartOptions.value = {
    ...chartOptions.value,
    xaxis: {
      ...chartOptions.value.xaxis,
      categories: elected
    }
  }

  deltaChartOptions.value = {
    ...deltaChartOptions.value,
    xaxis: {
      ...deltaChartOptions.value.xaxis,
      categories: elected
    }
  }

  series.value = [
    {
      name: 'Total 2024 tax',
      data: sch_j_total
    }
  ]

  delta_series.value = [
    {
      name: 'Total 2024 tax savings/expense',
      data: tax_delta
    }
  ]
}

const fetchResults = async () => {
    try {
        const id = route.params.id
        const data = await apiService.getResults(id)
        inputs.value = data.form
        outputs.value = data.outputs

        const taxYears = inputs.value?.tax_years?.map(year => ({
          ...year
        }))

        // Initilize form with API data
        Object.assign(form, {
          name: inputs.value?.name,
          max_elected_farm_income: inputs.value?.max_elected_farm_income,
          qualified_farm_income: inputs.value?.qualified_farm_income,
          tax_years: taxYears
        })

        updateChartData()

    } catch (err) {
        error.value = 'Failed to fetch results'
        console.error('Error fetching Results', err)
    } finally {
        loading.value = false
    }
}

const submitForm = async () => {
    try {
        const id = route.params.id
        const response = await apiService.updateDataset(id, form)
        await fetchResults()
    } catch (err) {
        console.error('Failed to update dataset:', err)
    }
}

const toDashboard = async () => {
  router.push('/')
}

onMounted(async () => {
    await fetchResults()
})
</script>

<style scoped>
/* Main Layout */
.results-container {
  display: grid;
  grid-template-columns: 1fr 2.5fr; /* Left: 1/3, Right: 2/3 */
  gap: 2rem;
  max-width: 1800px;
  margin: 0 auto;
  padding: 2rem;
  background: linear-gradient(135deg, #434b6f 0%, #2e2735 100%);
  min-height: 100vh;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  box-sizing: border-box;
}

/* Left Panel - Form */
.form-panel {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  width: 100%;
}

.dataset-header {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  padding: 2rem;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.dataset-title {
  position: relative;
  display: flex;
  justify-content: center;
  align-items: center;
}

.dataset-header h1 {
  color: #1a202c;
  font-size: 1.5rem;
  font-weight: 700;
  margin: 0;
  text-align: center;
}

.dataset-form {
  display: grid;
  gap: 1rem;
}

.field-container input, select {
  width: 100%;
  padding: 0.75rem 1rem;
  border: 2px solid rgba(0, 0, 0, 0.1);
  border-radius: 8px;
  font-size: 1rem;
  background: white;
  transition: all 0.3s ease;
  outline: none;
}

.field-container select {
   width: 100%;
  padding: 0.75rem 1rem;
  border: 2px solid rgba(0, 0, 0, 0.1);
  border-radius: 8px;
  font-size: 1rem;
  background: white;
  transition: all 0.3s ease;
  outline: none;
}

/* Title styling within field container */
.field-container .title {
  font-weight: 600;
  color: #1a202c;
  font-size: 0.95rem;
  margin: 1rem 0 0.5rem 0;
}

.field-container input:focus {
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.field-container input:hover {
  border-color: rgba(0, 0, 0, 0.2);
}

.field-container input::placeholder {
  color: rgba(0, 0, 0, 0.4);
  font-size: 0.95rem;
}

.title-with-info {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
}

.title-with-info .title {
  margin: 0; /* Remove default paragraph margin */
}

.title {
  color: #1a202c;
  font-size: 1rem;
  font-weight: 700;
  text-align: left;
  margin: 0.5rem 0 0.25rem 0;
}

.info-btn {
  position: relative;
  background: rgba(59, 130, 246, 0.1);
  border: 1px solid rgba(59, 130, 246, 0.3);
  border-radius: 50%;
  width: 20px;
  height: 20px;
  padding: 0;
  cursor: help;
  transition: all 0.2s ease;
  flex-shrink: 0;
}

.info-btn:hover {
  background: rgba(59, 130, 246, 0.2);
  border-color: rgba(59, 130, 246, 0.5);
  transform: scale(1.1);
}

.info-icon {
  font-size: 0.75rem;
  font-weight: 700;
  color: #3b82f6;
  font-style: italic;
  display: block;
  line-height: 1;
}

.tooltip {
  position: absolute;
  bottom: calc(100% + 8px); /* Positions above the button */
  left: 50%;
  transform: translateX(-50%);
  background: #545557; 
  border: 2px solid rgba(0, 0, 0, 0.3);
  color: white;
  padding: 0.5rem 0.75rem;
  border-radius: 6px;
  line-height: 1.5;
  font-size: 0.875rem;
  white-space: normal;
  min-width: 200px;
  max-width: 320px;
  width: max-content;
  opacity: 0;
  visibility: hidden;
  transition: opacity 0.2s ease, visibility 0.2s ease;
  pointer-events: none;
  z-index: 999;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}

/* Tooltip arrow */
.tooltip::after {
  content: '';
  position: absolute;
  top: 100%;
  left: 50%;
  transform: translateX(-50%);
  border: 6px solid transparent;
  border-top-color: #1a202c;
}

/* Show tooltip on hover */
.info-btn:hover .tooltip {
  opacity: 1;
  visibility: visible;
}

.to-dashboard-btn {
  position: absolute;
  left: 0;
  background: rgba(46, 39, 53, 0.1);
  border: 1px solid rgba(0, 0, 0, 0.3);
  color: #000000;
  padding: 0.3rem .3rem;
  border-radius: 8px;
  font-weight: 600;
  font-size: 0.65rem;
  cursor: pointer;
  transition: all 0.3s ease;
  white-space: nowrap;
}

.to-dashboard-btn:hover {
  background: rgba(255, 255, 255, .1);
  transform: translateY(-1px);
}

.year-tabs {
  display: flex;
  justify-content: center;
  gap: 0.5rem;
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
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.year-form h1 {
  color: #1a202c;
  font-size: 1.5rem;
  font-weight: 700;
  margin: 0;
  text-align: center;
}

.year-form h3 {
  color: #1a202c;
  font-size: 1.25rem;
  font-weight: 700;
  margin: 0 0 1.5rem 0;
  text-align: center;
}

.year-form form {
  display: grid;
  gap: 1rem;
}

input, select {
  padding: 0.75rem 1.25rem;
  border: 2px solid #e2e8f0;
  border-radius: 12px;
  font-size: 1rem;
  background: white;
  color: #1a202c;
  transition: all 0.3s ease;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  width: 65%;
  box-sizing: border-box;
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
  box-sizing: border-box;
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
  width: 100%;
  min-height: 100%;
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

/* Chart Section */
.chart-section {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  padding: 2rem;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  flex: 1; /* This makes the chart section take up remaining space */
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: .5rem;
}

.section-header h3 {
  color: #1a202c;
  font-size: 1.25rem;
  font-weight: 700;
  margin: 0;
  margin: auto
}

.chart-controls {
  display: flex;
  gap: 0.5rem;
}

.chart-placeholder {
  background: #f7fafc;
  border: 2px dashed #e2e8f0;
  border-radius: 12px;
  padding: 2rem;
  text-align: center;
  color: #718096;
  min-height: 400px; /* Ensures minimum height for the chart area */
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
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
  width: 100%;
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

/* Modal */
.open-modal-btn {
  padding: .2rem .5rem;
  background: #3b82f6;
  color: rgb(63, 27, 27);
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  transition: background 0.2s ease;
}

.open-modal-btn:hover {
  background: #2563eb;
}

.btn-primary {
  padding: 0.5rem .5rem;
  background: #717275;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 400;
}

.btn-secondary {
  padding: 0.75rem 1.5rem;
  background: #e5e7eb;
  color: #374151;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
}

/* Responsive Design */
@media (max-width: 1200px) {
  .results-container {
    grid-template-columns: 1fr;
    gap: 1.5rem;
  }
  
  .form-panel {
    max-width: none;
  }
}

@media (max-width: 768px) {
  .results-container {
    padding: 1rem;
  }
  
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
  
  .year-tabs {
    gap: 0.25rem;
  }
  
  .year-tabs button {
    padding: 0.5rem 1rem;
    font-size: 0.8rem;
  }
}
</style>