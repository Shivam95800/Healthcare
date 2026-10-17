"""
Doctor data model for CareOS.
"""
from django.db import models
from django.contrib.auth.models import User

class Doctor(models.Model):
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='doctors',
        db_index=True,
        help_text="User who created this doctor record"
    )
    name = models.CharField(max_length=255, db_index=True)
    specialization = models.CharField(max_length=150, db_index=True)
    email = models.EmailField(unique=True, db_index=True)
    phone = models.CharField(max_length=20)
    experience_years = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Doctor'
        verbose_name_plural = 'Doctors'

    def __str__(self):
        return f"Dr. {self.name} - {self.specialization}"
