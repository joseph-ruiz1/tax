from django.contrib.auth.models import Group, User
from rest_framework import serializers

from .models import FILING_STATUS, YEAR, TaxDataSet

class UserSerializer(serializers.ModelSerializer):
    datasets = serializers.PrimaryKeyRelatedField(many=True, queryset=TaxDataSet.objects.all())
    class Meta:
        model = User
        fields = ['id', 'username', 'datasets']

class TaxDataSetSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')
    class Meta:
        model = TaxDataSet
        fields = ["id", "user", "name", "max_elected_farm_income", "qualified_farm_income"]
