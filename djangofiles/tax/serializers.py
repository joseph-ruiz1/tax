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
    tax_years = serializers.PrimaryKeyRelatedField(many=True, queryset=TaxYearData.objects.all())
    class Meta:
        model = TaxDataSet
        fields = ["id", "user", "name", "max_elected_farm_income", "qualified_farm_income", "tax_years"]

class TaxDataSetDetailSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')
    tax_years = TaxYearDataDetailSerializer(many=True)

    class Meta:
        model = TaxDataSet
        fields = ["id", "user", "name", "max_elected_farm_income", "qualified_farm_income", "tax_years"]

class CalculationEntrySerializer(serializers.ModelSerializer):
    """
    Valiate input for TaxDataSet and 4 TaxYearDatas. Requires all information.
    """
    tax_years = TaxYearDataDetailSerializer(many=True, required=False)

    class Meta:
        model = TaxDataSet
        fields = ["name", "max_elected_farm_income", "qualified_farm_income", "tax_years"]
    
    def create(self, validated_data):
        tax_years_data = validated_data.pop('tax_years')
        dataset = TaxDataSet.objects.create(**validated_data)
        for tax_year_data in tax_years_data:
            TaxYearData.objects.create(dataset=dataset, **tax_year_data)
        return dataset
