from .calculations import tax_brackets
from .models import TaxYearData, AdjustedTaxData, CalculationIteration, ScheduleJForm

from decimal import Decimal

# CONSIDER MAKING SAVE FIELD AN ARGUMENT TO SCH J CALC FOR TESTING PURPOSES
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
            
        raise ValueError("Income too large or negative")

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

class AdjustedTaxData():
    """
    Represents a single tax year that has been allocated elected farm income. Separate from TaxYearData so
    instances don't get stored to DB, but keeps the same struct for calculation consistency and ease of use.
    Results of this calculation are internally only; API uses ScheduleJResultsContainer instead.
    
    Attributes:
        Same as TaxYearStruct
    """
    DEFAULT_FIELDS = ['year', 
                      'filing_status', 
                      'taxable_income', 
                      'qualified_income', 
                      'is_electing', 
                      'elected_farm_income', 
                      'qualified_farm_income']

    def __init__(self,
                year: str,
                filing_status: str,
                taxable_income: Decimal = 0,
                qualified_income: Decimal = 0,
                ordinary_rate: Decimal = 0,
                lower_ordinary_bound: Decimal = 0,
                upper_ordinary_bound: Decimal = 0,
                prior_ordinary_bracket_tax: Decimal = 0,
                ordinary_tax: Decimal = 0,
                qualified_tax: Decimal = 0,
                total_tax: Decimal = 0,
                is_electing: bool = False,
                elected_farm_income: Decimal = 0,
                qualified_farm_income: Decimal = 0,):
        self.year = year
        self.filing_status = filing_status
        self.taxable_income = taxable_income
        self.qualified_income = qualified_income
        self.taxable_ordinary = self.taxable_income - self.qualified_income
        self.ordinary_rate = ordinary_rate
        self.lower_ordinary_bound = lower_ordinary_bound
        self.upper_ordinary_bound = upper_ordinary_bound
        self.prior_ordinary_bracket_tax = prior_ordinary_bracket_tax
        self.ordinary_tax = ordinary_tax
        self.qualified_tax = qualified_tax
        self.total_tax = total_tax
        self.is_electing = is_electing
        self.elected_farm_income = elected_farm_income
        self.qualified_farm_income = qualified_farm_income

    @classmethod
    def from_model_instance(cls, model_instance, fields=None):
        """
        Extract/copy key fields from TaxYearData Model instance to create the adjusted tax year

        Args: 
            model_instance: TaxYearData Model instance to extract from
            fields: List of field names to extract or None for DEFAULT_FIELDS

        Returns:
            Instance of AdjustedTaxData
        """
        if fields is None:
            fields=cls.DEFAULT_FIELDS

        kwargs = {}
        # Read fields we want to extract to create instance with
        for field_name in fields:
            kwargs[field_name] = getattr(model_instance, field_name)
        
        return cls(**kwargs)

class ScheduleJForm():
    """
    Contains results from a single Schedule J calculation and mimics the lines on the form.
    Instances don't get stored to DB, used in ScheduleJCalculation.
    Internal use only; API uses ScheduleJResultsContainer instead.
    """
    def __init__(self):
        """
        Create lines for Schedule J Form
        """
        for n in range(1, 24):
            setattr(self, f'line{n}', None)
        for i in 'abc':
            setattr(self, f'line_2{i}', None)

    def __str__(self):
        return f"Elected Farm Income: {self.line_2a} | Total Tax: {self.line_23}"
    
    def __repr__(self):
        return f"Elected Farm Income: {self.line_2a} | Total Tax: {self.line_23}"
    
        
class ScheduleJResultContainer:
    """
    Contains results from Schedule J Calculation.

    Attributes:
        schedule_j_form (ScheduleJForm): Filled out Schedule J Form
        elected_farm_income (int): Amount we elected
        elected_farm_qualified (int): Total elected made up of qualified income
        long_form (boolean): All Sch J values or only key values (Default)
        all_years (boolean): All AdjustedTaxData or none (Default)

    Notes: Eventually I should expand this where the object can take an arg to show all lines of the form
    and the computation results for each year. Will help when extending calculations later.
    """
    def __init__(self, schedule_j_form: ScheduleJForm,
                 elected_farm_income,
                 elected_farm_qualified,
                 long_form=False,
                 all_years=False
                 ):
        self.schedule_j_form = schedule_j_form
        self.elected_farm_income = elected_farm_income
        self.elected_farm_qualified = elected_farm_qualified

    def to_dict(self):
        return {
            "schedule_j_form": self.schedule_j_form,
            "elected_farm_income": self.elected_farm_income,
            "elected_farm_qualified": self.elected_farm_qualified
            }

def allocate_all_years(years):
    """
    Distributes qualified income across all years.

    Args:
        years (list): List of all TaxYearDatas in dataset

    Returns:
        years(list): Objects are directly mutated
    """
    for i, year in enumerate(years):
        if year.is_electing:
            remaining_years = years[i + 1:]
            allocate_income(
                election_year=year,
                other_years=remaining_years,
                elected_income=year.elected_farm_income,
                elected_qualified_income=year.qualified_farm_income,
            )
    return years

