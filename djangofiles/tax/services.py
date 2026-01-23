import copy
from dataclasses import dataclass
from decimal import Decimal

from .calculations import tax_brackets
from .models import TaxYearData, TaxYearStructure


class TaxCalculationResult:
    def __init__(self, ordinary_tax: Decimal, qualified_tax: Decimal,
                 total_tax: Decimal, ordinary_rate: Decimal, lower_ordinary_bound: Decimal,
                 upper_ordinary_bound: Decimal, tax_on_prior_brackets: Decimal):
        self.ordinary_tax = ordinary_tax
        self.qualified_tax = qualified_tax
        self.total_tax = total_tax
        self.ordinary_rate = ordinary_rate
        self.lower_ordinary_bound = lower_ordinary_bound
        self.upper_ordinary_bound = upper_ordinary_bound
        self.tax_on_prior_brackets = tax_on_prior_brackets

    def to_dict(self):
        return {
        "ordinary_tax": self.ordinary_tax,
        "qualified_tax": self.qualified_tax,
        "total_tax": self.total_tax,
        "ordinary_rate": self.ordinary_rate,
    }

class TaxCalculation:
    def __init__(self, tax_data: TaxYearData):
        self.tax_data = tax_data

        # Pull needed fields from the TaxYearData object
        self.year = self.tax_data.year
        self.filing_status = self.tax_data.filing_status
        self.taxable_income = self.tax_data.taxable_income
        self.qualified_income = self.tax_data.qualified_income
        self.taxable_ordinary = self.tax_data.taxable_ordinary

    def calculate_total_tax(self) -> TaxCalculationResult:
        bracket_info = self._find_ordinary_bracket()
        ordinary_tax = self._calculate_ordinary_tax(bracket_info)
        qualified_tax = self._calculate_qualified_tax()
        total_tax = self._find_total_tax(ordinary_tax, qualified_tax)

        calculation_results = TaxCalculationResult(ordinary_tax=ordinary_tax,
                                                   qualified_tax=qualified_tax,
                                                   total_tax=total_tax,
                                                   **bracket_info,
                                                   )
        return calculation_results

    def _find_ordinary_bracket(self) -> dict[str, Decimal]:
        for rate, (lower, upper, prior_tax) in tax_brackets.ORDINARY_TAX_TABLES[self.year][self.filing_status].items():
            if lower <= self.taxable_ordinary <= upper:
                return {
                    "ordinary_rate": Decimal(rate),
                    "lower_ordinary_bound": lower,
                    "upper_ordinary_bound": upper,
                    "tax_on_prior_brackets": prior_tax,
                }

        # Test for edge case where taxable ordinary is < $0
        first_bracket = tax_brackets.ORDINARY_TAX_TABLES[self.year][self.filing_status]["0.10"]
        if self.taxable_ordinary < 0:
            return {
                "ordinary_rate": first_bracket[0],
                "lower_ordinary_bound": 0,
                "upper_ordinary_bound": first_bracket[1],
                "tax_on_prior_brackets": 0,
            }

        raise ValueError("Taxable income is too high")

    def _calculate_ordinary_tax(self, bracket_info):
        ordinary_tax = ((self.taxable_ordinary - bracket_info["lower_ordinary_bound"]) * bracket_info["ordinary_rate"] + bracket_info["tax_on_prior_brackets"])
        return ordinary_tax

    def _calculate_qualified_tax(self):
        qualified_tables = tax_brackets.QUALIFIED_TAX_TABLES[self.year][self.filing_status]
        zero_threshold = qualified_tables["0"][1]
        fifteen_threshold = qualified_tables[".15"][1]
        twenty_threshold = qualified_tables[".15"][0]

        if self.taxable_income <= zero_threshold:
            return Decimal(0)

        if self.taxable_income < fifteen_threshold:
            if self.taxable_ordinary >= 0:
                return self._qualified_tax_max_fifteen_percent(zero_threshold)
            return self._qualified_tax_max_fifteen_percent_negative_ordinary(zero_threshold)

        if self.taxable_income > twenty_threshold:
            if self.taxable_ordinary >= 0:
                return self._qualified_tax_max_twenty_percent(zero_threshold, fifteen_threshold)
            return self._qualified_tax_max_twenty_percent_negative_ordinary(zero_threshold, fifteen_threshold)

        raise ValueError("Qualified tax calculation not able to compute, check inputs")

    def _qualified_tax_max_fifteen_percent(self, zero_threshold):
        # Take the max to see if any income falls in the 0% bracket
        income_in_zero_bracket = max(zero_threshold - self.taxable_ordinary, 0)

        # Rest of qualified income goes in 15% bracket
        income_in_fifteen_bracket = self.qualified_income - income_in_zero_bracket

        qualified_tax = (income_in_zero_bracket * 0) + (income_in_fifteen_bracket * Decimal(.15))
        return qualified_tax

    def _qualified_tax_max_fifteen_percent_negative_ordinary(self, zero_threshold):
        # 0% bracket entirely filled
        income_in_zero_bracket = zero_threshold

        # Use taxable income instead since qualified income > taxable income
        income_in_fifteen_bracket = self.taxable_income - income_in_zero_bracket

        qualified_tax = (income_in_zero_bracket * 0) + (income_in_fifteen_bracket * Decimal(.15))
        return qualified_tax

    def _qualified_tax_max_twenty_percent(self, zero_threshold, fifteen_threshold):
        income_in_zero_bracket = max(zero_threshold - self.taxable_ordinary, 0)

        income_in_fifteen_bracket = max(fifteen_threshold - income_in_zero_bracket - self.taxable_ordinary, 0)

        income_in_twenty_bracket = self.qualified_income - income_in_zero_bracket - income_in_fifteen_bracket

        qualified_tax = (income_in_zero_bracket * 0) + (income_in_fifteen_bracket * Decimal(.15)) + (income_in_twenty_bracket * Decimal(.20))
        return qualified_tax

    def _qualified_tax_max_twenty_percent_negative_ordinary(self, zero_threshold, fifteen_threshold):
        # 0% bracket will be filled entirely
        income_in_zero_bracket = zero_threshold

        # 15% bracket will be filled entirely
        income_in_fifteen_bracket = fifteen_threshold - zero_threshold

        # Use taxable income instead since qualified income > taxable income
        income_in_twenty_bracket = self.taxable_income - income_in_fifteen_bracket - income_in_zero_bracket

        qualified_tax = (income_in_zero_bracket * 0) + (income_in_fifteen_bracket * Decimal(.15)) + (income_in_twenty_bracket * Decimal(.20))
        return qualified_tax

    def _find_total_tax(self, ordinary_tax, qualified_tax):
        # Keeping this as a separate method in case the tax calc logic expands (e.g. 1250 gains)
        total_tax = max(ordinary_tax + qualified_tax, 0)
        return total_tax

