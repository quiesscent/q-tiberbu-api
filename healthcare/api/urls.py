from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *


urlpatterns = [
    # authentications
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),

    # # profiles
    path('patients/profile/', PatientProfileView.as_view(), name='patient-profile'),
    path('doctors/profile/', DoctorProfileView.as_view(), name='doctor-profile'),

    # # appointments management
    path('appointments/', AppointmentView.as_view(), name='appointments'),
    path('appointments/<int:appointment_id>/', AppointmentUpdateView.as_view(), name='appointment-update'),
    path('appointments/doctor/<int:doctor_id>/availability/', DoctorAvailabilityView.as_view(), name='doctor-availability'),

    # medical records
    path('medical-records/', MedicalRecordListCreateView.as_view(), name='medical-records'),
    path('medical-records/<int:pk>/', MedicalRecordDetailView.as_view(), name='medical-record-detail'),
]