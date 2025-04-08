from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from .models import *
from rest_framework.exceptions import NotFound
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model
from datetime import datetime

class RegisterViewTest(APITestCase):

    def setUp(self):
        self.url = reverse('register')

    def test_register_success(self):
        """
        Test the user registration with valid data
        """
        data = {
            'email': 'testuser@example.com',
            'password': 'password123',
            'username': 'testuser',
            'role': 'patient'
        }
        response = self.client.post(self.url, data, format='json')

        # Check the response status code
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Check the response data for role and verify user is created
        self.assertEqual(response.data['role'], 'patient')

        # Ensure the user is saved in the database
        user = CustomUser.objects.get(email='testuser@example.com')
        self.assertIsNotNone(user)
        self.assertTrue(user.check_password('password123'))

    def test_register_invalid_data(self):
        """
        Test the user registration with invalid data (e.g., missing email or password)
        """
        data = {
            'email': 'testuser@example.com',
            'password': 222,
            'username': 'testuser',
            'role': 'patient'
        }

        response = self.client.post(self.url, data, format='json')

        # Check for bad request status code
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Check for specific error messages in the response
        self.assertIn('email', response.data)
        self.assertIn('password', response.data)

    def test_register_existing_email(self):
        """
        Test the user registration with an already existing email
        """
        data = {
            'email': 'testuser@example.com',
            'password': 'password123',
            'username': 'testuser',
            'role': 'patient'
        }

        # First, create the user manually
        CustomUser.objects.create_user(email='testuser@example.com', password='password123', role='patient', username='testuser')

        # Attempt to register with the same email
        response = self.client.post(self.url, data, format='json')

        # Check for conflict status code (usually 400 or 409 based on your settings)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Check if the response contains the email error
        self.assertIn('email', response.data)


class LoginViewTest(APITestCase):

    def setUp(self):
        self.url = reverse('login')

        # Create a test user for login
        self.user_data = {
            'email': 'testuser@example.com',
            'password': 'password123',
            'username': 'testuser',
            'role': 'patient'
        }
        self.user = get_user_model().objects.create_user(**self.user_data)

    def test_login_success(self):
        """
        Test the user login with correct credentials
        """
        data = {
            'email': 'testuser@example.com',
            'password': 'password123'
        }

        response = self.client.post(self.url, data, format='json')

        # Check for OK status
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check if the response contains the token
        self.assertIn('token', response.data)

        # Check if the returned role is correct
        self.assertEqual(response.data['role'], self.user.role)

        # Check if token is created
        token = Token.objects.get(user=self.user)
        self.assertEqual(response.data['token'], token.key)

    def test_login_invalid_credentials(self):
        """
        Test the user login with invalid credentials (wrong password)
        """
        data = {
            'email': 'testuser@example.com',
            'password': 'wrongpassword'
        }

        response = self.client.post(self.url, data, format='json')

        # Check for unauthorized status
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Check the error message
        self.assertEqual(response.data['error'], 'Invalid credentials')

    def test_login_non_existent_user(self):
        """
        Test login for a non-existent user
        """
        data = {
            'email': 'nonexistentuser@example.com',
            'password': 'password123'
        }

        response = self.client.post(self.url, data, format='json')

        # Check for unauthorized status
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Check the error message
        self.assertEqual(response.data['error'], 'Invalid credentials')

    def test_login_missing_credentials(self):
        """
        Test login with missing credentials
        """
        data = {}  # Empty data to test for missing fields

        response = self.client.post(self.url, data, format='json')

        # Check for bad request status (400)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Check if the response contains validation errors for email and password
        self.assertIn('email', response.data)
        self.assertIn('password', response.data)

