from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .models import *
from django.contrib.auth import login, logout
from rest_framework.response import Response
from .serializers import *
from .permissions import IsDoctor, IsAdmin, IsPatient, IsDoctorOrPatientOwner
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication
from django.db import IntegrityError


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