def allocate_income(election_year, other_years, elected_income, elected_qualified_income):
    """
    Takes single election year and distributes 1/3 of farm income to 3 previous years

    Arguments:
        election_year (TaxYearData): Year that is electing and distributing income
        other_years (list): All years prior to previous year
        elected_income (int)
        elected_qualified_income (int)

    Returns:
        election_year (TaxYearData): Mutated year - taxable and qualified updated to subtract elected income.
        three_prior_years (list): The three tax years that received elected income. Taxable and qualified updated

        Think about how we can go about mutating the Adjusted Tax Years in function
    """
    election_year.taxable_income -= elected_income
    election_year.qualified_income -= elected_qualified_income

    amount_to_distribute = elected_income / 3
    amount_to_distribute_qualified = elected_qualified_income / 3

    # Distribute to only the prior 3 years
    three_prior_years = list(other_years)[:3]

    for year in three_prior_years:
        year.taxable_income += amount_to_distribute
        year.qualified_income += amount_to_distribute_qualified

    return election_year, three_prior_years

def find_taxable(years):
    """
    Calculates the taxable income that is applied to the Schedule J for each year

    Args:
        years (list): List of all TaxYearDatas in dataset

    Returns:
        
    """

class ScheduleJCalculation:
    """
    Represents a Schedule J tax computation for a given current year as well as prior years if electing Sch J.
    
    Attributes:
        years (list): List of all TaxYearData instances in descending order by year
    """
    
    def __init__(self, years: list):
        # Create map of years
        self.years = {y.year: y for y in years}
        self.current_year = next(iter(self.years.values()))

    def schedule_j_calculation(self, elected_farm_income: Decimal, elected_cap_gains: Decimal) -> ScheduleJResultContainer:
        """
        Runs a single Schedule J calculation based on the elected income values

        Args:
            elected_farm_income (Decimal): The amount of farm income elected for averaging
            elected_cap_gains (Decimal): The amount of elected income made up of capital gains

        Returns:
            ScheduleJResultContainer: An object containing the computed Sch J results, which includes
            total tax for each year
        
        Raises: TypeError: If arguments are not a Decimal 
        """
        if not isinstance(elected_farm_income, Decimal):
            raise TypeError("Not a Decimal")
        if not isinstance(elected_cap_gains, Decimal):
            raise TypeError("Not a Decimal")
        
        # Create instances for calculations
        output = ScheduleJForm()
        all_adjusted_years = {year: AdjustedTaxData.from_model_instance(base) for year, base in self.years.items()}
        adjusted_current_year = all_adjusted_years[max(self.years)]

        output.line_1 = self.current_year.taxable_income
        output.line_2a = elected_farm_income
        output.line_2b = elected_cap_gains
        output.line_3 = output.line_1 - output.line_2a


        distribute_elected = elected_farm_income / 3
        output.line_6 = output.line_10 = output.line_14 = distribute_elected
    
        # Allocate elected farm income for all years
        years_list = list(all_adjusted_years.values())
        allocate_all_years(years_list)

        # Find tax on 2024 taxable less elected farm income
        TaxCalculation(adjusted_current_year).calculate()
        output.line_4 = adjusted_current_year.total_tax

        # Distribute elected farm income to each year, calculate tax
        update_lines = {
                'third_prior_year': ['line_5', 'line_7', 'line_8'],
                'second_prior_year': ['line_9', 'line_11', 'line_12'],
                'first_prior_year': ['line_13', 'line_15', 'line_16']
            }

        

        TaxCalculation(adjusted).calculate(save=False)
        

        output.line_17 = output.line_4 + output.line_8 + output.line_12 + output.line_16
        output.line_18 = output.line_17 

         # Get baseline tax from each year
        base_tax = {
                '2021': 'line_19',
                '2022': 'line_20',
                '2023': 'line_21',
            }

        for year, (tax_amount) in base_tax.items():
            setattr(output, tax_amount, self.base_years[year].total_tax)

        # Total base tax from prior years
        output.line_22 = output.line_19 + output.line_20 + output.line_21

        # Schedule J tax for 2024
        output.line_23 = output.line_18 - output.line_22

        # Tax savings/expense compared to not using Sch J
        output.tax_delta = self.current_year.total_tax - output.line_23

        return ScheduleJResultContainer(
            schedule_j_form=output,
            elected_farm_income=elected_farm_income,
            elected_farm_qualified=elected_qualified,
            long_form=False,
            all_years=False
            )


class ScheduleJOptimization:
    """
    Represents a single Schedule J Optimization
    """
    
    def __init__(self, years, elected_farm_income: float, elected_farm_qualified: float, dataset: TaxYearData):
        self.years = sorted(years, key=lambda y: y.year)
        self.elected_farm_income = elected_farm_income
        self.elected_farm_qualified = elected_farm_qualified
        self.dataset = dataset

    def optimize_sch_j(self, elected_farm_income: Decimal, elected_farm_qualified: Decimal):
        """
        Run Schedule J Optimization by iterating through the max elected farm income until we get to 0.

        Args:
            elected_farm_income (Decimal): The maximum amount of farm income that can be elected to average
            elected_cap_gains (Decimal): The amount of elected income made up of capital gains

        Returns:
            results (list): A list of all ScheduleJForm objects that were calcualted
        """
        # for sch j calculation, we need to know the years and how elected income flows. start from highest year so we know
        # how that income flows down. also need to know how many sch j calcualtions we're doing in total.

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
            instance = (ScheduleJCalculation(self.years)
                        .schedule_j_calculation(current_total_elected, current_qualified_elected))
            forms.append(instance.schedule_j_form)

            current_total_elected -= 500
            current_ordinary_elected -= 500 * ordinary_percentage
            current_qualified_elected -= 500 * qualified_percentage
            
        return forms