class PatientProfileViewTest(APITestCase):

    def setUp(self):
        # Create a test user and link a Patient profile to them
        self.user_data = {
            'email': 'testpatient@example.com',
            'password': 'password123',
            'username': 'testpatient',
            'role': 'patient'

        }
        self.user = get_user_model().objects.create_user(**self.user_data)
        self.patient = Patient.objects.create(user=self.user, full_name="Test Patient", age=30)

        # URL for patient profile
        self.url = reverse('patient-profile')

    def test_get_patient_profile(self):
        """
        Test retrieving the patient's profile with valid credentials
        """
        # Authenticate the user
        self.client.login(email='testpatient@example.com', password='password123')

        response = self.client.get(self.url)

        # Ensure status is OK
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Ensure the response data contains patient information
        self.assertEqual(response.data['full_name'], 'Test Patient')
        self.assertEqual(response.data['age'], 30)

    def test_get_patient_profile_no_profile(self):
        """
        Test retrieving the patient's profile when no profile exists
        """
        # Create a new user without a patient profile
        user_no_profile = get_user_model().objects.create_user(email='no_profile@example.com', password='password123', username='noprofile', role='patient')

        # Authenticate the new user
        self.client.login(email='no_profile@example.com', password='password123')

        response = self.client.get(self.url)

        # Ensure status is NOT FOUND because the profile does not exist
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['error'], 'Patient profile not found.')

    def test_create_patient_profile(self):
        """
        Test creating a patient profile
        """
        # Create a new user to link a patient profile to
        new_user = get_user_model().objects.create_user(email='newpatient@example.com', password='password123', username='newuser', role='patient')

        # Authenticate the new user
        self.client.login(email='newpatient@example.com', password='password123')

        data = {
            'full_name': 'New Patient',
            'age': 25
        }

        response = self.client.post(self.url, data, format='json')

        # Ensure profile is created successfully and status is CREATED
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['full_name'], 'New Patient')
        self.assertEqual(response.data['age'], 25)

    def test_create_patient_profile_already_exists(self):
        """
        Test trying to create a profile when one already exists for the user
        """
        self.client.login(email='testpatient@example.com', password='password123')

        data = {
            'full_name': 'Test Patient Duplicate',
            'age': 40
        }

        response = self.client.post(self.url, data, format='json')

        # Ensure a patient profile already exists and return bad request status
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'Patient profile already exists.')

    def test_update_patient_profile(self):
        """
        Test updating the patient's profile with valid data
        """
        self.client.login(email='testpatient@example.com', password='password123')

        data = {
            'full_name': 'Updated Patient Name',
            'age': 31
        }

        response = self.client.put(self.url, data, format='json')

        # Ensure profile is updated successfully
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['full_name'], 'Updated Patient Name')
        self.assertEqual(response.data['age'], 31)

    def test_update_patient_profile_not_found(self):
        """
        Test trying to update the patient's profile when it doesn't exist
        """
        # Simulate no profile existing for this user
        self.client.login(email='no_profile@example.com', password='password123')

        data = {
            'full_name': 'Updated Patient Name',
            'age': 32
        }

        response = self.client.put(self.url, data, format='json')

        # Ensure status is NOT FOUND because profile doesn't exist
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['error'], 'Patient profile not found.')

    def test_delete_patient_profile(self):
        """
        Test deleting the patient's profile
        """
        self.client.login(email='testpatient@example.com', password='password123')

        response = self.client.delete(self.url)

        # Ensure the profile is deleted and status is NO CONTENT
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_patient_profile_not_found(self):
        """
        Test trying to delete the patient's profile when it doesn't exist
        """
        # Simulate no profile existing for this user
        self.client.login(email='no_profile@example.com', password='password123')

        response = self.client.delete(self.url)

        # Ensure status is NOT FOUND because profile doesn't exist
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['error'], 'Patient profile not found.')


