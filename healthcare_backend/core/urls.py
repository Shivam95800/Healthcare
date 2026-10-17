"""
Core URL configuration for frontend pages and stats.
"""
from django.urls import path
from .views import landing_view, console_view, login_view, register_view, DashboardStatsView

urlpatterns = [
    path('', landing_view, name='landing'),
    path('console/', console_view, name='console'),
    path('login/', login_view, name='login'),
    path('register/', register_view, name='register'),
    path('api/stats/', DashboardStatsView.as_view(), name='api-stats'),
]
