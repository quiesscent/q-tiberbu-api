# signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import CustomUser, Doctor, Patient

@receiver(post_save, sender=CustomUser)
def create_doctor_profile(sender, instance, created, **kwargs):
    if created and instance.role == 'doctor':
        Doctor.objects.create(
            user=instance,
            full_name=instance.get_full_name(),
            specialization='General',  # or leave it blank to be filled later
            available_days=["Monday", "Tuesday"],
            available_time_start="09:00:00",
            available_time_end="17:00:00"
        )

@receiver(post_save, sender=CustomUser)
def create_doctor_profile(sender, instance, created, **kwargs):
    if created and instance.role == 'patient':
        Patient.objects.create(
            user=instance,
            full_name=instance.username,
        )