class DoctorProfileViewTest(APITestCase):

    def setUp(self):
        # Create a test user and link a Doctor profile to them
        self.user_data = {
            'email': 'testdoctor@example.com',
            'password': 'password123',
            'username': 'testdoctor',
            'role': 'doctor'
        }
        self.user = get_user_model().objects.create_user(**self.user_data)
        self.doctor = Doctor.objects.create(user=self.user, specialization="General Practitioner")

        # URL for doctor profile
        self.url = reverse('doctor-profile')

    def test_get_doctor_profile(self):
        """
        Test retrieving the doctor's profile with valid credentials
        """
        # Authenticate the user
        self.client.login(email='testdoctor@example.com', password='password123')

        response = self.client.get(self.url)

        # Ensure status is OK
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Ensure the response data contains doctor information
        self.assertEqual(response.data['specialization'], 'General Practitioner')

    def test_get_doctor_profile_no_profile(self):
        """
        Test retrieving the doctor's profile when no profile exists
        """
        # Create a new user without a doctor profile
        user_no_profile = get_user_model().objects.create_user(email='no_profile@example.com', password='password123', username='newdoctor', role='doctor')

        # Authenticate the new user
        self.client.login(email='no_profile@example.com', password='password123')

        response = self.client.get(self.url)

        # Ensure status is NOT FOUND because the profile does not exist
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['error'], 'Doctor profile not found.')

    def test_create_doctor_profile(self):
        """
        Test creating a doctor profile
        """
        # Create a new user to link a doctor profile to
        new_user = get_user_model().objects.create_user(email='newdoctor@example.com', password='password123', username='newdoctor', role='doctor')

        # Authenticate the new user
        self.client.login(email='newdoctor@example.com', password='password123')

        data = {
            'specialization': 'Pediatrician'
        }

        response = self.client.post(self.url, data, format='json')

        # Ensure profile is created successfully and status is CREATED
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['specialization'], 'Pediatrician')

    def test_create_doctor_profile_already_exists(self):
        """
        Test trying to create a profile when one already exists for the user
        """
        self.client.login(email='testdoctor@example.com', password='password123')

        data = {
            'specialization': 'Cardiologist'
        }

        response = self.client.post(self.url, data, format='json')

        # Ensure a doctor profile already exists and return bad request status
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'Doctor profile already exists.')

    def test_update_doctor_profile(self):
        """
        Test updating the doctor's profile with valid data
        """
        self.client.login(email='testdoctor@example.com', password='password123')

        data = {
            'specialization': 'Orthopedic Surgeon'
        }

        response = self.client.put(self.url, data, format='json')

        # Ensure profile is updated successfully
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['specialization'], 'Orthopedic Surgeon')

    def test_update_doctor_profile_not_found(self):
        """
        Test trying to update the doctor's profile when it doesn't exist
        """
        # Simulate no profile existing for this user
        self.client.login(email='no_profile@example.com', password='password123')

        data = {
            'specialization': 'Neurologist'
        }

        response = self.client.put(self.url, data, format='json')

        # Ensure status is NOT FOUND because profile doesn't exist
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['error'], 'Doctor profile not found.')

    def test_delete_doctor_profile(self):
        """
        Test deleting the doctor's profile
        """
        self.client.login(email='testdoctor@example.com', password='password123')

        response = self.client.delete(self.url)

        # Ensure the profile is deleted and status is NO CONTENT
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_doctor_profile_not_found(self):
        """
        Test trying to delete the doctor's profile when it doesn't exist
        """
        # Simulate no profile existing for this user
        self.client.login(email='no_profile@example.com', password='password123')

        response = self.client.delete(self.url)

        # Ensure status is NOT FOUND because profile doesn't exist
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['error'], 'Doctor profile not found.')

class AppointmentViewTest(APITestCase):

    def setUp(self):
        # Create a test user and link profiles for doctor and patient
        self.user_data = {
            'email': 'testuser@example.com',
            'password': 'password123',
            'username': 'testuser',
            'role': 'patient'
        }
        self.user = get_user_model().objects.create_user(**self.user_data)
        self.patient_profile = Patient.objects.create(user=self.user, insurance_number="12345")
        self.user.patient_profile = self.patient_profile
        self.user.save()

        self.doctor_user = get_user_model().objects.create_user(email='doctor@example.com', password='password123', username='testdoctor', role='doctor')
        self.doctor_profile = Doctor.objects.create(user=self.doctor_user, specialization="General Practitioner")
        self.doctor_user.doctor_profile = self.doctor_profile
        self.doctor_user.save()

        self.appointment_data = {
            'doctor': self.doctor_profile.id,
            'date': '2025-04-10',
            'time': '10:00:00'
        }

        # URL for appointment endpoints
        self.url = reverse('appointments')

    def test_get_appointments_for_patient(self):
        """
        Test that a patient can retrieve their appointments successfully
        """
        # Create an appointment for the patient
        Appointment.objects.create(patient=self.patient_profile, doctor=self.doctor_profile, date='2025-04-10', time='10:00:00')

        # Authenticate the user
        self.client.login(email='patient@example.com', password='password123')

        response = self.client.get(self.url)

        # Ensure status is OK and appointments are returned
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Appointments fetched successfully.')
        self.assertEqual(len(response.data['appointments']), 1)

    def test_get_appointments_for_doctor(self):
        """
        Test that a doctor can retrieve their appointments successfully
        """
        # Create an appointment for the doctor
        Appointment.objects.create(patient=self.patient_profile, doctor=self.doctor_profile, date='2025-04-10', time='10:00:00')

        # Authenticate the doctor user
        self.client.login(email='doctor@example.com', password='password123')

        response = self.client.get(self.url)

        # Ensure status is OK and appointments are returned
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Appointments fetched successfully.')
        self.assertEqual(len(response.data['appointments']), 1)

    def test_get_appointments_unauthorized_user(self):
        """
        Test that an unauthorized user cannot access appointments
        """
        # Authenticate with an unauthenticated user
        self.client.login(email='unauthorized@example.com', password='password123')

        response = self.client.get(self.url)

        # Ensure status is Forbidden since the user has no patient or doctor profile
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        # self.assertEqual(response.data['error'], 'Unauthorized user.')

    def test_book_appointment_for_patient(self):
        """
        Test that a patient can book an appointment successfully
        """
        # Authenticate the patient
        self.client.login(email='patient@example.com', password='password123')

        response = self.client.post(self.url, self.appointment_data, format='json')

        # Ensure the appointment is successfully booked
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['message'], 'Appointment booked successfully.')
        self.assertTrue(response.data['available'])

    def test_book_appointment_already_booked(self):
        """
        Test that a patient cannot book an appointment if the slot is already taken
        """
        # Book the first appointment
        Appointment.objects.create(patient=self.patient_profile, doctor=self.doctor_profile, date='2025-04-10', time='10:00:00')

        # Authenticate the patient again and try to book the same slot
        self.client.login(email='patient@example.com', password='password123')

        response = self.client.post(self.url, self.appointment_data, format='json')

        # Ensure the appointment slot is already booked
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(response.data['message'], 'This slot is already booked.')
        self.assertFalse(response.data['available'])

    def test_book_appointment_for_non_patient(self):
        """
        Test that a doctor or non-patient cannot book an appointment
        """
        # Authenticate as a doctor
        self.client.login(email='doctor@example.com', password='password123')

        response = self.client.post(self.url, self.appointment_data, format='json')

        # Ensure only patients can book appointments
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['error'], 'Only patients can book appointments.')

    def test_book_appointment_invalid_data(self):
        """
        Test that the appointment booking fails if the data is invalid
        """
        # Modify the data with invalid time format
        invalid_data = {
            'doctor': self.doctor_profile.id,
            'date': '2025-04-10',
            'time': 'invalid-time-format'
        }

        # Authenticate the patient
        self.client.login(email='patient@example.com', password='password123')

        response = self.client.post(self.url, invalid_data, format='json')

        # Ensure validation error is returned
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn('errors', response.data)

