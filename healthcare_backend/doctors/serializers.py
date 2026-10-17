"""
Serializers for Doctor records.
"""
from rest_framework import serializers
from .models import Doctor

class DoctorSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.first_name', read_only=True)
    created_by_email = serializers.EmailField(source='created_by.email', read_only=True)

    class Meta:
        model = Doctor
        fields = (
            'id',
            'created_by',
            'created_by_name',
            'created_by_email',
            'name',
            'specialization',
            'email',
            'phone',
            'experience_years',
            'created_at',
            'updated_at'
        )
        read_only_fields = ('id', 'created_by', 'created_at', 'updated_at')

    def validate_experience_years(self, value):
        if value < 0 or value > 80:
            raise serializers.ValidationError("Experience years must be between 0 and 80.")
        return value

    def validate_name(self, value):
        stripped = value.strip()
        if not stripped:
            raise serializers.ValidationError("Doctor name cannot be empty.")
        return stripped

    def validate_specialization(self, value):
        stripped = value.strip()
        if not stripped:
            raise serializers.ValidationError("Specialization cannot be empty.")
        return stripped
