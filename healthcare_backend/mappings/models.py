"""
Patient-Doctor Mapping model for CareOS.
"""
from django.db import models
from django.contrib.auth.models import User
from patients.models import Patient
from doctors.models import Doctor

class PatientDoctorMapping(models.Model):
    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name='doctor_mappings',
        db_index=True,
        help_text="Patient assigned to doctor"
    )
    doctor = models.ForeignKey(
        Doctor,
        on_delete=models.CASCADE,
        related_name='patient_mappings',
        db_index=True,
        help_text="Doctor assigned to patient"
    )
    assigned_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='assigned_mappings',
        db_index=True,
        help_text="User who made this assignment"
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        unique_together = (('patient', 'doctor'),)
        ordering = ['-created_at']
        verbose_name = 'Patient Doctor Mapping'
        verbose_name_plural = 'Patient Doctor Mappings'

    def __str__(self):
        return f"{self.patient.name} <-> {self.doctor.name}"
