from django.contrib import admin
from .models import User, TaxYearData, TaxDataSet, CalculationIteration, ScheduleJForm, AdjustedTaxData


class TaxYearDataInline(admin.TabularInline):
    model = TaxYearData
    extra = 0

class ScheduleJFormInLine(admin.StackedInline):
    model = ScheduleJForm
    can_delete = False
    extra = 0

class AdjustedTaxDataInline(admin.StackedInline):
    model = AdjustedTaxData
    can_delete = False
    extra = 0


@admin.register(CalculationIteration)
class CalculationIterationAdmin(admin.ModelAdmin):
    list_display = ('id',)

    inlines = [ScheduleJFormInLine, AdjustedTaxDataInline]

class CalculationIterationInline(admin.TabularInline):
    model = CalculationIteration
    extra = 0
    show_change_link = True

@admin.register(TaxDataSet)
class TaxDataSetAdmin(admin.ModelAdmin):
    list_display = ('name', 'id')
    inlines = [TaxYearDataInline, CalculationIterationInline]