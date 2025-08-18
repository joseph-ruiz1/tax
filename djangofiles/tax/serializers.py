from rest_framework import serializers
from django.contrib.auth.models import Group, User
from django.contrib.auth import authenticate
from rest_framework import serializers

from .models import FILING_STATUS, YEAR, TaxDataSet

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

class TaxDataSetSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')
    class Meta:
        model = TaxDataSet
        fields = ["id", "user", "name", "max_elected_farm_income", "qualified_farm_income"]
