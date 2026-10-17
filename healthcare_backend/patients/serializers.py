"""
Serializers for Patient records.
"""
from rest_framework import serializers
from .models import Patient

class PatientSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.first_name', read_only=True)
    created_by_email = serializers.EmailField(source='created_by.email', read_only=True)

    class Meta:
        model = Patient
        fields = (
            'id',
            'created_by',
            'created_by_name',
            'created_by_email',
            'name',
            'age',
            'gender',
            'phone',
            'address',
            'medical_history',
            'created_at',
            'updated_at'
        )
        read_only_fields = ('id', 'created_by', 'created_at', 'updated_at')

    def validate_age(self, value):
        if value <= 0 or value > 130:
            raise serializers.ValidationError("Please provide a valid age between 1 and 130.")
        return value

    def validate_name(self, value):
        stripped = value.strip()
        if not stripped:
            raise serializers.ValidationError("Patient name cannot be empty.")
        return stripped
