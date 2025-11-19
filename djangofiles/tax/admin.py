from django.contrib import admin
from .models import TaxYearData, TaxDataSet


class TaxYearDataInline(admin.TabularInline):
    model = TaxYearData
    extra = 0