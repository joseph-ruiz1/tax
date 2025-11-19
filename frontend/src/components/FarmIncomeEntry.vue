<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useIncomeWorksheet } from '@/composables/useIncomeWorksheet'
import FarmIncomeModal from './FarmIncomeModal.vue'

const router = useRouter()

// const modelValue = defineModel('modelValue', { required: true, type: object })
// const savedWorksheet = defineModel('savedWorksheet', { required: false, type: object})

const electionYears = [2025, 2024, 2023, 2022]

const props = defineProps({
    modelValue: {
        type: Object,
        required: true
    },
    savedWorksheet: {
        type: Object,
        default: null
    }
})

const emit = defineEmits(['update:modelValue'])

// Create local form that syncs with parent via v-model so we aren't directly mutating the prop
const form = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

const {
  farmIncomeWorksheet,
  isOpen,
  hasWorksheetData,
  openWorksheetModal,
  closeWorksheetModal,
  handleWorksheetSave,
  handleSingleValue,
  loadWorksheet,
} = useIncomeWorksheet(form.value)

// Load on mount
if (props.savedWorksheet) {
    loadWorksheet(props.savedWorksheet)
}

// Expose worksheet so parent can access it since componenets automatically closed by default
defineExpose({
    getWorksheetData: () => farmIncomeWorksheet.value
})

const toDashboard = async () => {
router.push('/')
}
</script>

<template>
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

      <div class="field-container-row">
        <div class="title-with-info">
          <p class="title">Election Year:</p>
        </div>
        <div class="radio-group">
          <div v-for="year in electionYears" :key="year" class="radio-option">
            <input 
              type="radio" 
              :id="`year-${year}`"
              v-model="form.election_year" 
              :value="year"
              name="election_year"
              required
            >
            <label :for="`year-${year}`">{{ year }}</label>
          </div>
        </div>
      </div>

      <div class="field-container">
        <div class="title-with-info">
          <p class="title">Max Elected Farm Income</p>
          <button type="button" class="open-modal-btn" @click="openWorksheetModal" aria-label="Open worksheet">
            <img src="../../src/assets/modalIcon.png" alt="Open worksheet">
          </button>
        </div>
        <input
          type="number"
          v-model.number="form.max_elected_farm_income" 
          placeholder="Enter Farm income" 
          :disabled="hasWorksheetData"
          @blur="handleSingleValue"
          @keydown.enter="handleSingleValue"
        >
        <span v-if="hasWorksheetData" class="worksheet-indicator">
          ⚠️ Using Worksheet
        </span>
      </div>

      <div class="field-container">
        <div class="title-with-info">
          <p class="title">Qualified Farm Income</p>
          <button type="button" class="info-btn" aria-label="More information">
            <span class="info-icon">i</span>
            <span class="tooltip">The portion of the total elected farm income that is made up of capital gains. Calculated as long term farm gains - short term farm loss. 1250 gains are currently not supported.</span>
          </button>
        </div>
        <input v-model.number="form.qualified_farm_income" placeholder="Farm income cap gains" required type="number">
      </div>
    </form>

    <!-- Modal stays within component -->
    <farm-income-modal
      :is-open="isOpen"
      :worksheet="farmIncomeWorksheet"
      @close="closeWorksheetModal"
      @save="handleWorksheetSave"
    />
  </div>
</template>

<style scoped>
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
  margin-bottom: .75rem;
}

.dataset-title h1 {
  color: #1a202c;
  font-size: 1.5rem;
  font-weight: 700;
  margin: 0;
}

.to-dashboard-btn {
  position: absolute;
  left: 0;
  background: rgba(46, 39, 53, 0.1);
  border: 1px solid rgba(0, 0, 0, 0.2);
  color: #1a202c;
  padding: 0.3rem 0.5rem;
  border-radius: 8px;
  font-weight: 600;
  font-size: 0.7rem;
  cursor: pointer;
  transition: all 0.3s ease;
  white-space: nowrap;
}

.to-dashboard-btn:hover {
  background: rgba(46, 39, 53, 0.2);
  transform: translateX(-2px);
}

.dataset-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.field-container {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.field-container-row {
  display: flex;
  flex-direction: row;
  gap: 0.5rem;
  align-items: center;
  flex-wrap: wrap;
}

.title {
  color: #1a202c;
  font-size: 0.95rem;
  font-weight: 600;
  margin: 0;
}

.title-with-info {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-shrink: 0;
  white-space: nowrap;
}

.field-container input {
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

.field-container input:disabled {
  background: #f7fafc;
  cursor: not-allowed;
  opacity: 0.6;
}

.field-container input:focus:not(:disabled) {
  border-color: #4c51bf;
  box-shadow: 0 0 0 3px rgba(76, 81, 191, 0.1);
}

.field-container input::placeholder {
  color: #a0aec0;
}

.radio-group {
  display: flex;
  gap: .75rem;
  align-items: center;
  flex-wrap: wrap;
  min-width: 0;
}

.radio-option {
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.radio-option input[type="radio"] {
  width: auto;
  padding: 0;
  margin: 0;
  cursor: pointer;
}

.radio-option label {
  cursor: pointer;
  margin: 0;
  white-space: nowrap;
  color: black;
}

.open-modal-btn {
  padding: 0rem;
  background: rgba(76, 81, 191, 0.1);
  border: 1px solid rgba(76, 81, 191, 0.3);
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.open-modal-btn img {
  width: 22px;
  height: 22px;
  display: block;
}

.open-modal-btn:hover {
  background: rgba(76, 81, 191, 0.2);
  transform: scale(1.05);
}

.worksheet-indicator {
  color: #d97706;
  font-size: 0.875rem;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 0.25rem;
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
</style>