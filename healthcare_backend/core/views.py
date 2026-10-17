"""
Frontend template views and system status endpoints for CareOS.
"""
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from django.contrib.auth.models import User
from patients.models import Patient
from doctors.models import Doctor
from mappings.models import PatientDoctorMapping

def landing_view(request):
    """Render Kuber-OS-style CareOS landing page."""
    return render(request, 'landing.html')

def console_view(request):
    """Render CareOS Controller Console."""
    return render(request, 'console.html')

def login_view(request):
    """Render Login page."""
    return render(request, 'login.html')

def register_view(request):
    """Render Registration page."""
    return render(request, 'register.html')


class DashboardStatsView(APIView):
    """
    GET /api/stats/ - Public or authenticated summary metrics for console & landing.
    """
    permission_classes = [permissions.AllowAny]

    def get(self, request, *args, **kwargs):
        user = request.user if request.user.is_authenticated else None
        
        total_patients = Patient.objects.count()
        total_doctors = Doctor.objects.count()
        total_mappings = PatientDoctorMapping.objects.count()

        user_patients = Patient.objects.filter(created_by=user).count() if user else 0
        user_mappings = PatientDoctorMapping.objects.filter(assigned_by=user).count() if user else 0

        return Response({
            'success': True,
            'total_patients': total_patients,
            'total_doctors': total_doctors,
            'total_mappings': total_mappings,
            'user_patients': user_patients,
            'user_mappings': user_mappings,
            'system_status': 'Operational',
            'orm_engine': 'PostgreSQL'
        })
