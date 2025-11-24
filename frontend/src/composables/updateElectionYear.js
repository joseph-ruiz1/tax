import { watch } from 'vue'

export function updateElectionYear(form, currentYearIndex) {
  function handleElectionYearChange(newYear, oldYear) {
    const delta = newYear - oldYear
    // Shift all existing year values based on delta
    form.tax_years = form.tax_years.map(yearObj => ({
      ...yearObj,
      year: parseFloat(yearObj.year) + delta
    })).filter(yearObj => yearObj.year >= 2018) // Remove years before 2018
  }

  // Set up the watcher
  watch(() => form.election_year, (newYear, oldYear) => {
    handleElectionYearChange(newYear, oldYear)
    currentYearIndex.value = 0
  })

  return {
    handleElectionYearChange
  }
}