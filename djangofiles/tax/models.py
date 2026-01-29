from decimal import Decimal

from django.contrib.auth.models import User
from django.db import models

VALID_YEARS = [
        ("2025", "2025"),
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
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="datasets")
    created_at = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=200, default="Created Set")
    max_elected_farm_income = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    qualified_farm_income = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    election_year = models.CharField(max_length=4, choices=VALID_YEARS, default="2024")
    ordinary_farm_income = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    income_worksheet = models.JSONField(null=True, blank=True, default=dict)

    def __str__(self):
        return f"{self.name} - {self.pk}"

    def save(self, *args, **kwargs):
        self.ordinary_farm_income = max(self.max_elected_farm_income - self.qualified_farm_income, Decimal("0"))  # noqa: FURB157
        super().save(*args, **kwargs)

class ScheduleJOptimization(models.Model):
    dataset = models.ForeignKey(TaxDataSet, on_delete=models.CASCADE)
    inputs = models.JSONField(null=True, blank=True, default=dict)
    best_result = models.JSONField(null=True, blank=True, default=dict)

class TaxYearStructure(models.Model):
    year = models.CharField(max_length=4, choices=VALID_YEARS)
    filing_status = models.CharField(max_length=6, choices=FILING_STATUS)
    taxable_income = models.DecimalField(decimal_places=2, max_digits=11, default=0)
    qualified_income = models.DecimalField(decimal_places=2, max_digits=11, default=0)
    is_electing = models.BooleanField(default=False)
    elected_farm_income = models.DecimalField(decimal_places=2, max_digits=11, default=0)
    qualified_farm_income = models.DecimalField(decimal_places=2, max_digits=11, default=0)

    class Meta:
        abstract = True

    def __str__(self):
        return f"{self.year}  {self.filing_status}  {self.taxable_income}  {self.qualified_income}"

    @property
    def taxable_ordinary(self):
        """Computed property: Returns taxable ordinary income on demand."""
        return self.taxable_income - self.qualified_income

    def to_dict(self):
        return {
            "year": self.year,
            "filing_status": self.filing_status,
            "taxable_income": self.taxable_income,
            "qualified_income": self.qualified_income,
            "taxable_ordinary": self.taxable_ordinary,
        }

class TaxYearData(TaxYearStructure):
    dataset = models.ForeignKey(TaxDataSet, on_delete=models.CASCADE, related_name="tax_years")
