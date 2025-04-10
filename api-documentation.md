# Healthcare Appointment API Documentation

## Base URL
`https://q-tiberbu-api.onrender.com/api/`

---

## Authentication
- **Method:** Tokens
- **Required for all endpoints unless stated otherwise**

---

## Endpoints

### 1. Doctor Profile

#### GET `/doctors/profile/`
- **Description:** Retrieve the authenticated doctor's profile.
- **Auth:** Required (Doctor)
- **Response:**
```json
{
  "full_name": "Dr. Smith",
  "specialization": "Cardiology",
  "bio": "Experienced Cardiologist",
  "available_days": [
    {"day": "Monday", "start": "08:00", "end": "17:00"},
    {"day": "Wednesday", "start": "10:00", "end": "16:00"}
  ]
}
```

#### POST `/doctors/profile/`
- **Description:** Create a doctor profile.
- **Body:**
```json
{
  "full_name": "Dr. Smith",
  "specialization": "Cardiology",
  "bio": "Experienced Cardiologist",
  "available_days": [
    {"day": "Monday", "start": "08:00", "end": "17:00"},
    {"day": "Wednesday", "start": "10:00", "end": "16:00"}
  ]
}
```

#### PUT `/doctors/profile/`
- **Description:** Update profile (partial allowed).

#### DELETE `/doctors/profile/`
- **Description:** Delete the doctor profile.

---

### 2. Doctor Availability

#### GET `/appointments/doctor/{doctor_id}/availability/?date=YYYY-MM-DD&time=HH:MM`
- **Description:** Check if a doctor is available at a specific time.
- **Params:**
  - `date`: Required
  - `time`: Optional
- **Response:**
```json
{
  "doctor_id": 1,
  "date": "2025-04-12",
  "time": "09:00",
  "available": true
}
```

#### GET `appointments/doctor/{doctor_id}/availability/?date=YYYY-MM-DD`
- **Description:** Get all available time slots on a specific date.
- **Response:**
```json
{
  "doctor_id": 1,
  "date": "2025-04-12",
  "time_slots": [
    {"time": "08:00", "available": true},
    {"time": "08:30", "available": false}
  ]
}
```

---

### 3. Appointments

#### GET `/appointments/`
- **Description:** Retrieve all appointments for the authenticated user.
- **Response:**
```json
{
  "appointments": [
    {
      "id": 1,
      "doctor": "Dr. Smith",
      "date": "2025-04-12",
      "time": "09:00",
      "status":"pending",
      "reason":"Attendance",
    }
  ]
}
```

#### POST `/appointments/`
- **Description:** Book an appointment.
- **Auth:** Patient only
- **Body:**
```json
{
  "doctor": 1,
  "date": "2025-04-12",
  "time": "09:00",
  "reason":"Attendance",
}
```
- **Response:**
```json
{
  "message": "Appointment booked successfully.",
  "appointment": {
    "id": 5,
    "doctor": "Dr. Smith",
    "date": "2025-04-12",
    "time": "09:00",
    "reason":"Attendance",
  },
  "available": true
}
```
- **Conflict:** If the slot is already booked.
```json
{
  "message": "This slot is already booked.",
  "available": false
}
```

#### PUT `/appointments/{appointment_id}/`
- **Description:** Update an appointment status.
- **Auth:** Doctor Only
- **Body:**
```json
{
  "status": "complete"
}
```

#### DELETE `/appointments/{appointment__id}/`
- **Description:** Delete the doctor profile.
---

### 4. Authentication

#### POST `/auth/register/`
- **Description:** Register a new user.
- **Body:**
```json
{
  "username": "john_doe",
  "password": "securepassword123",
  "email": "john@example.com",
  "role": "patient" // admin or doctor
}
```

#### POST `/auth/login/`
- **Description:** Log in a user and retrieve access token.
- **Body:**
```json
{
  "email": "john@email.com",
  "password": "securepassword123"
}
```
- **Response:**
```json
{
  "access_token": "...",
  "token_type": "Bearer"
}
```

---

### 5. Patient Profile

#### GET `/patients/profile/`
- **Description:** Retrieve the authenticated patient's profile.

#### POST `/patients/profile/`
- **Description:** Create patient profile.
- **Body:**
```json
{
  "full_name": "John Doe",
  "age": 30,
  "gender": "Male",
  "phone":"+254758039176",
  "address":"kilimani",
  "insurance_number": "INS-123456",
  "insurance_provider": "NHIF"
}
```

#### PUT `/patients/profile/`
- **Description:** Update patient profile.

---

### 6. Medical Records

#### GET `/medical-records/`
- **Description:** List all medical records for the authenticated patient.

#### POST `/medical-records/`
- **Description:** Add a new medical record.
- **Body:**
```json
{
  "diagnosis": "Hypertension",
  "treatment": "Medication",
  "appointment":1,
  "patient":1,
  "doctor":1,
  "notes": "Patient to return in 2 weeks",
  "diagnosis":"Alzheimer",
  "treatment":"Pills",
}
```
#### PATCH `/medical-records/{id}/`
- **Description:** Update a  medical record.
- **Body:**
```json
{
  "diagnosis": "Hypertension",
  "treatment": "Medication",
  "appointment":1,
  "patient":1,
  "doctor":1,
  "notes": "Patient to return in 2 weeks",
  "diagnosis":"Alzheimer",
  "treatment":"Pills",
}
```

#### DELETE `/medical-records/{id}/`
- **Description:** Delete medical record.

---

## Notes
- Time format: `HH:MM`
- Date format: `YYYY-MM-DD`
- All times are in server timezone

---

## Error Response Format
```json
{
  "error": "Error message here."
}