class AdjustedTaxData:
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
                      'qualified_farm_income',
                      'ordinary_rate']
    
    _DEFAULTS = {
        "taxable_income": Decimal(0),
        "qualified_income": Decimal(0),
        "ordinary_rate": Decimal(0),
        "lower_ordinary_bound": Decimal(0),
        "upper_ordinary_bound": Decimal(0),
        "prior_ordinary_bracket_tax": Decimal(0),
        "ordinary_tax": Decimal(0),
        "qualified_tax": Decimal(0),
        "total_tax": Decimal(0),
        "is_electing": False,
        "elected_farm_income": Decimal(0),
        "qualified_farm_income": Decimal(0),
    }


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
                qualified_farm_income: Decimal = 0):
        self.year = year
        self.filing_status = filing_status
        self.taxable_income = taxable_income
        self.qualified_income = qualified_income
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
        Extract/copy key fields from TaxYearData Model instance to create the adjusted tax year.

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

    @property
    def taxable_ordinary(self):
        """Computed property: Returns taxable ordinary income on demand."""
        return max(self.taxable_income - self.qualified_income, 0)

    def to_dict(self):
        return {
            "year": self.year,
            "filing_status": self.filing_status,
            "taxable_income": self.taxable_income,
            "qualifed_income": self.qualified_income,
            "total_tax": self.total_tax,
            "elected_farm_income": self.elected_farm_income
        }

