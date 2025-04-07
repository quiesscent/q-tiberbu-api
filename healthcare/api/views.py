from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .models import *
from django.contrib.auth import login, logout
from rest_framework.response import Response
from .serializers import *
from .permissions import IsDoctor, IsAdmin
from rest_framework.authtoken.models import Token
from django.db import IntegrityError

class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, created = Token.objects.get_or_create(user=user)
            return Response({'token': token.key, 'role': user.role}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data
            login(request, user)
            token, created = Token.objects.get_or_create(user=user)
            return Response({'token': token.key, 'role': user.role}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)


class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        request.user.auth_token.delete()
        logout(request)
        return Response({"message": "Logged out successfully."}, status=status.HTTP_200_OK)



class PatientProfileView(generics.CreateAPIView):
    # queryset = Patient.objects.all()
    # serializer_class = PatientSerializer

    def get(self, request):
        try:
            patient = request.user.patient_profile
            serializer = PatientSerializer(patient)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Patient.DoesNotExist:
            return Response({"error": "Patient profile not found."}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request):
        try:
            patient = request.user.patient_profile
            serializer = PatientSerializer(patient, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Patient.DoesNotExist:
            return Response({"error": "Patient profile not found."}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request):
        try:
            patient = request.user.patient_profile
            patient.delete()
            return Response({"message": "Patient profile deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
        except Patient.DoesNotExist:
            return Response({"error": "Patient profile not found."}, status=status.HTTP_404_NOT_FOUND)

class DoctorProfileView(APIView):

    def get(self, request):
        try:
            doctor = request.user.doctor_profile
            serializer = DoctorSerializer(doctor)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Doctor.DoesNotExist:
            return Response({"error": "Doctor profile not found."}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request):
        try:
            doctor = request.user.doctor_profile
            serializer = DoctorSerializer(doctor, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Doctor.DoesNotExist:
            return Response({"error": "Doctor profile not found."}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request):
        try:
            doctor = request.user.doctor_profile
            doctor.delete()
            return Response({"message": "Doctor profile deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
        except Doctor.DoesNotExist:
            return Response({"error": "Doctor profile not found."}, status=status.HTTP_404_NOT_FOUND)


class AppointmentAPIGetCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        if hasattr(user, 'doctor_profile'):
            appointments = Appointment.objects.filter(doctor=user.doctor_profile)
        elif hasattr(user, 'patient_profile'):
            appointments = Appointment.objects.filter(patient=user.patient_profile)
        else:
            return Response({"error": "Not authorized."}, status=status.HTTP_403_FORBIDDEN)

        serializer = AppointmentSerializer(appointments, many=True)
        return Response(serializer.data)

    def post(self, request):
        user = request.user
        if not hasattr(user, 'patient_profile'):
            return Response({"error": "Only patients can create appointments."}, status=status.HTTP_403_FORBIDDEN)

        serializer = AppointmentSerializer(data=request.data)
        if serializer.is_valid():
            try:
                appointment = serializer.save(patient=user.patient_profile)
                return Response(AppointmentSerializer(appointment).data, status=status.HTTP_201_CREATED)
            except IntegrityError:
                return Response({"error": "This time slot is already booked."}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
class AppointmentAPIUpdateView(APIView):
    def put(self, request, appointment_id):
        try:
            appointment = Appointment.objects.get(id=appointment_id)
        except Appointment.DoesNotExist:
            return Response({"error": "Appointment not found."}, status=status.HTTP_404_NOT_FOUND)

        user = request.user
        if hasattr(user, 'patient_profile') and appointment.patient != user.patient_profile:
            return Response({"error": "You can only update your own appointments."}, status=status.HTTP_403_FORBIDDEN)

        if hasattr(user, 'doctor_profile') and appointment.doctor != user.doctor_profile:
            return Response({"error": "You can only update your own appointments."}, status=status.HTTP_403_FORBIDDEN)

        # Restrict doctors from changing reason or date
        if hasattr(user, 'doctor_profile'):
            # Remove reason and date from the update data for doctors
            request_data = request.data.copy()
            request_data.pop('reason', None)
            request_data.pop('date', None)

            serializer = AppointmentSerializer(appointment, data=request_data, partial=True)
        else:
            serializer = AppointmentSerializer(appointment, data=request.data, partial=True)

        if serializer.is_valid():
            try:
                serializer.save()
                return Response(serializer.data)
            except IntegrityError:
                return Response({"error": "Time conflict with another appointment."}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, appointment_id):
        # status update
        try:
            appointment = Appointment.objects.get(id=appointment_id)
        except Appointment.DoesNotExist:
            return Response({"error": "Appointment not found."}, status=status.HTTP_404_NOT_FOUND)

        # Check if the user is the doctor of the appointment
        if hasattr(request.user, 'doctor_profile') and appointment.doctor != request.user.doctor_profile:
            return Response({"error": "You can only update the status of appointments assigned to you."}, status=status.HTTP_403_FORBIDDEN)

        new_status = request.data.get("status")
        if new_status not in ['pending', 'confirmed', 'cancelled', 'completed']:
            return Response({"error": "Invalid status."}, status=status.HTTP_400_BAD_REQUEST)

        appointment.status = new_status
        appointment.save()
        return Response({"message": "Status updated successfully."}, status=status.HTTP_200_OK)