from .calculations import tax_brackets
from .models import TaxYearData, AdjustedTaxData, CalculationIteration, ScheduleJForm
from .utils import chunker

from decimal import Decimal


class TaxCalculation:
    def __init__(self, tax_data: TaxYearData):
        self.tax_data = tax_data

    def find_ordinary_bracket(self):
        
        for rate, (lower, upper, prior_tax) in tax_brackets.ORDINARY_TAX_TABLES[self.tax_data.year][self.tax_data.filing_status].items():
            self.tax_data.taxable_ordinary = max(self.tax_data.taxable_income - self.tax_data.qualified_income, 0)

            if lower <= self.tax_data.taxable_ordinary <= upper:
                self.tax_data.ordinary_rate = Decimal(rate)
                self.tax_data.lower_ordinary_bound = lower
                self.tax_data.upper_ordinary_bound = upper
                self.tax_data.prior_ordinary_bracket_tax = prior_tax
                return
            
        print("Income too large or negative") 
        return 1

    def find_ordinary_tax(self):
        self.tax_data.ordinary_tax = ((self.tax_data.taxable_ordinary - self.tax_data.lower_ordinary_bound) * self.tax_data.ordinary_rate) + self.tax_data.prior_ordinary_bracket_tax     
        return
        
    def find_qualified_tax(self):
        #intialize some variables for ease of use
        year = self.tax_data.year
        filing_status = self.tax_data.filing_status
        taxable_income = self.tax_data.taxable_income
        taxable_ordinary = self.tax_data.taxable_ordinary
        qualified_income = self.tax_data.qualified_income

        # if taxable income than 0% bracket, all at 0%
        if taxable_income <= tax_brackets.QUALIFIED_TAX_TABLES[year][filing_status]["0"][1]:            
            qualified_tax = tax_brackets.QUALIFIED_TAX_TABLES[year][filing_status]["0"][1] * 0

        # see if taxable exceeds 15% bracket                                  
        elif taxable_income < tax_brackets.QUALIFIED_TAX_TABLES[year][filing_status][".15"][1]:
            
            # Edge case where more qualified income than ordinary income. Taxable income falls within 15% bracket.
            if qualified_income >= taxable_income:
                qualified_tax = (taxable_income - tax_brackets.QUALIFIED_TAX_TABLES[year][filing_status]["0"][1]) * Decimal(.15)
                
            else:
            # tax at 0% = 0% bracket - ordinary          
                zero_bracket = max((tax_brackets.QUALIFIED_TAX_TABLES[year][filing_status]["0"][1] - taxable_ordinary), 0)
                #tax at 15% = qualified - 0% tax        
                fifteen_bracket = qualified_income - zero_bracket
                qualified_tax = (zero_bracket * 0) + (fifteen_bracket * Decimal(.15))

        # taxable above 15% bracket, should be minimum 15%
        elif taxable_ordinary >= taxable_income:
            #0% bracket - ordinary: cases where high taxable and high qualified
            zero_bracket = max(tax_brackets.QUALIFIED_TAX_TABLES[year][filing_status]["0"][1] - taxable_ordinary, 0)

            #15% bracket - tax at zero (if any) - ordinary  
            fifteen_bracket = max(tax_brackets.QUALIFIED_TAX_TABLES[year][filing_status][".15"][1] - zero_bracket - taxable_ordinary, 0)

            #find amount at 20%
            twenty_bracket = qualified_income - fifteen_bracket - zero_bracket                                          
            qualified_tax = (zero_bracket * 0) + (fifteen_bracket * Decimal(.15)) + (twenty_bracket * Decimal(.20))

        # Edge case where more qualified income than ordinary income and Taxable Income falls beyond 20%.
        else:
            # Fill 0 bracket
            zero_bracket = max(tax_brackets.QUALIFIED_TAX_TABLES[year][filing_status]["0"][1], 0)

            # Fill 15 bracket
            fifteen_bracket = max(tax_brackets.QUALIFIED_TAX_TABLES[year][filing_status][".15"][1] - zero_bracket, 0)

            # taxable income - prior brackets
            twenty_bracket = taxable_income - fifteen_bracket - zero_bracket                                          
            qualified_tax = (zero_bracket * 0) + (fifteen_bracket * Decimal(.15)) + (twenty_bracket * Decimal(.20))
        
        self.tax_data.qualified_tax = max(qualified_tax, 0)
 
    def find_total_tax(self):
        self.tax_data.total_tax = max(self.tax_data.ordinary_tax + self.tax_data.qualified_tax, 0) 

    def calculate(self, save=False): 
        self.find_ordinary_bracket()
        self.find_ordinary_tax()
        self.find_qualified_tax()
        self.find_total_tax()
        if save:
            self.tax_data.save()
        
