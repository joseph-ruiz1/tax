from collections.abc import Mapping

from tax.models import TaxDataSet, TaxYearData

# prob need to create custom type here
def update_inputs(dataset: TaxDataSet, data_to_update):
    tax_year_data = data_to_update.pop("tax_years")

    for field, value in data_to_update.items():
        setattr(dataset, field, value)
    dataset.save()

    for data in tax_year_data:
        TaxYearData.objects.filter(
            dataset=dataset, 
            year=data["year"]
        ).update(**{k: v for k, v in data.items() if k != "year"})

def add_pk_to_tax_year(dataset: TaxDataSet, data_to_update):
    tax_years = TaxYearData.objects.filter(dataset=dataset).order_by("-year")
    for year_obj, year_test_data in zip(tax_years, data_to_update["tax_years"]):
        year_test_data["id"] = year_obj.id
    print(data_to_update["tax_years"])
    return data_to_update