<!-- DataEntryView.vue -->
<template>
    <div class="form-container">
      <farm-income-entry
      ref="farmIncomeEntryRef"
      v-model="form"
      :saved-worksheet="savedWorksheet"
      />

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

      <!-- Current Year Form -->
      <div class="dataset-header">
          <h1>Tax Year {{ form.tax_years[currentYearIndex].year }}</h1>

          <form class="dataset-form">
            <div class="form-group">
              <p class="title">Filing Status</p>
              <select v-model="form.tax_years[currentYearIndex].filing_status" required>
                <option disabled value="">Filing Status</option>
                <option v-for="opt in filingStatusOptions" :key="opt.value" :value="opt.value">
                  {{ opt.label }}
                </option>
              </select>
            </div>

            <div class="form-group">
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

            <div class="form-group">
              <div class="title-with-info">
                <p class="title">Qualified Income</p>
                <button type="button" class="info-btn" aria-label="More information">
                  <span class="info-icon">i</span>
                  <span class="tooltip">Long term capital gains + qualified dividends.</span>
                </button>
              </div>
              <input
              v-model.number="form.tax_years[currentYearIndex].qualified_income"
              placeholder="Taxable income"
              required
              type="number"
              >
            </div>
          </form>
      </div>
      <button @click="submitForm" class="submit-btn">Submit</button>
    </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { apiService } from '@/services/api.js'
import { useRouter } from 'vue-router'
import { useRoute } from 'vue-router'
import { filingStatusOptions } from '@/composables/filingstatusOptions'

import FarmIncomeEntry from '@/components/FarmIncomeEntry.vue'

const route = useRoute()
const router = useRouter()
const loading = ref(true)
const error = ref('')

const currentYearIndex = ref(0)

const form = reactive({
    name: '',
    max_elected_farm_income: 0,
    qualified_farm_income: 0,
    tax_years: [
        { year: 2024, filing_status: null, taxable_income: 0, qualified_income: 0 },
        { year: 2023, filing_status: null, taxable_income: 0, qualified_income: 0 },
        { year: 2022, filing_status: null, taxable_income: 0, qualified_income: 0 },
        { year: 2021, filing_status: null, taxable_income: 0, qualified_income: 0 },
    ]
})

const farmIncomeEntryRef = ref(null)
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
    tax_years: form.tax_years
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
</script>

<style scoped>
/* Main container */
.form-container {
  margin: 0 auto;
  padding: 2rem;
  background: linear-gradient(135deg, #434b6f 0%, #2e2735 100%);
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

.dataset-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  max-width: 500px;
  margin: 0 auto;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
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

.form-group {
  display: flex;
  flex-direction: column;
  gap: .5rem;
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

input:focus, select:focus {
  outline: none;
  border-color: #4c51bf;
  box-shadow: 0 0 0 3px rgba(76, 81, 191, 0.1);
  transform: translateY(-1px);
}

input::placeholder {
  color: #a0aec0;
  font-weight: 400;
}

/* Navigation Buttons */
.navigation {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
}

.navigation button {
  padding: 0.75rem 1.5rem;
  border-radius: 10px;
  border: none;
  font-weight: 600;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.navigation button:not(.submit-btn) {
  background: #f7fafc;
  color: #4a5568;
  border: 2px solid #e2e8f0;
}

.navigation button:not(.submit-btn):hover:not(:disabled) {
  background: #edf2f7;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.navigation button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none !important;
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

.info-btn {
  position: relative;
  background: rgba(59, 130, 246, 0.1);
  border: 1px solid rgba(59, 130, 246, 0.3);
  border-radius: 50%;
  width: 20px;
  height: 20px;
  padding: 0;
  cursor: help;
  transition: transform 0.2s ease, background .2s ease;
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
  transition: opacity 0.2s ease, visibility .2s ease;
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

.title-with-info {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}
</style>