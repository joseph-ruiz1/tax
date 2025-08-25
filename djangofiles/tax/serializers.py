from rest_framework import serializers
from django.contrib.auth.models import Group, User
from django.contrib.auth import authenticate
from rest_framework import serializers

from .models import FILING_STATUS, YEAR, TaxDataSet, TaxYearData

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
        fields = "__all__"


class TaxDataSetSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')
    tax_years = TaxYearDataDetailSerializer(many=True, read_only=True)

    class Meta:
        model = TaxDataSet
        fields = ["id", "user", "name", "max_elected_farm_income", "qualified_farm_income", "tax_years"]

class TaxDataSetDetailSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')
    tax_years = TaxYearDataDetailSerializer(many=True)

    class Meta:
        model = TaxDataSet
        fields = ["id", "user", "name", "max_elected_farm_income", "qualified_farm_income", "tax_years"]


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
        for _ in range(4):
            year = 2024
            TaxYearData.objects.create(dataset=dataset, year=year)
            year -= 1
        return dataset

class CalculationEntrySerializer(serializers.ModelSerializer):
    """
    Valiate input for TaxDataSet and 4 TaxYearDatas. Requires all information.
    """
    tax_years = TaxYearDataDetailSerializer(many=True, required=True)

    class Meta:
        model = TaxDataSet
        fields = ["name", "max_elected_farm_income", "qualified_farm_income", "tax_years"]
    
    def update(self, instance, validated_data):
        years_data = validated_data.pop('tax_years', [])
        instance.name = validated_data.get('name', instance.name)
        instance.max_elected_farm_income = validated_data.get('max_elected_farm_income', instance.max_elected_farm_income)
        instance.qualified_farm_income = validated_data.get('qualified_farm_income', instance.qualified_farm_income)
        instance.save()

        for i, year_data in enumerate(years_data):
            year = year_data['year']
            tax_year = instance.tax_years.get(year=str(year))
            print(f"===>{tax_year}")
            year_serializer = TaxYearDataDetailSerializer(tax_year, data=year_data, partial=True)
            if year_serializer.is_valid(raise_exception=True):
                year_serializer.save()
        return instance

    def validate(self, data):
        """
        Validate that tax years are 2024 - 2021, filing status in options. 
        """
        if data['max_elected_farm_income'] < 0 or data['qualified_farm_income'] < 0:
            raise serializers.ValidationError("Cannot have negative farm income")
        current_year = 2024
        for i, year in enumerate(data['tax_years']):
            if str(year['year']) != str(current_year):
                # TYPE ERROR WITH YEAR
                raise serializers.ValidationError(f"Year error. {year['year']} not valid.")
            if year['filing_status'] not in FILING_STATUS:
                raise serializers.ValidationError(f"Incorrect filing status. {year['filing_status']} not valid.")
            if year['taxable_income'] < 0 or year['qualified_income'] < 0:
                raise serializers.ValidationError("Income must be positive")
            current_year -= 1
        return data