class ScheduleJResultContainer:
    def __init__(self, schedule_j_form: ScheduleJForm,
                 adjusted_current_year: AdjustedTaxData,
                 adjusted_base1: AdjustedTaxData,
                 adjusted_base2: AdjustedTaxData,
                 adjusted_base3: AdjustedTaxData,
                 elected_farm_income: float,
                 elected_farm_qualified: float):
        self.schedule_j_form = schedule_j_form
        self.adjusted_current = adjusted_current_year
        self.adjusted_base1 = adjusted_base1
        self.adjusted_base2 = adjusted_base2
        self.adjusted_base3 = adjusted_base3
        self.elected_farm_income = elected_farm_income
        self.elected_farm_qualified = elected_farm_qualified

    def to_dict(self):
        return {
            "schedule_j_form": self.schedule_j_form,
            "adjusted_current": self.adjusted_current.to_dict(),
            "adjusted_base1": self.adjusted_base1.to_dict(),
            "adjusted_base2": self.adjusted_base2.to_dict(),
            "adjusted_base3": self.adjusted_base3.to_dict(),
            "elected_farm_income": self.elected_farm_income,
            "elected_farm_qualified": self.elected_farm_qualified, }


class ScheduleJCalculation:
    def __init__(self, current_year: TaxYearData, base_year_1: TaxYearData, base_year_2: TaxYearData, 
                 base_year_3: TaxYearData, iteration: CalculationIteration):
        self.current_year = current_year
        self.base_years = {2021: base_year_1, 2022: base_year_2, 2023: base_year_3}
        self.iteration = iteration

    def schedule_j_calculation(self, elected_farm_income: Decimal, elected_cap_gains: Decimal) -> ScheduleJResultContainer:
        """
        Runs calculation and returns ResultContainer object, does not directly save to DB
        """
        if not isinstance(elected_farm_income, Decimal):
            raise TypeError("Not a Decimal")
        if not isinstance(elected_cap_gains, Decimal):
            raise TypeError("Not a Decimal")

        # Create ScheduleJForm and AdjustedTaxData but do not save to DB yet, will be done in bulk create
        output = ScheduleJForm(iteration=self.iteration)
        adjusted_current_year = AdjustedTaxData.from_base(self.current_year, self.iteration, save=False)

        # Create new instances for adjusted base years
        adjusted_bases = {year: AdjustedTaxData.from_base(base, self.iteration, save=False) for year, base in self.base_years.items()}

      

        output.line_1 = self.current_year.taxable_income
        output.line_2a = elected_farm_income
        output.line_2b = elected_cap_gains
        output.line_3 = output.line_1 - output.line_2a

        # Intitialize elected farm income amounts and find 1/3 of each
        total_elected =  output.line_2a
        elected_qualified = output.line_2b
        elected_ordinary =  total_elected - elected_qualified
        distribute_total_elected = total_elected / 3
        distribute_farm_ordinary = elected_ordinary / 3
        distribute_farm_qualified = elected_qualified / 3

        output.line_6 = distribute_total_elected
        output.line_10 = distribute_total_elected
        output.line_14 = distribute_total_elected
        # Copy 2024 numbers from baseline and decrease incomes by elected amounts
        adjusted_current_year.taxable_income = self.current_year.taxable_income - total_elected
        adjusted_current_year.qualified_income = self.current_year.qualified_income - elected_qualified
        adjusted_current_year.taxable_ordinary = self.current_year.taxable_ordinary - elected_ordinary

        # Find tax on 2024 taxable less elected farm income
        TaxCalculation(adjusted_current_year).calculate()
        output.line_4 = adjusted_current_year.total_tax

        # Distribute elected farm income to each year, calculate tax
        update_lines = {
                2021: ['line_5', 'line_7', 'line_8'],
                2022: ['line_9', 'line_11', 'line_12'],
                2023: ['line_13', 'line_15', 'line_16']
            }

        for year, (base_income, adjusted_income, calculate_tax) in update_lines.items():
                base = self.base_years[year]
                adjusted = adjusted_bases[year]

                # Pull base income from given tax info
                base_ordinary_income =  int(base.taxable_ordinary)
                base_qualified_income = int(base.qualified_income)
                base_taxable_income = int(base.taxable_income)

                setattr(output, base_income, base_taxable_income)

                # Increase income by 1/3
                adjusted_ordinary_income = base_ordinary_income + distribute_farm_ordinary
                adjusted_qualified_income = base_qualified_income + distribute_farm_qualified
                adjusted_taxable_income = base_taxable_income + distribute_total_elected

                # Place increased income total taxable income into Sch J
                setattr(output, adjusted_income, adjusted_taxable_income) 

                # Increase ordinary, qualified, taxable income with respective elected farm incomes
                adjusted.taxable_ordinary = adjusted_ordinary_income
                adjusted.qualified_income = adjusted_qualified_income
                adjusted.taxable_income = adjusted_taxable_income

                TaxCalculation(adjusted).calculate(save=False)
                setattr(output, calculate_tax, adjusted.total_tax)

        output.line_17 = output.line_4 + output.line_8 + output.line_12 + output.line_16
        output.line_18 = output.line_17 

         # Get baseline tax from each year
        base_tax = {
                2021: 'line_19',
                2022: 'line_20',
                2023: 'line_21',
            }

        for year, (tax_amount) in base_tax.items():
            setattr(output, tax_amount, self.base_years[year].total_tax)

        # Total base tax from prior years
        output.line_22 = output.line_19 + output.line_20 + output.line_21

        # Schedule J tax for 2024
        output.line_23 = output.line_18 - output.line_22

        return ScheduleJResultContainer(
            schedule_j_form=output,
            adjusted_current_year=adjusted_current_year,
            adjusted_base1=adjusted_bases[2021],
            adjusted_base2=adjusted_bases[2022],
            adjusted_base3=adjusted_bases[2023],
            elected_farm_income=elected_farm_income,
            elected_farm_qualified=elected_qualified)


