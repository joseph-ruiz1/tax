<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useIncomeWorksheet } from '@/composables/useIncomeWorksheet'
import FarmIncomeModal from './FarmIncomeModal.vue'

const props = defineProps({
    modelValue: {
        type: Object,
        required: true
    }
})

const emit = defineEmits(['update:modelValue'])

const router = useRouter()

// Create local form that syncs with parent via v-model
const form = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

const {
  farmIncomeWorksheet,
  isOpen,
  usingWorksheet,
  hasWorksheetData,
  openWorksheetModal,
  handleWorksheetSave,
  handleSingleValue,
} = useIncomeWorksheet(form.value)

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

      <div class="field-container">
        <div class="title-with-info">
          <p class="title">Max Elected Farm Income</p>
          <button type="button" class="open-modal-btn" @click="openWorksheetModal" aria-label="More information">
            <img src="../../src/assets/modalIcon.png" alt="Open worksheet">
          </button>
        </div>
        <input
          type="number"
          v-model="form.max_elected_farm_income" 
          placeholder="Enter Farm income" 
          :disabled="hasWorksheetData"
          @blur="handleSingleValue"
          @keydown.enter="handleSingleValue"
        >
        <span v-if="hasWorksheetData" class="worksheet-indicator">
          <p>⚠️ Using Worksheet</p>
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
        <input v-model="form.qualified_farm_income" placeholder="Farm income cap gains" required type="number">
      </div>
    </form>

    <!-- Modal stays within component -->
    <farm-income-modal
      :is-open="isOpen"
      :worksheet="farmIncomeWorksheet"
      @close="isOpen = false"
      @save="handleWorksheetSave"
    />
  </div>
</template>

<style scoped>
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
</style>