"""
Serializers for Patient-Doctor Mapping in CareOS.
"""
from rest_framework import serializers
from patients.models import Patient
from doctors.models import Doctor
from .models import PatientDoctorMapping

class PatientDoctorMappingSerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(source='patient.name', read_only=True)
    patient_age = serializers.IntegerField(source='patient.age', read_only=True)
    patient_gender = serializers.CharField(source='patient.gender', read_only=True)
    doctor_name = serializers.CharField(source='doctor.name', read_only=True)
    doctor_specialization = serializers.CharField(source='doctor.specialization', read_only=True)
    doctor_email = serializers.EmailField(source='doctor.email', read_only=True)
    assigned_by_name = serializers.CharField(source='assigned_by.first_name', read_only=True)

    class Meta:
        model = PatientDoctorMapping
        fields = (
            'id',
            'patient',
            'patient_name',
            'patient_age',
            'patient_gender',
            'doctor',
            'doctor_name',
            'doctor_specialization',
            'doctor_email',
            'assigned_by',
            'assigned_by_name',
            'created_at',
        )
        read_only_fields = ('id', 'assigned_by', 'created_at')

    def validate(self, attrs):
        request = self.context.get('request')
        patient = attrs.get('patient')
        doctor = attrs.get('doctor')

        if request and request.user:
            # Rule: patient must belong to the authenticated user
            if patient.created_by != request.user:
                raise serializers.ValidationError({
                    'patient': 'You can only assign doctors to patients you created.'
                })

        # Rule: reject duplicate patient-doctor mapping
        if PatientDoctorMapping.objects.filter(patient=patient, doctor=doctor).exists():
            raise serializers.ValidationError({
                'duplicate': 'This doctor is already assigned to this patient.'
            })

        return attrs
