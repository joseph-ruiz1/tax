import { watch } from 'vue'
import { correctTaxYears } from './correctTaxYears'

export function updateElectionYear(form, currentYearIndex) {
  function handleElectionYearChange(newYear, oldYear) {
    if (!newYear || !oldYear || newYear === oldYear) {
      return
    }

    const delta = parseInt(newYear, 10) - parseInt(oldYear, 10)
    
    // Shift all existing year values based on delta
    form.tax_years = form.tax_years.map(yearObj => ({
      ...yearObj,
      year: String(parseInt(yearObj.year, 10) + delta)
    })).filter(yearObj => parseInt(yearObj.year, 10) >= 2018)
    
    // Correct all tax years if election year doesn't match first tax year
    if (form.election_year != parseInt(form.tax_years[0].year)) {
      correctTaxYears(form.election_year, form.tax_years)
    }
  }
 
  watch(() => form.election_year, (newYear, oldYear) => {
    handleElectionYearChange(newYear, oldYear)
    currentYearIndex.value = 0
  })

  return {
    handleElectionYearChange
  }
}