class AppointmentUpdateViewTest(APITestCase):

    def setUp(self):
        # Create users and their profiles
        self.user_data = {
            'email': 'testuser@example.com',
            'password': 'password123',
            'username': 'testuser',
            'role': 'patient'
        }
        self.user = get_user_model().objects.create_user(**self.user_data)
        self.patient_profile = Patient.objects.create(user=self.user, insurance_number="12345")
        self.user.patient_profile = self.patient_profile
        self.user.save()

        self.doctor_user = get_user_model().objects.create_user(email='doctor@example.com', password='password123', username='testdoctor', role='doctor')
        self.doctor_profile = Doctor.objects.create(user=self.doctor_user, specialization="General Practitioner")
        self.doctor_user.doctor_profile = self.doctor_profile
        self.doctor_user.save()

        self.appointment = Appointment.objects.create(
            patient=self.patient_profile,
            doctor=self.doctor_profile,
            date="2025-04-10",
            time="10:00:00"
        )

        self.url = reverse('appointment-update', args=[self.appointment.id])

    def test_update_appointment_status_by_doctor(self):
        """
        Test that a doctor can update the status of an appointment
        """
        self.client.login(email='doctor@example.com', password='password123')

        response = self.client.put(self.url, {'status': 'Confirmed'}, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Appointment status updated.')

    def test_update_appointment_status_without_status(self):
        """
        Test that the appointment update fails if no status is provided
        """
        self.client.login(email='doctor@example.com', password='password123')

        response = self.client.put(self.url, {}, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'No status provided.')

    def test_update_appointment_status_unauthorized_user(self):
        """
        Test that a patient cannot update the appointment status
        """
        self.client.login(email='patient@example.com', password='password123')

        response = self.client.put(self.url, {'status': 'Confirmed'}, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        # self.assertEqual(response.data['error'], 'You are not authorized to update this appointment.')

    def test_delete_appointment_by_doctor(self):
        """
        Test that a doctor can delete an appointment
        """
        self.client.login(email='doctor@example.com', password='password123')

        response = self.client.delete(self.url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(response.data['message'], 'Appointment deleted successfully.')

    def test_delete_appointment_by_patient(self):
        """
        Test that a patient cannot delete an appointment
        """
        self.client.login(email='patient@example.com', password='password123')

        response = self.client.delete(self.url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        # self.assertEqual(response.data['error'], 'You do not have permission to delete this appointment.')

    def test_delete_appointment_not_found(self):
        """
        Test that a 404 is returned if the appointment is not found
        """
        self.client.login(email='doctor@example.com', password='password123')

        response = self.client.delete(reverse('appointment-update', args=[9999]))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        # self.assertEqual(response.data['error'], 'Appointment not found.')


class DoctorAvailabilityViewTest(APITestCase):

    def setUp(self):
        # Set up the doctor profile
        self.doctor_user = get_user_model().objects.create_user(email='doctor@example.com', password='password123', username='testdoctor', role='doctor')
        self.doctor_profile = Doctor.objects.create(user=self.doctor_user, specialization="General Practitioner")
        self.doctor_user.doctor_profile = self.doctor_profile
        self.doctor_user.save()

        self.url = reverse('doctor-availability', args=[self.doctor_profile.id])

    def test_get_doctor_availability_full_day(self):
        """
        Test that the doctor availability for the whole day is returned correctly
        """
        self.client.login(email='doctor@example.com', password='password123')

        response = self.client.get(self.url, {'date': '2025-04-10'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('time_slots', response.data)
        self.assertEqual(len(response.data['time_slots']), 18)  # From 08:00 to 17:00, 30-minute slots

    def test_get_doctor_availability_for_specific_time(self):
        """
        Test that the doctor availability for a specific time is checked correctly
        """
        self.client.login(email='doctor@example.com', password='password123')

        response = self.client.get(self.url, {'date': '2025-04-10', 'time': '10:00:00'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('available', response.data)
        self.assertTrue(response.data['available'])  # Assuming no appointment is booked

    def test_get_doctor_availability_unauthorized_user(self):
        """
        Test that an unauthorized user cannot access the doctor availability
        """
        self.client.login(email='unauthorized@example.com', password='password123')

        response = self.client.get(self.url, {'date': '2025-04-10'})

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        # self.assertEqual(response.data['error'], 'Unauthorized access.')


class MedicalRecordViewTest(APITestCase):

    def setUp(self):
        # Create users and their profiles
        self.doctor_user = get_user_model().objects.create_user(email='doctor@example.com', password='password123', username='testdoctor', role='doctor')
        self.doctor_profile = Doctor.objects.create(user=self.doctor_user, specialization="General Practitioner")
        self.doctor_user.doctor_profile = self.doctor_profile
        self.doctor_user.save()

        self.patient_user = get_user_model().objects.create_user(email='patient@example.com', password='password123', role='patient', username='testuser')
        self.patient_profile = Patient.objects.create(user=self.patient_user, insurance_number="12345")
        self.patient_user.patient_profile = self.patient_profile
        self.patient_user.save()

        self.medical_records = MedicalRecord.objects.create(
            patient=self.patient_profile,
            doctor=self.doctor_profile,
            notes="Test record"
        )

        self.url = reverse('medical-records')

    def test_create_medical_record_by_doctor(self):
        """
        Test that a doctor can create a medical record
        """
        self.client.login(email='doctor@example.com', password='password123')

        response = self.client.post(self.url, {
            'patient': self.patient_profile.id,
            'notes': 'New medical record data'
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['notes'], 'New medical record data')

    def test_create_medical_record_unauthorized_user(self):
        """
        Test that a patient cannot create a medical record
        """
        self.client.login(email='patient@example.com', password='password123')

        response = self.client.post(self.url, {
            'patient': self.patient_profile.id,
            'notes': 'New medical record data'
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['error'], 'Only doctors or admins can create medical records.')

    def test_update_medical_record(self):
        """
        Test that a doctor can update a medical record
        """
        self.client.login(email='doctor@example.com', password='password123')

        response = self.client.patch(reverse('medical-record-detail', args=[self.medical_records.id]), {
            'notes': 'Updated record data'
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['notes'], 'Updated record data')

    def test_delete_medical_record(self):
        """
        Test that a doctor can delete a medical record
        """
        self.client.login(email='doctor@example.com', password='password123')

        response = self.client.delete(reverse('medical-record-detail', args=[self.medical_records.id]))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(response.data['message'], 'Record deleted successfully.')

    def test_delete_medical_record_unauthorized_user(self):
        """
        Test that a patient cannot delete a medical record
        """
        self.client.login(email='patient@example.com', password='password123')

        response = self.client.delete(reverse('medical-record-detail', args=[self.medical_records.id]))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['error'], 'You do not have permission to delete this record.')