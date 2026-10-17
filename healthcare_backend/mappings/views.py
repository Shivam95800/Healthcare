"""
Views for PatientDoctorMapping endpoints.
"""
from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from patients.models import Patient
from .models import PatientDoctorMapping
from .serializers import PatientDoctorMappingSerializer

class MappingListCreateView(generics.ListCreateAPIView):
    """
    GET /api/mappings/ - List all mappings (select_related patient, doctor, assigned_by)
    POST /api/mappings/ - Assign a doctor to a patient (patient must belong to user, no duplicates)
    """
    serializer_class = PatientDoctorMappingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return PatientDoctorMapping.objects.select_related(
            'patient', 'doctor', 'assigned_by'
        ).order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(assigned_by=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response({
            'success': True,
            'message': 'Doctor successfully assigned to patient.',
            'data': serializer.data
        }, status=status.HTTP_201_CREATED, headers=headers)


class PatientMappingDetailView(APIView):
    """
    Handles:
    - GET /api/mappings/<patient_id>/ : all doctors assigned to that patient
    - DELETE /api/mappings/<id>/ : remove a doctor from a patient (by mapping ID)
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk, *args, **kwargs):
        # Query mappings for this patient_id
        mappings = PatientDoctorMapping.objects.filter(
            patient_id=pk
        ).select_related('patient', 'doctor', 'assigned_by').order_by('-created_at')

        if mappings.exists():
            serializer = PatientDoctorMappingSerializer(mappings, many=True)
            return Response({
                'success': True,
                'patient_id': pk,
                'count': mappings.count(),
                'doctors': serializer.data
            }, status=status.HTTP_200_OK)

        # Fallback: check if pk is a specific mapping ID
        single_mapping = PatientDoctorMapping.objects.filter(id=pk).select_related('patient', 'doctor', 'assigned_by').first()
        if single_mapping:
            serializer = PatientDoctorMappingSerializer(single_mapping)
            return Response({
                'success': True,
                'data': serializer.data
            }, status=status.HTTP_200_OK)

        # If patient exists with no mappings
        if Patient.objects.filter(id=pk).exists():
            return Response({
                'success': True,
                'patient_id': pk,
                'count': 0,
                'doctors': []
            }, status=status.HTTP_200_OK)

        return Response({
            'success': False,
            'message': f'No patient or mapping found with ID {pk}.',
            'errors': {'id': [f'Record {pk} not found.']}
        }, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, pk, *args, **kwargs):
        mapping = PatientDoctorMapping.objects.filter(id=pk).first()
        if not mapping:
            return Response({
                'success': False,
                'message': f'Mapping record with ID {pk} does not exist.',
                'errors': {'id': ['Mapping not found.']}
            }, status=status.HTTP_404_NOT_FOUND)

        # Authorization: can be deleted by creator of patient or the user who assigned it
        if mapping.assigned_by != request.user and mapping.patient.created_by != request.user:
            return Response({
                'success': False,
                'message': 'You do not have permission to remove this mapping.',
                'errors': {'permission': ['Only the creator or assigner can remove this mapping.']}
            }, status=status.HTTP_403_FORBIDDEN)

        mapping.delete()
        return Response({
            'success': True,
            'message': 'Doctor mapping removed successfully.'
        }, status=status.HTTP_200_OK)
