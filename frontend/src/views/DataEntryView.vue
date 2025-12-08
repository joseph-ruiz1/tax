<!-- DataEntryView.vue -->
<template>
    <div class="form-container">

      <div class="dataset-header">
        <farm-income-entry
        ref="farmIncomeEntryRef"
        v-model="form"
        :saved-worksheet="savedWorksheet"
        />
      </div>

      <!-- Year Navigation-->
      <div class="year-tabs">
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
      <div class="dataset-header">
        <years-data-entry 
        v-model="form"
        :currentYearIndex="currentYearIndex"
        />
        </div>
      <button @click="submitForm" class="submit-btn">Submit</button>
    </div>
    
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { apiService } from '@/services/api.js'
import { useRouter } from 'vue-router'
import { useRoute } from 'vue-router'
import { updateElectionYear } from '@/composables/updateElectionYear'
import YearsDataEntry from '@/components/YearsDataEntry.vue'
import FarmIncomeEntry from '@/components/FarmIncomeEntry.vue'

const route = useRoute()
const router = useRouter()
const loading = ref(true)
const error = ref('')
const farmIncomeEntryRef = ref(null)
const currentYearIndex = ref(0)

const form = reactive({
    name: '',
    max_elected_farm_income: 0,
    qualified_farm_income: 0,
    election_year: 2024,
    tax_years: [
        { year: 2024, filing_status: null, taxable_income: 0, qualified_income: 0, cannot_elect: true, is_electing: true},
        { year: 2023, filing_status: null, taxable_income: 0, qualified_income: 0 },
        { year: 2022, filing_status: null, taxable_income: 0, qualified_income: 0 },
        { year: 2021, filing_status: null, taxable_income: 0, qualified_income: 0 },
    ]
})

updateElectionYear(form, currentYearIndex)

const savedWorksheet = ref({
  sch_f: 0,
  wages: 0,
  sch_c: 0,
  sch_e: 0,
  form_4835: 0,
  ccf: 0,
  se_deduction: 0,
  qbi: 0,
  form_4797: 0,
  sch_d: 0,
})

const submitForm = async () => {
  const worksheetData = farmIncomeEntryRef.value?.getWorksheetData() || null

  const submissionData = {
    name: form.name,
    max_elected_farm_income: form.max_elected_farm_income,
    income_worksheet: worksheetData,
    qualified_farm_income: form.qualified_farm_income,
    tax_years: form.tax_years.map((year, index) => 
      index === 0 
        ? {
            ...year,
            is_electing: true,
            elected_farm_income: form.max_elected_farm_income,
            qualified_farm_income: form.qualified_farm_income
          }
        : year
    )
  }

  const filingstatusMapping = {
    'Single': 'single',
    'Married Filing Jointly': 'MFJ'
  }
  form.tax_years?.forEach(year => {
    if (filingstatusMapping[year.filing_status]) {
        year.filing_status = filingstatusMapping[year.filing_status]
    }
  })
  try {
    const id = route.params.id
    const response = await apiService.patchDataset(id, submissionData)
    router.push(`/datasets/${id}/results`)
  } catch (err) {
      console.error('Failed to update dataset:', err)
  }
}

onMounted(async () => {
  // Fill tax_years with IDs
  try {
        const id = route.params.id
        const response = await apiService.getDatasetDetail(id)

        form.tax_years = form.tax_years.map((year, index) => ({
        ...year,
        id: response?.tax_years?.[index]?.id
  }))
  console.log(form.tax_years)
} catch (err) {
        error.value = 'Failed to fetch tax years'
        console.error('Error fetching tax years', err)
  }
})
</script>

<style scoped>
/* Main container */
.form-container {
  margin: 0 auto;
  padding: 2rem;
  min-height: 100vh;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

/* Dataset Header Section */
.dataset-header {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 16px;
  padding: 1.5rem;
  margin: 0 auto 2rem auto;
  max-width: 700px;
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

.title {
    color: #1a202c;
    font-size: 1rem;
    font-weight: 600;
    display: flex;
}

/* Year Navigation Tabs */
.year-tabs {
  display: flex;
  justify-content: center;
  gap: 0.5rem;
  margin-bottom: 2rem;
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
  transition: transform 0.2s ease, background .2s ease;
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

.title {
  margin: 0;
  font-weight: 600;
  color: #374151;
  font-size: 0.9rem;
}

/* Input Styles */
input {
  padding: .5rem 1.25rem;
  border: 2px solid #e2e8f0;
  border-radius: 12px;
  font-size: 1rem;
  background: white;
  color: #1a202c;
  transition: all 0.3s ease;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  }

select {
  padding: .5rem 1.25rem;
  border: 2px solid #e2e8f0;
  border-radius: 12px;
  font-size: 1rem;
  background: white;
  color: #1a202c;
  transition: all 0.3s ease;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

/* Submit Button */
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
  box-shadow: 0 4px 15px rgba(72, 187, 120, 0.4);
  margin: 0 auto;
  display: block;
}

.submit-btn:hover {
  transform: translateY(-3px);
  box-shadow: 0 6px 20px rgba(72, 187, 120, 0.5);
}

.title-with-info {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}
</style>