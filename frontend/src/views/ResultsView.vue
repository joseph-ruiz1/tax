<!-- ResultsView.vue -->
<template>
    <div class="results-container" v-if="!loading">
        <!-- Left Panel - Form -->
        <div class="form-panel">
          <farm-income-entry
          ref="farmIncomeEntryRef"
          v-model="form"
          :saved-worksheet="savedWorksheet"
          />

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
                          type="number"
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
                          type="number"
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
</template>

<script setup>
import {ref, onMounted, reactive} from 'vue'
import { apiService } from '@/services/api.js'
import { useRoute } from 'vue-router'
import { filingStatusOptions } from '@/composables/filingstatusOptions'
import VueApexCharts from 'vue3-apexcharts'
import FarmIncomeEntry from '@/components/FarmIncomeEntry.vue'

const route = useRoute()
const loading = ref(true)
const error = ref('')
const inputs = ref(null)
const outputs = ref(null)
const currentYearIndex = ref(0)


const form = reactive({
    name: '',
    max_elected_farm_income: 0,
    qualified_farm_income: 0,
    tax_years: [],
})

const farmIncomeEntryRef = ref(null)
const savedWorksheet = ref(null)

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
        form.name = inputs.value?.name || ''
        form.max_elected_farm_income = inputs.value?.max_elected_farm_income || 0
        form.qualified_farm_income = inputs.value?.qualified_farm_income || 0
        form.tax_years = taxYears || []
        
        // Load worksheet data if it exists
        if (inputs.value?.income_worksheet) {
          savedWorksheet.value = { ...inputs.value.income_worksheet }
        }

        updateChartData()

    } catch (err) {
        error.value = 'Failed to fetch results'
        console.error('Error fetching Results', err)
    } finally {
        loading.value = false
    }
}

const submitForm = async () => {
  // Get worksheet data from FarmIncomeEntry via template ref
  const worksheetData = farmIncomeEntryRef.value?.getWorksheetData() || null

  const submissionData = {
    name: form.name,
    max_elected_farm_income: form.max_elected_farm_income,
    income_worksheet: worksheetData,
    qualified_farm_income: form.qualified_farm_income,
    tax_years: form.tax_years
  }
    try {
        const id = route.params.id
        const response = await apiService.updateDataset(id, submissionData)
        await fetchResults()
    } catch (err) {
        console.error('Failed to update dataset:', err)
    } // Need error here
}

onMounted(async () => {
    await fetchResults()
})
</script>

<style scoped>
/* Main Layout */
.results-container {
  display: grid;
  grid-template-columns: 1fr 2.5fr;
  gap: 2rem;
  max-width: 1800px;
  margin: 0 auto;
  padding: 2rem;
  background: linear-gradient(135deg, #434b6f 0%, #2e2735 100%);
  min-height: 100vh;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

.loading-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #434b6f 0%, #2e2735 100%);
  color: white;
  font-size: 1.5rem;
}

/* Left Panel - Form */
.form-panel {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.year-tabs {
  display: flex;
  justify-content: center;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.year-tabs button {
  padding: 0.75rem 1.5rem;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  color: white;
  font-weight: 600;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
}

.year-tabs button:hover {
  background: rgba(255, 255, 255, 0.2);
  transform: translateY(-2px);
}

.year-tabs button.active {
  background: rgba(255, 255, 255, 0.9);
  color: #4c51bf;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
}

.year-form {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  padding: 2rem;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.dataset-title {
  margin-bottom: 1.5rem;
}

.dataset-title h1 {
  color: #1a202c;
  font-size: 1.5rem;
  font-weight: 700;
  margin: 0;
  text-align: center;
}

.year-form form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.field-container {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.title-with-info {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.title {
  color: #1a202c;
  font-size: 0.95rem;
  font-weight: 600;
  margin: 0;
}

.field-container input,
.field-container select {
  width: 100%;
  padding: 0.75rem 1rem;
  border: 2px solid #e2e8f0;
  border-radius: 8px;
  font-size: 1rem;
  background: white;
  color: #1a202c;
  transition: all 0.3s ease;
  outline: none;
}

.field-container input:focus,
.field-container select:focus {
  border-color: #4c51bf;
  box-shadow: 0 0 0 3px rgba(76, 81, 191, 0.1);
}

.field-container input::placeholder {
  color: #a0aec0;
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
  display: flex;
  align-items: center;
  justify-content: center;
}

.info-btn:hover {
  background: rgba(59, 130, 246, 0.2);
  transform: scale(1.1);
}

.info-icon {
  font-size: 0.75rem;
  font-weight: 700;
  color: #3b82f6;
  font-style: italic;
}

.tooltip {
  position: absolute;
  bottom: calc(100% + 8px);
  left: 50%;
  transform: translateX(-50%);
  background: #1a202c;
  color: white;
  padding: 0.75rem;
  border-radius: 8px;
  font-size: 0.875rem;
  line-height: 1.5;
  white-space: normal;
  min-width: 200px;
  max-width: 300px;
  width: max-content;
  opacity: 0;
  visibility: hidden;
  transition: all 0.2s ease;
  pointer-events: none;
  z-index: 1000;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

.tooltip::after {
  content: '';
  position: absolute;
  top: 100%;
  left: 50%;
  transform: translateX(-50%);
  border: 6px solid transparent;
  border-top-color: #1a202c;
}

.info-btn:hover .tooltip {
  opacity: 1;
  visibility: visible;
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
  justify-content: center;
  align-items: center;
  margin-bottom: 1rem;
}

.section-header h3 {
  color: #1a202c;
  font-size: 1.25rem;
  font-weight: 700;
  margin: 0;
}

.chart-placeholder {
  background: #f7fafc;
  border: 2px dashed #e2e8f0;
  border-radius: 12px;
  padding: 3rem 2rem;
  text-align: center;
  color: #718096;
  min-height: 350px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}

/* Responsive Design */
@media (max-width: 1200px) {
  .results-container {
    grid-template-columns: 1fr;
    gap: 1.5rem;
  }
}

@media (max-width: 768px) {
  .results-container {
    padding: 1rem;
  }
  
  .year-tabs {
    gap: 0.25rem;
  }
  
  .year-tabs button {
    padding: 0.5rem 1rem;
    font-size: 0.8rem;
  }
  
  .year-form,
  .chart-section {
    padding: 1.5rem;
  }
}
</style>