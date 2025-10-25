import {ref, computed } from 'vue'
import { resetWorksheet } from '@/composables/resetWorksheet'

export function useIncomeWorksheet(initialForm = null) {
    const farmIncomeWorksheet = ref({
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

    const worksheetTotal = ref(0)
    const isOpen = ref(false)
    const usingWorksheet = ref(false)

    // If worksheet exists and has non-zero values
    const hasWorksheetData = computed (() => {
        if (!usingWorksheet) return false

        const otherFields = Object.entries(farmIncomeWorksheet.value)
        .filter(([key]) => key !== 'sch_f')
        .some(([i, value]) => value !== 0)
        return otherFields
    })

    const openWorksheetModal = () => {
        isOpen.value = true
    }

    const closeWorksheetModal = () => {
        isOpen.value = false
    }

    const handleWorksheetSave = async ({ worksheetData, total }) => {
        // Store the worksheet data and total
        // Stays in FarmIncomeEntry component
        farmIncomeWorksheet.value = { ...worksheetData }
        worksheetTotal.value = total
        usingWorksheet.value = true

        // Update parent form via initialForm reference
        if (initialForm) {
            initialForm.max_elected_farm_income = total
        }

        closeWorksheetModal()
    }

    const handleSingleValue = (event) => {
        if (event.type == 'blur' || event.key == 'Enter') {
            // Reset worksheet
            const singleValue = parseFloat(initialForm.max_elected_farm_income)

            resetWorksheet(farmIncomeWorksheet)
            farmIncomeWorksheet.value.sch_f = singleValue
            worksheetTotal.value = singleValue

            usingWorksheet.value = false
        }
    }

    const loadWorksheet = (worksheetData) => {
        if (!worksheetData) return 

        Object.assign(farmIncomeWorksheet.value, worksheetData)

        // Calculate Total
        worksheetTotal.value = Object.values(worksheetData).reduce((sum, val) => sum + (parseFloat(val) || 0), 0)

        // Check if using worksheet
        const hasOtherValues = Object.entries(worksheetData)
            .filter(([key]) => key !== 'sch_f')
            .some(([, value]) => value !== 0)
        
        usingWorksheet.value = hasOtherValues
    }

    return {
    // State
    farmIncomeWorksheet,
    worksheetTotal,
    isOpen,
    usingWorksheet,
    
    // Computed
    hasWorksheetData,
    
    // Methods
    openWorksheetModal,
    closeWorksheetModal,
    handleWorksheetSave,
    handleSingleValue,
    resetWorksheet,
    loadWorksheet,
  }
}