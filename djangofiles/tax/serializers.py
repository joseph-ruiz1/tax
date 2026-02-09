from decimal import Decimal

from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.db import transaction
from rest_framework import serializers
from dj_rest_auth.serializers import UserDetailsSerializer as BaseUserDetailsSerializer

from .models import FILING_STATUS, TaxDataSet, TaxYearData
from .utils import (
    validate_only_four_tax_years,
    validate_years_are_in_order,
)

VALID_YEARS_LIST = ["2025", "2024", "2023", "2022", "2021", "2020", "2019", "2018"]
DEFAULT_ELECTION_YEAR = "2024"

class UserSerializer(serializers.ModelSerializer):
    datasets = serializers.PrimaryKeyRelatedField(many=True, queryset=TaxDataSet.objects.all())
    class Meta:
        model = User
        fields = ['id', 'username', 'datasets', 'date_joined']

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        username = data.get('username')
        password = data.get('password')
        user = authenticate(username=username, password=password)
        if not user:
            raise serializers.ValidationError('Invalid credentials')
        return user

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=4)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["username", "password", "password_confirm"]

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("A user with this username already exists.")
        return value

    def validate(self, data):
        errors = {}
        if data["password"] != data["password_confirm"]:
            errors["password_confirm"] = "Passwords do not match"
        if errors:
            raise serializers.ValidationError(errors)

        return data

    @transaction.atomic
    def create(self, validated_data):
        """
        Create user with validated data, remove password validator
        """
        validated_data.pop('password_confirm')

        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password']
        )
        return user

class TaxYearDataDetailSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    class Meta:
        model = TaxYearData
        fields = ["id", "year", "filing_status", "taxable_income", "qualified_income", "is_electing", "elected_farm_income", "qualified_farm_income"]

    def validate(self, data):
        """Validate that year and filing status are in options."""
        if data["year"] not in VALID_YEARS_LIST:
            raise serializers.ValidationError(f"Year error. {data['year']} not valid.")
        if data["filing_status"] not in FILING_STATUS:
            raise serializers.ValidationError(f"Incorrect filing status. {data['filing_status']} not valid.")
        if data["taxable_income"] < 0 or data["qualified_income"] < 0:
            raise serializers.ValidationError("Income must be positive")
        return data

class SchJFormSerializer(serializers.Serializer):
    """
    Show total tax and the associated elected farm incomes.

    Eventually I should build where all Sch J lines can be serialized. Maybe have an arg for it.

    """

    line_23 = serializers.DecimalField(max_digits=12, decimal_places=2, min_value=0)
    line_2a = serializers.DecimalField(max_digits=12, decimal_places=2, min_value=0)
    line_2b = serializers.DecimalField(max_digits=12, decimal_places=2, min_value=0)
    tax_delta = serializers.DecimalField(max_digits=12, decimal_places=2)
    taxable_ordinary_results = serializers.JSONField()

class FarmIncomeWorksheetSerializer(serializers.Serializer):
    sch_f = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    wages = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    sch_c = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    sch_e = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    form_4835 = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    ccf = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    se_deduction = serializers.DecimalField(max_digits=10, decimal_places=2, max_value=0, required=False)
    qbi = serializers.DecimalField(max_digits=10, decimal_places=2, max_value=0, required=False)
    form_4797 = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    sch_d = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)

    def to_internal_value(self, data):
        """Validates as Decimal, but returns as floats for JSON serializer."""
        validated = super().to_internal_value(data)

        # Convert decimals to floats
        return {
            key: float(value) if isinstance(value, Decimal) and value is not None else value
            for key, value in validated.items()
        }

class TaxDataSetSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source="user.username")

    class Meta:
        model = TaxDataSet
        fields = ["id", "user", "name", "max_elected_farm_income", "qualified_farm_income", "election_year", "created_at"]

class TaxDataSetDetailSerializer(serializers.ModelSerializer):
    """Only general info and invididual tax years. Can use on FE form instances."""

    user = serializers.ReadOnlyField(source="user.username")
    tax_years = TaxYearDataDetailSerializer(many=True)

    class Meta:
        model = TaxDataSet
        fields = ["id", "user", "name", "max_elected_farm_income", "qualified_farm_income", "election_year", "tax_years"]

    def validate(self, data):
        """Validate the years only go to 2018."""
        current_year = DEFAULT_ELECTION_YEAR
        for i, year in enumerate(data["tax_years"]):
            if str(year["year"]) != str(current_year):
                msg = f"Year error. {year['year']} not valid."
                raise serializers.ValidationError(msg)
            year -= 1

