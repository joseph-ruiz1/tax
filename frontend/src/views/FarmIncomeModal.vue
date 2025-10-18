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
            <div class="footer-total">
                <label><strong>Total:</strong></label>
                <div class="total-display">{{totalFarmIncome }}</div>
            </div>
          <button @click="handleSave" class="btn-primary">Save</button>
          <button @click="handleClose" class="btn-secondary">Cancel</button>
        </template>
      </modal-content>
    </div>
  </Teleport>
</template>

<script setup>
import { ref, watch, computed, onMounted } from 'vue'
import ModalContent from './ModalContent.vue'

const props = defineProps({
  isOpen: {
    type: Boolean,
    required: true
  },
  worksheet: {
    type: Object,
    default: null
  }
});

const emit = defineEmits(['close', 'save'])

const fieldDefinitions = [
    {
        key: 'schedule_f',
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

const initializeWorksheet = () => {
    const form = {}
    fieldDefinitions.forEach(field => {
        form[field.key] = 0
    })
    return form
}

const localWorksheet = ref(initializeWorksheet())

// Calculate total
const totalFarmIncome = computed(() => {
    return Object.values(localWorksheet.value).reduce((sum, value) => {
        const numValue = parseFloat(value) || 0
        return sum + numValue
    }, 0)
})

// Populates modal upon GET
watch(() => props.worksheet, (newVal) => {
  if (newVal) {
    localWorksheet.value = { ...newVal}
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
    total: totalFarmIncome
  })
  emit('close')
}


</script>

<style scoped>
.field-container {
  margin-bottom: 1.5rem;
}

.field-container:last-child {
  margin-bottom: 0;
}

.title-with-info {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
}

.title {
  font-weight: 600;
  color: #1a202c;
  font-size: 0.95rem;
  margin: 0;
}

.field-container input {
  width: 100%;
  padding: 0.75rem 1rem;
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

.btn-primary {
  padding: 0.75rem 1.5rem;
  background: #3b82f6;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  transition: background 0.2s ease;
}

.btn-primary:hover {
  background: #2563eb;
}

.btn-secondary {
  padding: 0.75rem 1.5rem;
  background: #e5e7eb;
  color: #374151;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  transition: background 0.2s ease;
}

.btn-secondary:hover {
  background: #d1d5db;
}
</style>