class ScheduleJForm:
    def __init__(self, long_form=False):
        self.long_form = long_form

        for n in range(1, 24):
            setattr(self, f"line_{n}", None)
        for i in "abc":
            setattr(self, f"line_2{i}", None)
        self.election_year_base_tax = None
        self.tax_delta = None

        self.delete_extraneous_lines()

    def delete_extraneous_lines(self):
        del self.line_2
        del self.line_2c

    def to_dict(self):
        if not self.long_form:
            return {
                "elected_farm_income": self.line_2a,
                "total_tax": self.line_23,
            }

        def sort_key(attr):
            # Extract the part after "line_"
            suffix = attr[5:]  # Remove "line_" prefix

            # Split into numeric and letter parts
            # e.g., "2a" -> (2, "a"), "23" -> (23, "")
            numeric_part = ""
            letter_part = ""

            for char in suffix:
                if char.isdigit():
                    numeric_part += char
                else:
                    letter_part += char

            # Return tuple for sorting: (numeric value, letter part)
            return (int(numeric_part) if numeric_part else 0, letter_part)

        # Get all line attributes
        line_attrs = [
            attr for attr in dir(self)
            if attr.startswith("line") and not callable(getattr(self, attr))
        ]

        # Sort them numerically
        line_attrs.sort(key=sort_key)

        # Build the dictionary in order
        fields = {attr: getattr(self, attr) for attr in line_attrs}
        fields["election_year_base_tax"] = self.election_year_base_tax
        fields["tax_delta"] = self.tax_delta
        return fields

    def __str__(self):
        if self.long_form:
            result = self.to_dict()
            lines = [f"{key}: {value}" for key, value in result.items()]
            return "\n".join(lines)
        return f"Elected Farm Income: {self.line_2a} | Total Tax: {self.line_23}"

    __repr__ = __str__  # Same for debugging

class ScheduleJResultContainer:
    def __init__(self,
                 schedule_j_form: ScheduleJForm,
                 elected_farm_income,
                 elected_farm_qualified,
                 config,
                 tax_years=None,
                 ):
        self.schedule_j_form = schedule_j_form
        self.elected_farm_income = elected_farm_income
        self.elected_farm_qualified = elected_farm_qualified

        self.show_full_sch_j_form = config.show_full_sch_j_form
        self.show_all_tax_years = config.show_all_tax_years
        self.tax_years = tax_years or {}

    def to_dict(self):
        result = {
            "schedule_j_form": self.schedule_j_form,
            "elected_farm_income": self.elected_farm_income,
            "elected_farm_qualified": self.elected_farm_qualified,
            }

        if self.all_years:
            result["tax_years"] = {
                year: data.to_dict() for year, data in self.tax_years.items()
            }
        return result

def find_bracket_thresholds(year: str, filing_status: str, ordinary_rate_lowest: str, ordinary_rate_highest: str):
    """
    Returns the bracket thresholds for all brackets between and including the lowest and highest ordinary income rates
    
    Arguments:
        year (String): year we want to find brackets for
        filing_status (String): filing status that was clamed
        ordinary_rate_lowest (String): Ordinary income rate for the year with no elected income
        ordinary_rate_highest (String): Ordinary income rate for the year with max elected income
    
    Returns:
        bracket_thresholds (dict): dict with marginal rate (str) as key and upper threshold (int) as value
        ex: {0.22: 80521, 0.24: 120000, 0.32: 180000}

    Notes:
        The bracket values are being converted to ints here so we don't need to serialize the Decimals

        Returns all brackets from one bracket below the lowest ordinary income amount 
        to one bracket above the highest income amount.
        Example: With $0 of elected income, we are in the 24% bracket, and with the max elected income we are in the 32% bracket
                The 22%, 24%, 32%, and 35% brackets will be returned and displayed on the ordinary income graph
    """
    applicable_brackets = list(tax_brackets.ORDINARY_TAX_TABLES[str(year)][filing_status].items())

    # Find the lowest and highest rate positions
    lowest_index = next(i for i, (rate, _) in enumerate(applicable_brackets) if rate == ordinary_rate_lowest)
    highest_index = next(i for i, (rate, _) in enumerate(applicable_brackets) if rate == ordinary_rate_highest)

    # Expand range by one bracket on each side if possible
    start_index = max(0, lowest_index - 1)
    end_index = min(len(applicable_brackets) - 1, highest_index + 1)

    # Extract all brackets in the range
    bracket_thresholds = {}
    for i in range(start_index, end_index + 1):
        rate, (threshold, _, _) = applicable_brackets[i]
        bracket_thresholds[rate] = int(threshold)

    return bracket_thresholds

