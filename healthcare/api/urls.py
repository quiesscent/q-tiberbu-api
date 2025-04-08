from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *


urlpatterns = [
    # authentications
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),

    # # profiles
    path('patients/profile/', PatientProfileView.as_view()),
    path('doctors/profile/', DoctorProfileView.as_view()),

    # # appointments management
    # path('appointments/', AppointmentAPIGetCreateView.as_view(), name='appointments'),
    # path('appointments/<int:appointment_id>/', AppointmentAPIUpdateView.as_view(), name='appointment-update'),

    # # medical records
    # path('medical-records/', MedicalRecordCreateViewAPIView.as_view(), name='medical-records'),
    # path('medical-records/<int:record_id>/', MedicalRecordUpdateDeleteAPIView.as_view(), name='medical-record-detail'),
]