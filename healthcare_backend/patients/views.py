"""
Views for Patient endpoints.
"""
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from core.permissions import IsOwner
from .models import Patient
from .serializers import PatientSerializer

class PatientListCreateView(generics.ListCreateAPIView):
    """
    GET /api/patients/ - List only patients created by the authenticated user
    POST /api/patients/ - Create a patient, auto-setting created_by = request.user
    """
    serializer_class = PatientSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Patient.objects.filter(created_by=self.request.user).order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response({
            'success': True,
            'message': 'Patient record created successfully.',
            'data': serializer.data
        }, status=status.HTTP_201_CREATED, headers=headers)


class PatientDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET /api/patients/<id>/ - Retrieve patient (owner only)
    PUT /api/patients/<id>/ - Update patient (owner only)
    PATCH /api/patients/<id>/ - Partial update (owner only)
    DELETE /api/patients/<id>/ - Delete patient (owner only)
    """
    serializer_class = PatientSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]
    queryset = Patient.objects.all()

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response({
            'success': True,
            'message': 'Patient record updated successfully.',
            'data': serializer.data
        })

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({
            'success': True,
            'message': 'Patient record deleted successfully.'
        }, status=status.HTTP_200_OK)
