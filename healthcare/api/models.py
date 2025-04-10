from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('patient', 'Patient'),
        ('doctor', 'Doctor'),
        ('admin', 'Admin'),
    )

    email = models.EmailField(unique=True)
    username = models.CharField(max_length=50, unique=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username','role',]

    class Meta:
        verbose_name_plural ='Users'

    def __str__(self):
        return self.email


class Patient(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='patient_profile')
    full_name = models.CharField(max_length=255)
    age = models.PositiveIntegerField(default=0)
    gender = models.CharField(max_length=10, choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')])
    phone = models.CharField(max_length=20)
    address = models.TextField()
    insurance_number = models.CharField(max_length=50, blank=True, null=True)
    insurance_provider = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.full_name

class Doctor(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='doctor_profile')
    full_name = models.CharField(max_length=255)
    specialization = models.CharField(max_length=100)
    bio = models.TextField(blank=True, null=True)

    # simple availability as days + time range
    available_days = models.JSONField(default=dict)

    def __str__(self):
        return f"{self.full_name} - {self.specialization}"

STATUS_CHOICES = [
    ('pending', 'Pending'),
    ('confirmed', 'Confirmed'),
    ('cancelled', 'Cancelled'),
    ('completed', 'Completed'),
]

class Appointment(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    date = models.DateField()
    time = models.TimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    reason = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ('doctor', 'date', 'time')  # prevents double-booking

    def __str__(self):
        return f"{self.date} - {self.time} with Dr. {self.doctor.full_name}"

class MedicalRecord(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='medical_records')
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='created_records')
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE, null=True, blank=True)
    diagnosis = models.TextField()
    treatment = models.TextField()
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Record for {self.patient.full_name} by Dr. {self.doctor.full_name}"
