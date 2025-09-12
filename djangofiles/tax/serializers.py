from rest_framework import serializers
from django.contrib.auth.models import Group, User
from django.contrib.auth import authenticate
from rest_framework import serializers

from .models import FILING_STATUS, YEAR, TaxDataSet, TaxYearData, CalculationIteration, ScheduleJForm
from .utils import validate_tax_years

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        username = data.get('username')
        password = data.get('password')
        user = authenticate(username=username, password=password)
        if not user:
            raise serializers.ValidationError('Invalid credentials')
        data['user'] = user
        return data

class UserSerializer(serializers.ModelSerializer):
    datasets = serializers.PrimaryKeyRelatedField(many=True, queryset=TaxDataSet.objects.all())
    class Meta:
        model = User
        fields = ['id', 'username', 'datasets', 'date_joined']

class TaxYearDataDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaxYearData
        fields = ["id", "year", "filing_status", "taxable_income", "qualified_income"]

class SchJFormSerializer(serializers.ModelSerializer):
    """
    Show total tax and the associated elected farm incomes
    """
    class Meta:
        model = ScheduleJForm
        fields = ["line_23", 'line_2a', 'line_2b']

class CalculationIterationSerializer(serializers.ModelSerializer):
    """
    Serialize nested relationship to get SchJForm. ID is iteration #
    """
    form = SchJFormSerializer(many=False)

    class Meta:
        model = CalculationIteration
        fields = ["id", "form"]

class TaxDataSetSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')
    tax_years = TaxYearDataDetailSerializer(many=True, read_only=True)

    class Meta:
        model = TaxDataSet
        fields = ["id", "user", "name", "max_elected_farm_income", "qualified_farm_income", "tax_years"]

class TaxDataSetDetailSerializer(serializers.ModelSerializer):
    """
    Only general info and invididual tax years. Can use on FE form instances.
    """
    user = serializers.ReadOnlyField(source='user.username')
    tax_years = TaxYearDataDetailSerializer(many=True)

    class Meta:
        model = TaxDataSet
        fields = ["id", "user", "name", "max_elected_farm_income", "qualified_farm_income", "tax_years"]

    def validate(self, data):
        """
        Validate there are only 4 year instances for data entered before other serializations.
        """
        current_year = 2024
        for i, year in enumerate(data['tax_years']):
            if str(year['year']) != str(current_year):
                # TYPE ERROR WITH YEAR
                raise serializers.ValidationError(f"Year error. {year['year']} not valid.")
            year += 1

class CreateCalculationSerializer(serializers.ModelSerializer):
    """
    Creates new tax data set and four tax years, all of which are empty
    """
    tax_years = TaxYearDataDetailSerializer(many=True, required=False)
    class Meta:
        model = TaxDataSet
        fields = ["id", "tax_years"]
        read_only_fields = ["id"]
    
    def create(self, validated_data):
        dataset = TaxDataSet.objects.create(**validated_data)
        # Create 4 blank years
        year = 2024
        for _ in range(4):
            TaxYearData.objects.create(dataset=dataset, year=year)
            year -= 1
        return dataset

class CalculationEntrySerializer(serializers.ModelSerializer):
    """
    Deserialize input from form submission for TaxDataSet and 4 TaxYearDatas . Requires all information.
    """
    tax_years = TaxYearDataDetailSerializer(many=True, required=True)

    class Meta:
        model = TaxDataSet
        fields = ["name", "max_elected_farm_income", "qualified_farm_income", "tax_years"]
    
    def validate(self, data):
        """
        Validate that tax years are 2024 - 2021, filing status in options. 
        """
        if data['max_elected_farm_income'] < 0 or data['qualified_farm_income'] < 0:
            raise serializers.ValidationError("Cannot have negative farm income")
        current_year = 2024
        for i, year in enumerate(data['tax_years']):
            if str(year['year']) != str(current_year):
                raise serializers.ValidationError(f"Year error. {year['year']} not valid.")
            if year['filing_status'] not in FILING_STATUS.keys():
                raise serializers.ValidationError(f"Incorrect filing status. {year['filing_status']} not valid.")
            if year['taxable_income'] < 0 or year['qualified_income'] < 0:
                raise serializers.ValidationError("Income must be positive")
            current_year -= 1
        return data

    def update(self, instance, validated_data):
        years_data = validated_data.pop('tax_years', [])
        instance.name = validated_data.get('name', instance.name)
        instance.max_elected_farm_income = validated_data.get('max_elected_farm_income', instance.max_elected_farm_income)
        instance.qualified_farm_income = validated_data.get('qualified_farm_income', instance.qualified_farm_income)

        for i, year_data in enumerate(years_data):
            year = year_data['year']
            tax_year = instance.tax_years.get(year=str(year))
            year_serializer = TaxYearDataDetailSerializer(tax_year, data=year_data, partial=True)
            if year_serializer.is_valid(raise_exception=True):
                year_serializer.save()

        instance.save()
        return instance

class OutputSerializer(serializers.ModelSerializer):
    """
    Prepare get request data for output page
    """
    tax_years = TaxYearDataDetailSerializer(many=True, required=True)
    inputs = serializers.SerializerMethodField()
    outputs = serializers.SerializerMethodField()

    class Meta:
        model = TaxDataSet
        fields = ["name", "max_elected_farm_income", "qualified_farm_income", "tax_years", "inputs", "outputs"]

    def get_inputs(self, instance):
        """
        Form for front end to patch
        """
        validate_tax_years(instance)
        return {
            "name": instance.name,
            "max_elected_farm_income": instance.max_elected_farm_income,
            "qualified_farm_income": instance.qualified_farm_income,
            "tax_years": TaxYearDataDetailSerializer(instance.tax_years.all(), many=True).data
        }
    
    def get_outputs(self, instance):
        """
        Results of calculations. Previously computed upon patch. Manually extract iterations since inside method.
        """
        iterations_instances = instance.iterations.all()
        iterations = CalculationIterationSerializer(iterations_instances, many=True).data
        best_instance = instance.return_optimal_amount()
        best = SchJFormSerializer(best_instance).data
        return {
            'results': iterations,
            'best': best
        }