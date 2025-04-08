from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsPatient(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'patient'

class IsDoctor(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'doctor'

class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'admin'


class IsDoctorOrPatientOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        user = request.user
        return (
            (hasattr(user, 'doctor_profile') and obj.doctor.user == user) or
            (hasattr(user, 'patient_profile') and obj.patient.user == user)
        )

class IsDoctorOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.is_superuser:
            return True
        if hasattr(user, 'doctor_profile') and obj.doctor == user.doctor_profile:
            return True
        if hasattr(user, 'patient_profile') and obj.patient == user.patient_profile:
            return request.method in SAFE_METHODS
        return False