from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal

from .utils import create_schedulej_fields

YEAR = [
        ("2024", "2024"),
        ("2023", "2023"),
        ("2022", "2022"),
        ("2021", "2021"),
        ("2020", "2020"),
        ("2019", "2019"),
        ("2018", "2018"),
    ]

FILING_STATUS = {
        "single": "Single",
        "MFJ": "Married Filing Jointly",
        "MFS": "Married Filing Separately",
        "HOH": "Head of Household",
        "QSS": "Qualifying Surviving Spouse",
    }


class TaxDataSet(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='datasets')
    created_at = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=200, default="Created Set")
    max_elected_farm_income = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    qualified_farm_income = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    ordinary_farm_income = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    income_worksheet = models.JSONField(null=True, blank=True, default=dict)

    def __str__(self):
        return '{} - {}'.format(self.name, self.pk)
    
    def return_optimal_amount(self):
        return ScheduleJForm.objects.filter(
            iteration__dataset=self
        ).order_by('line_23').first()
    
    def save(self, *args, **kwargs):
        self.ordinary_farm_income = max(self.max_elected_farm_income - self.qualified_farm_income, Decimal('0'))
        super().save(*args, **kwargs)

    def return_best_tax_delta(self):
        return ScheduleJForm.objects.filter(
            iteration__dataset=self
        ).order_by('tax_delta').last()
        

class TaxYearStructure(models.Model):
    year = models.CharField(max_length=4, choices=YEAR)
    filing_status = models.CharField(max_length=6, choices=FILING_STATUS)
    taxable_income = models.DecimalField(decimal_places=2, max_digits=11, default=0)
    qualified_income = models.DecimalField(decimal_places=2, max_digits=11, default=0)
    taxable_ordinary = models.DecimalField(decimal_places=2, max_digits=11, editable=False)

    ordinary_rate = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    lower_ordinary_bound = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    upper_ordinary_bound = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    prior_ordinary_bracket_tax = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    ordinary_tax = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    qualified_tax = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_tax = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def save(self, *args, **kwargs):
        self.taxable_ordinary = self.taxable_income - self.qualified_income
        super().save(*args, **kwargs)

    def __str__(self):
        return '{}  {}  {}  {}'.format(self.year, self.filing_status, self.taxable_income, self.qualified_income)
    
    def to_dict(self):
        return {
            "year": self.year,
            "filing_status": self.filing_status,
            "taxable_income": self.taxable_income,
            "qualified_income": self.qualified_income,
            "taxable_ordinary": self.taxable_ordinary,
            # "ordinary_rate": self.ordinary_rate,
            # "lower_ordinary_bound": self.lower_ordinary_bound,
            # "upper_ordinary_bound": self.upper_ordinary_bound,
            # "prior_ordinary_bracket_tax": self.prior_ordinary_bracket_tax,
            "ordinary_tax": self.ordinary_tax,
            "qualified_tax": self.qualified_tax,
            "total_tax": self.total_tax,
        }

    class Meta:
        abstract = True

class TaxYearData(TaxYearStructure):
    dataset = models.ForeignKey(TaxDataSet, on_delete=models.CASCADE, related_name="tax_years")

class CalculationIteration(models.Model):
    dataset = models.ForeignKey(TaxDataSet, on_delete=models.CASCADE, related_name="iterations")
    def __str__(self):
        return f"Iteration {self.id}"
    
class AdjustedTaxData(TaxYearStructure):
    iteration = models.ForeignKey(CalculationIteration, on_delete=models.CASCADE, related_name="adjusted_years")

    @classmethod
    def from_base(cls, base: TaxYearStructure, iteration: "CalculationIteration", save=False):
        """
        Does not save to DB by default
        """
        instance = cls(
            year=base.year,
            filing_status=base.filing_status,
            taxable_income=base.taxable_income,
            qualified_income=base.qualified_income,
            ordinary_rate=base.ordinary_rate,
            lower_ordinary_bound=base.lower_ordinary_bound,
            upper_ordinary_bound=base.upper_ordinary_bound,
            prior_ordinary_bracket_tax=base.prior_ordinary_bracket_tax,
            ordinary_tax=base.ordinary_tax,
            qualified_tax=base.qualified_tax,
            total_tax=base.total_tax,
            iteration=iteration,
        )
        if save:
            instance.save()
        return instance
    
    def to_dict(self):
        return self.total_tax

class ScheduleJForm(models.Model):
    iteration = models.OneToOneField(CalculationIteration, on_delete=models.CASCADE, related_name="form")
    locals().update(create_schedulej_fields())
    tax_delta = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def __str__(self):
        field_values = [f"{field.name}={getattr(self, field.name)}" for field in self._meta.fields]
        return f"{self.__class__.__name__}({', '.join(field_values)})"