class ScheduleJOptimization:
    def __init__(self, current_year: TaxYearData, base_year_1: TaxYearData, base_year_2: TaxYearData, 
                 base_year_3: TaxYearData, elected_farm_income: float, elected_farm_qualified: float, dataset: TaxYearData):
        self.current_year = current_year
        self.base_year_1 = base_year_1
        self.base_year_2 = base_year_2
        self.base_year_3 = base_year_3
        self.elected_farm_income = elected_farm_income
        self.elected_farm_qualified = elected_farm_qualified
        self.dataset = dataset


    def optimize_sch_j(self, elected_farm_income, elected_farm_qualified):
        """
        Create lists we can temporarily store objects in, then bulk create
        """
        iterations = []
        forms = []
        all_adjusted_years = []

        current_total_elected = elected_farm_income
        current_qualified_elected = elected_farm_qualified
        current_ordinary_elected = elected_farm_income - elected_farm_qualified

        # Find percentage so we can decrease proportionally
        ordinary_percentage = current_ordinary_elected / current_total_elected
        qualified_percentage = current_qualified_elected / current_total_elected        

        while current_total_elected >= 500:
            # Initialize CalculationIteration
            iteration = CalculationIteration(dataset=self.dataset)
            
            iterations.append(iteration)

            instance = (ScheduleJCalculation(self.current_year, self.base_year_1, self.base_year_2, self.base_year_3, iteration)
                        .schedule_j_calculation(current_total_elected, current_qualified_elected))
            forms.append(instance.schedule_j_form)

            current_total_elected -= 500
            current_ordinary_elected -= 500 * ordinary_percentage
            current_qualified_elected -= 500 * qualified_percentage

        created_iterations = CalculationIteration.objects.bulk_create(iterations)
        # Ensure SQLite populates IDs
        if not all(iter.id for iter in created_iterations):
            # fallback: reload from DB
            created_iterations = list(
                CalculationIteration.objects.filter(dataset=self.dataset).order_by("id")
            )[-len(iterations):]
        for form, iteration in zip(forms, created_iterations):
            form.iteration = iteration
        ScheduleJForm.objects.bulk_create(forms)
        
        for adjusted, iteration in zip(chunker(all_adjusted_years, 4), created_iterations):
            for i in adjusted:
                i.iteraion = iteration
        return
