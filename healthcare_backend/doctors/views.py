"""
Views for Doctor endpoints.
"""
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from core.permissions import IsCreatorOrReadOnly
from .models import Doctor
from .serializers import DoctorSerializer

class DoctorListCreateView(generics.ListCreateAPIView):
    """
    GET /api/doctors/ - List all doctors (select_related created_by)
    POST /api/doctors/ - Add a doctor (auto-sets created_by = request.user)
    """
    serializer_class = DoctorSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Doctor.objects.select_related('created_by').order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response({
            'success': True,
            'message': 'Doctor profile created successfully.',
            'data': serializer.data
        }, status=status.HTTP_201_CREATED, headers=headers)


class DoctorDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET /api/doctors/<id>/ - View doctor details (authenticated users)
    PUT /api/doctors/<id>/ - Update doctor (creator only)
    PATCH /api/doctors/<id>/ - Partial update (creator only)
    DELETE /api/doctors/<id>/ - Delete doctor (creator only)
    """
    serializer_class = DoctorSerializer
    permission_classes = [permissions.IsAuthenticated, IsCreatorOrReadOnly]
    queryset = Doctor.objects.select_related('created_by').all()

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response({
            'success': True,
            'message': 'Doctor profile updated successfully.',
            'data': serializer.data
        })

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({
            'success': True,
            'message': 'Doctor profile deleted successfully.'
        }, status=status.HTTP_200_OK)
