"""URL Configuration for the ResumeIQ analyzer app."""
from django.urls import path
from . import views

app_name = 'analyzer'

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('api/analyze/', views.analyze_resume_api, name='analyze_resume'),
    path('api/sample-jobs/', views.sample_jobs_api, name='sample_jobs'),
]
