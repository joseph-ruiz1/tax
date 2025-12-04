<template>
<!-- Current Year Form -->
  <div class="dataset-title">
    <h1>Tax Year {{ form.tax_years[props.currentYearIndex].year }}</h1>
  </div>

  <form class="dataset-form">
    <div class="field-container">
      <div class="title-with-info">
          <p class="title">Filing Status</p>
      </div>
      <select v-model="form.tax_years[props.currentYearIndex].filing_status" required>
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
            v-model.number="form.tax_years[props.currentYearIndex].taxable_income"
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
            v-model.number="form.tax_years[props.currentYearIndex].qualified_income"
            placeholder="Qualified income"
            required
            type="number"
        >
    </div>
    
    <div v-if="!form.tax_years[props.currentYearIndex].cannot_elect" class="field-container">
        <div class="title-with-info">
        <p class="title">Schedule J filed?</p>
        <input
            type="checkbox"
            v-model="form.tax_years[props.currentYearIndex].is_electing"
        >
        </div>
    </div>

    <div v-if="form.tax_years[props.currentYearIndex].is_electing && !form.tax_years[props.currentYearIndex].cannot_elect" class="field-container">
        <div class="title-with-info">
        <p class="title">Elected Farm Income</p>
        </div>
        <input
            v-model.number="form.tax_years[props.currentYearIndex].elected_farm_income"
            required
            type="number"
            value=0
        >
    </div>

    <div v-if="form.tax_years[props.currentYearIndex].is_electing && !form.tax_years[props.currentYearIndex].cannot_elect" class="field-container">
        <div class="title-with-info">
        <p class="title">Qualified Farm Income</p>
        </div>
        <input
            v-model.number="form.tax_years[props.currentYearIndex].qualified_farm_income"
            required
            type="number"
            value=0
        >
    </div>
  </form>
</template>

<script setup>
import { computed } from 'vue'
import { filingStatusOptions } from '@/composables/filingstatusOptions'

const props = defineProps({
  modelValue: {
    type: Object,
    required: true
  },
  currentYearIndex: {
    type: Number,
    required: true
  }
})

const emit = defineEmits(['update:modelValue'])

const form = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})
</script>

<style scoped>
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