class CreateCalculationSerializer(serializers.ModelSerializer):
    """Creates new tax data set and four tax years, all of which are empty."""

    tax_years = TaxYearDataDetailSerializer(many=True, required=False)

    class Meta:
        model = TaxDataSet
        fields = ["id", "tax_years"]
        read_only_fields = ["id"]

    @transaction.atomic
    def create(self, validated_data):
        dataset = TaxDataSet.objects.create(**validated_data)
        # Create 4 blank years
        new_year_obj_list = [TaxYearData.objects.create(dataset=dataset, year=int(DEFAULT_ELECTION_YEAR)-i) for i in range(4)]
        # First year has is_electing = True
        new_year_obj_list[0].is_electing = True
        return dataset

class CalculationEntrySerializer(serializers.ModelSerializer):
    """Deserialize input from form submission for TaxDataSet and TaxYearDatas. Requires all information."""

    tax_years = TaxYearDataDetailSerializer(many=True, required=True)
    income_worksheet = FarmIncomeWorksheetSerializer(many=False, required=False)

    class Meta:
        model = TaxDataSet
        fields = ["id", "name", "max_elected_farm_income", "qualified_farm_income", "election_year", "income_worksheet", "tax_years"]

    def validate(self, data):
        if data["max_elected_farm_income"] < 0 or data["qualified_farm_income"] < 0:
            raise serializers.ValidationError("Cannot have negative farm income")
        if sum(data["income_worksheet"].values()) != data["max_elected_farm_income"]:
            raise serializers.ValidationError("Farm income worksheet total not equal to max elected")
        validate_years_are_in_order(data["tax_years"])
        return data

    def update(self, instance, validated_data):
        years_data = validated_data.pop("tax_years", [])
        income_worksheet = validated_data.pop("income_worksheet", None)

        # Update TaxDataSet attributes
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

       # Pull existing TaxYearDatas based on ID from dataset instance
        existing_years = {y.id: y for y in instance.tax_years.all()}
        for year_dict in years_data:
            year_id = year_dict.get("id")

            if year_id not in existing_years:
                raise serializers.ValidationError(f"Invalid TaxYearData ID {year_id}")

            year_obj = existing_years[year_id]

            # Update TaxYearData attributes
            for attr, value in year_dict.items():
                setattr(year_obj, attr, value)
            year_obj.save()

        if income_worksheet is not None:
            instance.income_worksheet = income_worksheet

        instance.save()
        return instance

class OutputSerializer(serializers.ModelSerializer):
    """
    Prepare our inputs and outputs for results page. 
    Context dict should be provided that includes results from utils.update_calculations
    """
    tax_years = TaxYearDataDetailSerializer(many=True, required=True)
    income_worksheet = FarmIncomeWorksheetSerializer(many=False, allow_null=True, required=False)
    inputs = serializers.SerializerMethodField()
    outputs = serializers.SerializerMethodField()

    class Meta:
        model = TaxDataSet
        fields = ["name", "max_elected_farm_income", "qualified_farm_income", "election_year", "income_worksheet", "tax_years", "inputs", "outputs"]

    def get_inputs(self, instance):
        """Form for the general info, years, and income worksheet."""
        validate_only_four_tax_years(instance)
        return {
            "name": instance.name,
            "max_elected_farm_income": instance.max_elected_farm_income,
            "qualified_farm_income": instance.qualified_farm_income,
            "election_year": instance.election_year,
            "income_worksheet": instance.income_worksheet,
            "tax_years": TaxYearDataDetailSerializer(instance.tax_years.all(), many=True).data
        }

    def get_outputs(self, instance):
        """
        Results of calculations. Schedule J Form serialized in its own serializer.

        This serializer not very robust right now, but will keep for future expansion (like showing optimal results).
        """
        results = self.context.get("results")
        iterations = SchJFormSerializer(results, many=True).data
        bracket_thresholds = self.context.get("bracket_thresholds")

        return {
            "results": iterations,
            "bracket_thresholds": bracket_thresholds,
        }