@dataclass
class ScheduleJConfig:
    """Using in case results want to be extended and customized in future."""

    show_full_sch_j_form: bool = False
    show_all_tax_years: bool = False

    @classmethod
    def full_audit(cls):
        return cls(True, True)

class ScheduleJCalculation:
    def __init__(self, years: list[TaxYearData],
                elected_farm_income: Decimal,
                qualified_farm_income: Decimal,
                config: ScheduleJConfig = None):
        self.tax_years = self._create_tax_years_map(years)
        self.election_year, self.election_year_obj = self._get_first_year_from_tax_years_map()
        self.elected_farm_income = elected_farm_income
        self.qualified_farm_income = qualified_farm_income
        self.config = config if config is not None else ScheduleJConfig()
        self.adjusted_years = self._create_adjusted_years_map()
        self.sch_j = ScheduleJForm(long_form=self.config.show_full_sch_j_form)

        self._validate_inputs()

    def _create_tax_years_map(self, years: TaxYearStructure):
        years_map = {int(y.year): y for y in years}
        return years_map

    def _get_first_year_from_tax_years_map(self):
        year, tax_year_obj = next(iter(self.tax_years.items()))
        return year, tax_year_obj

    def _create_adjusted_years_map(self) -> dict[str, AdjustedTaxData]:
        adjusted_years_list = [copy.deepcopy(base) for base in self.tax_years.values()]
        return self._create_tax_years_map(adjusted_years_list)

    def _validate_inputs(self):
        if not isinstance(self.elected_farm_income, Decimal):
            raise TypeError("elected_farm_income must be a Decimal")
        if not isinstance(self.qualified_farm_income, Decimal):
            raise TypeError("qualified_farm_income must be a Decimal")
        if self.qualified_farm_income > self.elected_farm_income:
            raise ValueError("qualified_farm_income cannot exceed elected_farm_income")
        if len(self.tax_years) != 4 | len(self.adjusted_years) != 4:
            raise ValueError("Number of tax years not equal to four")

    def calculate(self) -> ScheduleJResultContainer:
        self._fill_schedule_j_with_basic_information()

        # Allocate elected farm income for all years
        distributor = IncomeDistributor(self.adjusted_years)
        distributor.distribute_all_elected_income()

        # Calculate tax with elected income factored in: lines (7,8), (11,12), (15,16)
        tax_on_all_years = self._calculate_tax_on_all_years()
        self._fill_form_with_tax_results(tax_on_all_years)

        # Remove the election year's elected income since that income gets distributed in the IncomeDistributor
        # Need to remove that income so we can calculate the base tax without the election year's elected income factored in (lines 19, 20, 21)
        # We use IncomeDistributor first so the elected income in the prior years get accounted for
        self._adjust_taxable_income_by_elected()
        tax_on_all_years_without_elected = self._calculate_tax_on_all_years()
        self._fill_form_with_adj_tax_results(tax_on_all_years_without_elected)
        self._readjust_taxable_income_for_elected()

        # Fill in remainder of form
        self._fill_remainder_of_form()

        self.sch_j.tax_delta = self.sch_j.election_year_base_tax - self.sch_j.line_23

        # Get ordinary income for each year for bracket threshold graph
        # sch_j.taxable_ordinary_all_years = {year: int(y.taxable_ordinary) for year, y in all_adjusted_years.items()}

        return ScheduleJResultContainer(
            schedule_j_form=self.sch_j,
            elected_farm_income=self.elected_farm_income,
            elected_farm_qualified=self.qualified_farm_income,
            config=self.config,
            tax_years=self.adjusted_years if self.config.show_all_tax_years else {},
            )

    def _fill_schedule_j_with_basic_information(self):
        self.sch_j.line_1 = self.election_year_obj.taxable_income
        self.sch_j.line_2a = self.elected_farm_income
        self.sch_j.line_2b = self.qualified_farm_income
        self.sch_j.line_3 = self.sch_j.line_1 - self.sch_j.line_2a

        distribute_elected = self.elected_farm_income / 3
        self.sch_j.line_6 = self.sch_j.line_10 = self.sch_j.line_14 = distribute_elected

    def _fill_year_lines(self, results, year_to_lines):
        """Helper to fill form lines from yearly tax results."""
        for year, (income_line, tax_line) in year_to_lines.items():
            if year in results:
                taxable_income = self.adjusted_years[year].taxable_income
                total_tax = results[year]
                setattr(self.sch_j, income_line, taxable_income)
                setattr(self.sch_j, tax_line, total_tax)

    def _calculate_tax_on_all_years(self) -> dict[int, Decimal]:
        """Calculate tax for all years based on current adjusted_years state."""
        tax_on_all_years = {}
        for year, year_obj in self.adjusted_years.items():
            result = TaxCalculation(year_obj).calculate_total_tax()
            tax_on_all_years[year] = result.total_tax
        return tax_on_all_years

    def _fill_form_with_tax_results(self, tax_on_all_years: dict[int, Decimal]):
        lines_to_update = {
            self.election_year: ("line_3", "line_4"),
            self.election_year - 1: ("line_15", "line_16"),
            self.election_year - 2: ("line_11", "line_12"),
            self.election_year - 3: ("line_7", "line_8"),
        }
        self._fill_year_lines(tax_on_all_years, lines_to_update)

    def _adjust_taxable_income_by_elected(self):
        for year, year_obj in self.adjusted_years.items():
            if year != self.election_year:
                year_obj.taxable_income -= self.elected_farm_income / 3
                year_obj.qualified_income -= self.qualified_farm_income / 3
            else:
                year_obj.taxable_income += self.elected_farm_income
                year_obj.qualified_income += self.qualified_farm_income

    def _fill_form_with_adj_tax_results(self, tax_on_all_years: dict[int, Decimal]):
        lines_to_update = {
            self.election_year: ("line_1", "election_year_base_tax"),
            self.election_year - 1: ("line_13", "line_21"),
            self.election_year - 2: ("line_9", "line_20"),
            self.election_year - 3: ("line_5", "line_19"),
        }
        self._fill_year_lines(tax_on_all_years, lines_to_update)

    def _readjust_taxable_income_for_elected(self):
        """Just wanna do the opposite of _adjust_by_elected to get taxable income back at right place."""
        for year, year_obj in self.adjusted_years.items():
            if year != self.election_year:
                year_obj.taxable_income += self.elected_farm_income / 3
                year_obj.qualified_income += self.qualified_farm_income / 3
            else:
                year_obj.taxable_income -= self.elected_farm_income
                year_obj.qualified_income -= self.qualified_farm_income

    def _fill_remainder_of_form(self):
        self.sch_j.line_17 = self.sch_j.line_4 + self.sch_j.line_8 + self.sch_j.line_12 + self.sch_j.line_16
        self.sch_j.line_18 = self.sch_j.line_17

        # Total base tax from prior years
        self.sch_j.line_22 = self.sch_j.line_19 + self.sch_j.line_20 + self.sch_j.line_21

        # Schedule J tax for 2024
        self.sch_j.line_23 = self.sch_j.line_18 - self.sch_j.line_22

        # Tax savings/expense compared to not using Sch J
        self.sch_j.tax_delta = self.sch_j.election_year_base_tax - self.sch_j.line_23

