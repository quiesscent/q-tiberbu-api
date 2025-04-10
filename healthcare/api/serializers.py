from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import *
from datetime import datetime
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ['email', 'username', 'password', 'role']

    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            email=validated_data['email'],
            username=validated_data['username'],
            password=validated_data['password'],
            role=validated_data.get('role', 'patient')
        )
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = '__all__'
        read_only_fields = ['user']

class DoctorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Doctor
        fields = '__all__'
        read_only_fields = ['user']

    def validate_available_days(self, value):
        valid_days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

        if not isinstance(value, dict):
            raise serializers.ValidationError("available_days must be a dictionary.")

        for day, time_range in value.items():
            if day not in valid_days:
                raise serializers.ValidationError(f"'{day}' is not a valid weekday.")

            if not isinstance(time_range, dict):
                raise serializers.ValidationError(f"The time range for '{day}' must be a dictionary.")

            start = time_range.get('start')
            end = time_range.get('end')

            if not start or not end:
                raise serializers.ValidationError(f"'{day}' must have both 'start' and 'end' times.")

            try:
                start_time = datetime.datetime.strptime(start, "%H:%M").time()
                end_time = datetime.datetime.strptime(end, "%H:%M").time()
            except ValueError:
                raise serializers.ValidationError(f"Invalid time format for '{day}'. Use 'HH:MM'.")

            if start_time >= end_time:
                raise serializers.ValidationError(f"For '{day}', start time must be earlier than end time.")

        return value

class AppointmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = '__all__'
        read_only_fields = ['patient']

class MedicalRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicalRecord
        fields = '__all__'
        read_only_fields = ['doctor']
