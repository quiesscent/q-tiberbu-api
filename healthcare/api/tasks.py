# from celery import shared_task
# from django.core.mail import send_mail
# from .models import Appointment

# @shared_task
# def send_appointment_confirmation_email(appointment_id):
#     appointment = Appointment.objects.get(id=appointment_id)
#     subject = f"Appointment Confirmed: {appointment.date} {appointment.time}"
#     message = f"Your appointment with Dr. {appointment.doctor.full_name} is confirmed."
#     recipient = appointment.patient.user.email
#     send_mail(subject, message, 'from@example.com', [recipient])

# @shared_task
# def create_medical_record_after_appointment(appointment_id):
#     appointment = Appointment.objects.get(id=appointment_id)
#     # Assuming you've already set up a MedicalRecord model as per earlier steps
#     # Automatically create a medical record after a completed appointment
#     from records.models import MedicalRecord
#     MedicalRecord.objects.create(
#         patient=appointment.patient,
#         doctor=appointment.doctor,
#         appointment=appointment,
#         diagnosis="No diagnosis yet",
#         prescription="None",
#         notes="Follow-up in a week"
#     )