class IncomeDistributor:
    def __init__(self, adjusted_years: dict[int, AdjustedTaxData]):
        self.adjusted_years = adjusted_years

    def distribute_all_elected_income(self):
        for year, year_obj in self.adjusted_years.items():
            if year_obj.is_electing:
                self._distribute_current_year_to_older_years(year, year_obj)

    def _distribute_current_year_to_older_years(self, election_year_key, election_year_obj):
        prior_years = self._get_prior_years_to_distribute_to(election_year_key)

        self._distribute_income_to_prior_years(
            election_year=election_year_obj,
            prior_years=prior_years,
            elected_income=election_year_obj.elected_farm_income,
            elected_qualified_income=election_year_obj.qualified_farm_income,
        )

    def _get_prior_years_to_distribute_to(self, election_year):
        return [obj for year, obj in self.adjusted_years.items() if year < election_year]

    def _distribute_income_to_prior_years(self, election_year, prior_years, elected_income, elected_qualified_income):
        election_year.taxable_income -= elected_income
        election_year.qualified_income -= elected_qualified_income

        amount_to_distribute = elected_income / 3
        amount_to_distribute_qualified = elected_qualified_income / 3

        for year_obj in prior_years:
            year_obj.taxable_income += amount_to_distribute
            year_obj.qualified_income += amount_to_distribute_qualified

