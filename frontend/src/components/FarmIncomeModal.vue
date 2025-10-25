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

// Populates modal upon GET; sync with prop changes
watch(() => props.worksheet, (newValue) => {
  if (newValue) {
    localWorksheet.value = { ...newValue}
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
  max-height: 60vh;
  overflow-y: auto;
}

.field-container {
  margin-bottom: 1rem;
  display: flex;
  align-items: center;
  gap: 1rem;
}

.field-container:last-child {
  margin-bottom: 0;
}

.title-with-info {
  flex: 1;
  min-width: 0;
}

.title {
  font-weight: 600;
  color: #1a202c;
  font-size: 0.95rem;
  margin: 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.field-container input {
  width: 180px;
  flex-shrink: 0;
  padding: 0.6rem 1rem;
  border: 2px solid #e2e8f0;
  border-radius: 8px;
  font-size: 1rem;
  background: white;
  color: #1a202c;
  transition: all 0.3s ease;
  outline: none;
}

.field-container input:focus {
  border-color: #4c51bf;
  box-shadow: 0 0 0 3px rgba(76, 81, 191, 0.1);
}

.field-container input::placeholder {
  color: #a0aec0;
  font-size: 0.875rem;
}

/* Footer styling */
.footer-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  gap: 1rem;
  flex-wrap: wrap;
}

.footer-total {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.footer-total label {
  margin: 0;
  font-weight: 600;
  color: #1a202c;
  font-size: 1rem;
}

.total-display {
  font-size: 1.25rem;
  font-weight: 700;
  color: #4c51bf;
}

.button-group {
  display: flex;
  gap: 0.75rem;
  margin-left: auto;
}

.btn-primary,
.btn-secondary {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  font-size: 0.95rem;
  transition: all 0.2s ease;
  white-space: nowrap;
}

.btn-primary {
  background: linear-gradient(135deg, #4c51bf 0%, #434190 100%);
  color: white;
  box-shadow: 0 2px 8px rgba(76, 81, 191, 0.3);
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(76, 81, 191, 0.4);
}

.btn-secondary {
  background: #e5e7eb;
  color: #374151;
}

.btn-secondary:hover {
  background: #d1d5db;
}

/* Responsive adjustments */
@media (max-width: 640px) {
  .field-container {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }

  .field-container input {
    width: 100%;
  }

  .footer-actions {
    flex-direction: column;
    align-items: stretch;
  }

  .footer-total {
    justify-content: space-between;
    width: 100%;
  }

  .button-group {
    margin-left: 0;
    width: 100%;
  }

  .button-group button {
    flex: 1;
  }
}
</style>