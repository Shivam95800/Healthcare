"""
Patient data model for CareOS.
"""
from django.db import models
from django.contrib.auth.models import User

class Patient(models.Model):
    GENDER_CHOICES = (
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
        ('Prefer not to say', 'Prefer not to say'),
    )

    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='patients',
        db_index=True,
        help_text="User who created this patient record"
    )
    name = models.CharField(max_length=255, db_index=True)
    age = models.PositiveIntegerField()
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES, default='Other')
    phone = models.CharField(max_length=20)
    address = models.TextField()
    medical_history = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Patient'
        verbose_name_plural = 'Patients'

    def __str__(self):
        return f"{self.name} (Age: {self.age})"