class ScheduleJOptimizer:
    def __init__(self, tax_years, max_elected_farm_income: Decimal, qualified_farm_income: Decimal, config: ScheduleJConfig):
        self.tax_years = tax_years
        self.max_elected_farm_income = max_elected_farm_income
        self.qualified_farm_income = qualified_farm_income
        self.config = config if config is not None else ScheduleJConfig()

        self.income_increment = 500
        self.ordinary_farm_income = self.max_elected_farm_income - self.qualified_farm_income
        self.show_all_years = self.config.show_all_tax_years
        self.long_form = self.config.show_full_sch_j_form

        self._validate_inputs()

    def _validate_inputs(self):
        if not isinstance(self.max_elected_farm_income, Decimal):
            raise TypeError("Not a Decimal")
        if not isinstance(self.qualified_farm_income, Decimal):
            raise TypeError("Not a Decimal")
        if self.qualified_farm_income > self.max_elected_farm_income:
            raise ValueError("qualified_farm_income cannot exceed elected_farm_income")
        if len(self.tax_years) != 4:
            raise ValueError("Number of tax years not equal to four")

    def run_optimization(self):
        """
        Run Schedule J Optimization by iterating through the max elected farm income until we get to 0.

        Args:
            elected_farm_income (Decimal): The maximum amount of farm income that can be elected to average
            elected_farm_qualified (Decimal): The amount of elected income made up of capital gains
            show_all_years (bool): True if you want ScheduleJResultContainer to return all AdjustedTaxData instances. Default is False.
            long_form (bool): True if you want ScheduleJResultContainer to return all lines on ScheduleJForm. Default is False.

        Returns:
            results (list): A list of all ScheduleJForm objects that were calcualted
            first instance (ScheduleJResultsContainer): Sch J instance with no elected farm income
            last_instance (ScheduleJResultsContainer): Sch J instance with max elected farm income

        """
        ordinary_income_percentage, qualified_income_percentage = self._calculate_income_proportions()
        self._handle_optimization_loop(ordinary_income_percentage, qualified_income_percentage)

    def _calculate_income_proportions(self):
        ordinary_income_percentage = self.ordinary_farm_income / self.max_elected_farm_income
        qualified_income_percentage = self.qualified_farm_income / self.max_elected_farm_income
        return ordinary_income_percentage, qualified_income_percentage

    def _handle_optimization_loop(self, ordinary_income_percentage, qualified_income_percentage):
        current_total_elected = self.max_elected_farm_income
        current_qualified_elected = self.qualified_farm_income
        current_ordinary_elected = current_total_elected - current_qualified_elected
        iteration = 0
        results = []

        while current_total_elected >= self.income_increment:
            is_first_instance = (iteration == 0)
            is_last_instance = (current_total_elected - self.income_increment < self.income_increment)

            # Compute with show_all_years = True on first and last iterations only
            if is_first_instance:
                none_elected_instance = self._handle_first_iteration(current_total_elected, current_qualified_elected)
            if is_last_instance:
                all_elected_instance = self._handle_last_iteration(current_total_elected, current_qualified_elected)

            else:
                # Truncated data show_all_years = False
                instance = (ScheduleJCalculation(self.years, show_all_years=self.show_all_years, long_form=self.long_form)
                            .schedule_j_calculation(current_total_elected, current_qualified_elected))

            results.append(instance.schedule_j_form)

            current_total_elected -= 500
            current_ordinary_elected -= 500 * ordinary_income_percentage
            current_qualified_elected -= 500 * qualified_income_percentage
            self.years[0].elected_farm_income -= 500 * ordinary_income_percentage
            self.years[0].qualified_farm_income -= 500 * qualified_income_percentage
            iteration += 1

        return {
            "optimization_results": results,
            "all_elected": all_elected_instance,
            "none_elected": none_elected_instance,
        }

    def _handle_first_iteration(self, current_total_elected, current_qualified_elected):
        calc_instance = ScheduleJCalculation(years=self.years,
                                            elected_farm_income=current_total_elected,
                                            qualified_farm_income=current_qualified_elected,
                                            config=self.config)
        first_iteration_results = calc_instance.calculate()
        return first_iteration_results

    def _handle_last_iteration(self, current_total_elected, current_qualified_elected):
        calc_instance = ScheduleJCalculation(years=self.years,
                                            elected_farm_income=current_total_elected,
                                            qualified_farm_income=current_qualified_elected,
                                            config=self.config)
        last_iteration_results = calc_instance.calculate()
        return last_iteration_results
