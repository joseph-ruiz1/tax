<template>
  <Teleport to="body">
    <div v-if="isOpen">
      <modal-content
        @close="handleClose"
        title="Farm Income Worksheet"
        :close-on-overlay-click="true"
      >
        <!-- Main content -->
        <div class="worksheet-form">
          <!-- Loop thru all fields -->
            <div
            v-for="field in fieldDefinitions"
            :key="field.key"
            class="field-container"
            >
                <div class="title-with-info">
                    <p class="title">{{ field.label }}</p>
                </div>
                <input 
                v-model.number="localWorksheet[field.key]" 
                :placeholder="field.placeholder" 
                type="number"
                />
            </div>
        </div>
        
        <!-- Footer with action buttons -->
        <template #footer>
          <div class="footer-actions">
            <div class="footer-total">
              <label><strong>Total:</strong></label>
              <div class="total-display">{{ totalFarmIncome }}</div>
            </div>
            <div class="button-group">
              <button @click="handleClose" class="btn-secondary">Cancel</button>
              <button @click="handleSave" class="btn-primary">Save</button>
            </div>
          </div>
        </template>
      </modal-content>
    </div>
  </Teleport>
</template>

<script setup>
import { ref, watch, computed } from 'vue'
import ModalContent from '../components/ModalContent.vue'

const props = defineProps({
  isOpen: {
    type: Boolean,
    required: true
  },
  worksheet: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['close', 'save'])

const fieldDefinitions = [
    {
        key: 'sch_f',
        label: 'Schedule F',
        placeholder: "Schedule F Net Profit",
    },
    {
        key: 'wages',
        label: 'Wages',
        placeholder: 'Farm Wages Received',
    },
     {
        key: 'sch_c',
        label: 'Schedule C',
        placeholder: 'Schedule C Farm Income',
    },
    {
        key: 'sch_e',
        label: 'Schedule E',
        placeholder: 'Schedule E Farm Income',
    },
    {
        key: 'form_4835',
        label: 'Form 4835',
        placeholder: 'Farm Rental Income',
    },
    {
        key: 'ccf',
        label: 'Capital Construction Fund',
        placeholder: 'Capital Construction Fund',
    },
    {
        key: 'se_deduction',
        label: '1/2 SE Deduction',
        placeholder: 'Deductible Half of SE Tax',
    },
    {
        key: 'qbi',
        label: 'QBI Deduction',
        placeholder: 'Farm Associated QBI Deduction',
    },
    {
        key: 'form_4797',
        label: 'Form 4797',
        placeholder: 'Ordinary Farm Gain/Loss',
    },
    {
        key: 'sch_d',
        label: 'Schedule D',
        placeholder: 'Farm Capital Gains',
    },
]

const localWorksheet = ref({...props.worksheet})

// Calculate total
const totalFarmIncome = computed(() => {
    return Object.values(localWorksheet.value).reduce((sum, value) => {
        const numValue = parseFloat(value) || 0
        return sum + numValue
    }, 0)
})

// Populates modal upon GET
watch(() => props.worksheet, (newValue) => {
  if (newValue) {
    localWorksheet.value = { ...newValue}
  } else {
    localWorksheet.value = initializeWorksheet()
  }
}, {immediate: true, deep: true})

const handleClose = () => {
  emit('close')
}

const handleSave = () => {
  emit('save', {
    worksheetData: {...localWorksheet.value},
    total: totalFarmIncome.value
  })
  emit('close')
}
</script>

<style scoped>
.worksheet-form {
  padding: 0.5rem 0;
}

.field-container {
  margin-bottom: .5rem;
  display: flex;
  align-items: center;
  gap: 1rem;
}

.field-container:last-child {
  margin-bottom: 0;
}

.title-with-info {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-shrink: 0;
}

.title {
  font-weight: 600;
  color: #1a202c;
  font-size: 0.95rem;
  margin: 0;
  white-space: nowrap;
}

.field-container input {
  width: 100%;
  max-width: 175px;
  margin-left: auto;
  padding: 0.5rem 1rem;
  border: 2px solid rgba(0, 0, 0, 0.1);
  border-radius: 8px;
  font-size: 1rem;
  background: white;
  transition: all 0.3s ease;
  outline: none;
}

.field-container input:focus {
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

/* Footer styling - works with parent modal-footer */
.footer-total {
  display: flex;
  align-items: center;
  gap: .25rem;
  white-space: nowrap;
}

.footer-total label {
  margin: 0;
  font-weight: 600;
  color: #1a202c;
  font-size: 0.95rem;
}

.total-display {
  font-size: 1.1em;
  font-weight: 700;
  color: #000000;
}

.footer-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.button-group {
  display: flex;
  gap: 0.75rem;
  margin-left: auto;
}

.btn-primary {
  padding: 0.75rem 1.5rem;
  background: #3b82f6;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  font-size: 0.95rem;
  transition: all 0.2s ease;
}

.btn-primary:hover {
  background: #2563eb;
  transform: translateY(-1px);
}

.btn-secondary {
  padding: 0.75rem 1.5rem;
  background: #e5e7eb;
  color: #374151;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  font-size: 0.95rem;
  transition: all 0.2s ease;
}

.btn-secondary:hover {
  background: #d1d5db;
}

.btn-clear {
  padding: 0.75rem 1.5rem;
  background: #ef4444;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  font-size: 0.95rem;
  transition: all 0.2s ease;
}

.btn-clear:hover {
  background: #dc2626;
  transform: translateY(-1px);
}
</style>
