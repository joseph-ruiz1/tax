export function correctTaxYears(election_year, tax_years) {
    const correction = election_year - parseInt(tax_years[0].year)
    tax_years = tax_years.map(yearObj => ({
      ...yearObj,
      year: String(parseInt(yearObj.year) + correction),
  }))
  return tax_years
}