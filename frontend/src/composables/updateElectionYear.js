import { watch } from 'vue'

export function updateElectionYear(form, currentYearIndex) {
  function handleElectionYearChange(newYear, oldYear) {
    if (!newYear || !oldYear || newYear === oldYear) {
      return;
    }

    const delta = parseInt(newYear, 10) - parseInt(oldYear, 10)
    console.log('Delta:', delta)
    
    // Shift all existing year values based on delta
    form.tax_years = form.tax_years.map(yearObj => ({
      ...yearObj,
      year: String(parseInt(yearObj.year, 10) + delta) // Cast back to string
    })).filter(yearObj => parseInt(yearObj.year, 10) >= 2018) // Parse for comparison
    
    console.log('After:', form.tax_years)
  }
  
  watch(() => form.election_year, (newYear, oldYear) => {
    handleElectionYearChange(newYear, oldYear)
    currentYearIndex.value = 0
  })

  return {
    handleElectionYearChange
  }
}