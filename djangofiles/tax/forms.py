from django import forms
from django.forms import modelformset_factory
from .models import TaxDataSet, TaxYearData


class TaxYearDataForm(forms.ModelForm):
    class Meta:
        model = TaxYearData
        fields = ['year', 'filing_status', 'taxable_income', 'qualified_income',]

        
class TaxDataSetForm(forms.ModelForm):
    class Meta:
        model = TaxDataSet
        fields = ["name", "max_elected_farm_income", "qualified_farm_income"]

TaxYearDataFormSet = modelformset_factory(
    TaxYearData,
    form=TaxYearDataForm,
    extra=4,
    exclude=["user"]
)

