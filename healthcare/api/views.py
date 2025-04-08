from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .models import *
from django.contrib.auth import login, logout
from rest_framework.response import Response
from .serializers import *
from .permissions import *
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication
from datetime import datetime, timedelta
from django.shortcuts import get_object_or_404

class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({'role': user.role}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]
    def post(self, request):
            serializer = LoginSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            email = serializer.validated_data.get('email')
            password = serializer.validated_data.get('password')

            user = authenticate(email=email, password=password)
            if not user:
                return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

            login(request, user)
            print(request.user)
            token, created = Token.objects.get_or_create(user=user)
            return Response({'token': token.key, 'role': user.role}, status=status.HTTP_200_OK)

class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def post(self, request):
        request.user.auth_token.delete()
        logout(request)
        return Response({"message": "Logged out successfully."}, status=status.HTTP_200_OK)


# patient views

class PatientProfileView(APIView):
    permission_classes = [IsPatient]
    serializer_class = PatientSerializer

    def get(self, request):
        try:
            patient = request.user.patient_profile
            serializer = self.serializer_class(patient)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Patient.DoesNotExist:
            return Response({"error": "Patient profile not found."}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request):
        if hasattr(request.user, 'patient_profile'):
            return Response({"error": "Patient profile already exists."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        try:
            patient = request.user.patient_profile
            serializer = self.serializer_class(patient, data=request.data, partial=True)
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

# doctor views
class DoctorProfileView(APIView):
    permission_classes = [IsDoctor]
    serializer_class = DoctorSerializer

    def get(self, request):
        try:
            doctor = request.user.doctor_profile
            serializer = self.serializer_class(doctor)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Doctor.DoesNotExist:
            return Response({"error": "Doctor profile not found."}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request):
        if hasattr(request.user, 'doctor_profile'):
            return Response({"error": "Doctor profile already exists."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        try:
            doctor = request.user.doctor_profile
            serializer = self.serializer_class(doctor, data=request.data, partial=True)
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

# appointment endpoints
class AppointmentView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        if hasattr(user, 'patient_profile'):
            appointments = Appointment.objects.filter(patient=user.patient_profile)
        elif hasattr(user, 'doctor_profile'):
            appointments = Appointment.objects.filter(doctor=user.doctor_profile)
        else:
            return Response({"error": "Unauthorized user."}, status=status.HTTP_403_FORBIDDEN)

        serializer = AppointmentSerializer(appointments, many=True)
        return Response({
            "message": "Appointments fetched successfully.",
            "appointments": serializer.data
        })

    def post(self, request):
        if not hasattr(request.user, 'patient_profile'):
            return Response({"error": "Only patients can book appointments."}, status=status.HTTP_403_FORBIDDEN)

        serializer = AppointmentSerializer(data=request.data)
        if serializer.is_valid():
            doctor = serializer.validated_data['doctor']
            date = serializer.validated_data['date']
            time = serializer.validated_data['time']

            if Appointment.objects.filter(doctor=doctor, date=date, time=time).exists():
                return Response({
                    "message": "This slot is already booked.",
                    "available": False
                }, status=status.HTTP_409_CONFLICT)

            appointment = serializer.save(patient=request.user.patient_profile)
            return Response({
                "message": "Appointment booked successfully.",
                "appointment": AppointmentSerializer(appointment).data,
                "available": True
            }, status=status.HTTP_201_CREATED)

        return Response({"message": "Validation failed.", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

class AppointmentUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, appointment_id):
        try:
            appointment = Appointment.objects.get(id=appointment_id)
        except Appointment.DoesNotExist:
            return Response({"error": "Appointment not found."}, status=status.HTTP_404_NOT_FOUND)

        if hasattr(request.user, 'doctor_profile') and appointment.doctor == request.user.doctor_profile:
            status_value = request.data.get("status")
            if status_value:
                appointment.status = status_value
                appointment.save()
                return Response({
                    "message": "Appointment status updated.",
                    "appointment": AppointmentSerializer(appointment).data
                })
            return Response({"error": "No status provided."}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"error": "You are not authorized to update this appointment."}, status=status.HTTP_403_FORBIDDEN)

    def delete(self, request, appointment_id):
        try:
            appointment = Appointment.objects.get(id=appointment_id)
        except Appointment.DoesNotExist:
            return Response({"error": "Appointment not found."}, status=status.HTTP_404_NOT_FOUND)
        user = request.user
        if not (user.is_superuser or (hasattr(user, 'doctor_profile') or hasattr(request.user, 'patient_profile') and appointment.doctor == user.doctor_profile or appointment.patient == user.patient_profile)):
            return Response({"error": "You do not have permission to delete this appointment."}, status=status.HTTP_403_FORBIDDEN)

        appointment.delete()
        return Response({'message': 'Appointment deleted successfully.'}, status=status.HTTP_204_NO_CONTENT)



class DoctorAvailabilityView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, doctor_id):
        date_str = request.query_params.get('date')  # YYYY-MM-DD
        time_str = request.query_params.get('time')  # Optional HH:MM:SS

        if not date_str:
            return Response({"error": "'date' query parameter is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            doctor = Doctor.objects.get(id=doctor_id)
        except Doctor.DoesNotExist:
            return Response({"error": "Doctor not found."}, status=status.HTTP_404_NOT_FOUND)

        # Check single time slot
        if time_str:
            is_booked = Appointment.objects.filter(doctor=doctor, date=date_str, time=time_str).exists()
            return Response({
                "doctor_id": doctor_id,
                "date": date_str,
                "time": time_str,
                "available": not is_booked
            })

        # Full day availability
        start_time = datetime.strptime("08:00", "%H:%M")
        end_time = datetime.strptime("17:00", "%H:%M")
        slot_duration = timedelta(minutes=30)

        booked_times = set(
            Appointment.objects.filter(doctor=doctor, date=date_str)
            .values_list('time', flat=True)
        )

        time_slots = []
        current = start_time
        while current < end_time:
            slot_str = current.time().strftime("%H:%M")
            time_slots.append({
                "time": slot_str,
                "available": current.time() not in booked_times
            })
            current += slot_duration

        return Response({
            "doctor_id": doctor_id,
            "date": date_str,
            "time_slots": time_slots
        })

# medical records
class MedicalRecordListCreateView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        user = request.user
        if user.is_superuser:
            records = MedicalRecord.objects.all()
        elif hasattr(user, 'doctor_profile'):
            records = MedicalRecord.objects.filter(doctor=user.doctor_profile)
        elif hasattr(user, 'patient_profile'):
            records = MedicalRecord.objects.filter(patient=user.patient_profile)
        else:
            return Response({'error': 'Unauthorized access'}, status=status.HTTP_403_FORBIDDEN)

        serializer = MedicalRecordSerializer(records, many=True)
        return Response(serializer.data)

    def post(self, request):
        user = request.user
        if not (user.is_superuser or hasattr(user, 'doctor_profile')):
            return Response({'error': 'Only doctors or admins can create medical records.'}, status=status.HTTP_403_FORBIDDEN)

        serializer = MedicalRecordSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(doctor=user.doctor_profile if hasattr(user, 'doctor_profile') else None)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class MedicalRecordDetailView(APIView):
    permission_classes = [IsAuthenticated]


    def patch(self, request, pk):
        try:
            record = MedicalRecord.objects.get(id=pk)
        except MedicalRecord.DoesNotExist:
            return Response({"error": "Record not found."}, status=status.HTTP_404_NOT_FOUND)
        user = request.user
        if not (user.is_superuser or (hasattr(user, 'doctor_profile') and record.doctor == user.doctor_profile)):
            return Response({'error': 'You do not have permission to update this record.'}, status=status.HTTP_403_FORBIDDEN)

        serializer = MedicalRecordSerializer(record, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            record = MedicalRecord.objects.get(id=pk)
        except MedicalRecord.DoesNotExist:
            return Response({"error": "Record not found."}, status=status.HTTP_404_NOT_FOUND)
        user = request.user
        if not (user.is_superuser or (hasattr(user, 'doctor_profile') and record.doctor == user.doctor_profile)):
            return Response({'error': 'You do not have permission to delete this record.'}, status=status.HTTP_403_FORBIDDEN)

        record.delete()
        return Response({'message': 'Record deleted successfully.'}, status=status.HTTP_204_NO_CONTENT)