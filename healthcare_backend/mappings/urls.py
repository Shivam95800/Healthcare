"""
URL patterns for PatientDoctorMapping endpoints.
"""
from django.urls import path
from .views import MappingListCreateView, PatientMappingDetailView

urlpatterns = [
    path('', MappingListCreateView.as_view(), name='mapping-list-create'),
    path('<int:pk>/', PatientMappingDetailView.as_view(), name='mapping-detail'),
]
