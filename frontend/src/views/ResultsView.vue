<!-- ResultsView.vue -->
<template>
  <div class="results-container" v-if="!loading">
    <!-- Left Panel - Form -->
    <div class="form-panel">

      <!-- FarmIncomeEntry.vue -->
      <div class="year-form">
        <farm-income-entry
        ref="farmIncomeEntryRef"
        v-model="form"
        :saved-worksheet="savedWorksheet"
        />
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
      
      <!-- YearsDataEntry.vue-->
      <div class="year-form">
        <years-data-entry 
        v-model="form"
        :currentYearIndex="currentYearIndex"
        />
      </div>
      <button @click="submitForm" class="submit-btn">Update Calculation</button>
    </div>

    <!--Results -->
    <div class="results-panel">
      <!-- Chart Area -->
      <div class="chart-section">
        <div class="section-header">
            <h3>Total {{ form.election_year }} tax</h3>
        </div>

        <div class="chart-container">
          <div v-if="loading || chartTransitioning" class="chart-loading-overlay" key="loading">
            <div class="loading-text">Updating chart...</div>
          </div>

          <vue-apex-charts
            id="tax-savings-chart"
            key="chart"
            v-if="series.length > 0 && !chartTransitioning"
            height="350"
            :options="chartOptions"
            :series="series"
          ></vue-apex-charts>
        </div>
        
        <div class="section-header">
          <h3>Net Tax Savings/Expense</h3>
        </div>

        <div class="chart-container">
          <div v-if="loading || chartTransitioning" class="chart-loading-overlay" key="loading-delta">
            <div class="loading-text">Updating chart...</div>
          </div>

          <vue-apex-charts
              id="tax-delta-chart"
              v-if="series.length > 0 && !chartTransitioning"
              height="350"
              :options="deltaChartOptions"
              :series="delta_series"
          ></vue-apex-charts>
        </div>
      </div>
        
       
    </div>
  </div>
  <div v-else>
      loading...
  </div>
</template>

<script setup>
import {ref, onMounted, reactive, watch} from 'vue'
import { apiService } from '@/services/api.js'
import { useRoute } from 'vue-router'
import VueApexCharts from 'vue3-apexcharts'
import { updateElectionYear } from '@/composables/updateElectionYear'
import FarmIncomeEntry from '@/components/FarmIncomeEntry.vue'
import YearsDataEntry from '@/components/YearsDataEntry.vue'
import { correctTaxYears } from '@/composables/correctTaxYears'

const route = useRoute()
const loading = ref(true)
const chartTransitioning = ref(false)
const error = ref('')
const inputs = ref(null)
const outputs = ref(null)
const currentYearIndex = ref(0)
const farmIncomeEntryRef = ref(null)
const savedWorksheet = ref(null)

const form = reactive({
    name: '',
    max_elected_farm_income: 0,
    qualified_farm_income: 0,
    election_year: null,
    tax_years: [],
})

updateElectionYear(form, currentYearIndex)

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
      easing: 'easeout',
      speed: 150,
      animateGradually: {
        enabled: true,
        delay: 800,
      },
      dynamicAnimation: {
        enabled: true,
        speed: 800,
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
      offsetX: -1,
      offsetY: 5,
      style: {
        fontSize: '14px',
        fontWeight: 600,
      }
    },
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

const updateChartData = (response = null) => {
// response.outputs will only contain data upon update
  const data = response?.outputs || outputs.value

  try {
    loading.value = true
  
    if (!data) return
    const sch_j_total = data.results.map(result => parseFloat(result.line_23))
    const tax_delta = data.results.map(result => parseFloat(result.tax_delta))
    const elected = data.results.map(result => parseFloat(result.line_2a))
    const qualified_elected = data.results.map(result => parseFloat(result.line_2b))

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
  
    loading.value = false  
    // Transition delay
    chartTransitioning.value = true
    setTimeout(() => {
      chartTransitioning.value = false
    }, 100)

  } catch (err) {
    error.value = 'Failed to update results'
  } finally {
    loading.value = false
  }
}

const fetchResults = async () => {
  try {
    const id = route.params.id
    const data = await apiService.getResults(id)
    inputs.value = data.form
    outputs.value = data.outputs

    // Initilize form with API data
    form.name = inputs.value?.name || ''
    form.max_elected_farm_income = inputs.value?.max_elected_farm_income || 0
    form.qualified_farm_income = inputs.value?.qualified_farm_income || 0
    form.election_year = inputs.value?.election_year || null
    
    form.tax_years = inputs.value?.tax_years?.map((year, index) => ({
      ...year,
      is_electing: index === 0 ? true : year.is_electing,
      cannot_elect: index === 0 ? true : year.cannot_elect
    })) || []

    // Search for current year to ensure we set cannot_elect on correct year
    const current_year = form.tax_years.reduce((max, current) => 
    parseFloat(current.year) > parseFloat(max.year) ? current : max)
    current_year.cannot_elect = true
    
    // Load worksheet data if it exists
    if (inputs.value?.income_worksheet) {
      savedWorksheet.value = { ...inputs.value.income_worksheet }
    }

    // Ensure election year aligns with first year in tax_years array, correct if off
    if (form.election_year != parseInt(form.tax_years[0].year)) {
      correctTaxYears(form.election_year, form.tax_years)
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
    election_year: form.election_year,
      tax_years: form.tax_years.map((year, index) => 
      index === 0 
        ? {
            ...year,
            elected_farm_income: form.max_elected_farm_income,
            qualified_farm_income: form.qualified_farm_income
          }
        : year
    )
  }
    try {
        const id = route.params.id
        const response = await apiService.updateDataset(id, submissionData)
        updateChartData(response)
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
.dataset-header {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 16px;
  padding: 1.5rem;
  margin: 0 auto 2rem auto;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

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
  transition: transform 0.3s ease, background .2s ease;
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
  border-radius: 16px;
  padding: 1.5rem;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.dataset-title {
  margin-bottom: .75rem;
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
  gap: 1rem;
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

.title-with-info input[type="checkbox"] {
  width: auto;
  padding: 0;
  border: none;
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
  transition: box-shadow 0.3s ease;
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

.submit-btn {
  background: linear-gradient(135deg, #48bb78 0%, #38a169 100%);
  color: white;
  padding: 1rem 2rem;
  border-radius: 12px;
  border: none;
  font-weight: 700;
  font-size: 1rem;
  cursor: pointer;
  transition: transform 0.3s ease;
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
  border-radius: 16px;
  padding: 3rem;
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

.chart-container {
  position: relative;
  width: 100%;
  height: 350px
}

.chart-loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: rgba(255, 255, 255, 0.95);
  z-index: 10;
}

.loading-text {
  font-size: 16px;
  color: #666;
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