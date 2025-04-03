# Healthcare Appointment Scheduling System Documentation

## Overview

The **Healthcare Appointment Scheduling System** is a web-based platform developed using Django. It enables efficient management of healthcare appointments by providing functionalities for **patient and doctor management, appointment scheduling, insurance details, and authentication via OAuth 2.0**. The system is backed by **PostgreSQL** for secure and scalable data management.

## Features

### 1. User Authentication and Authorization
- Secure login and authentication using OAuth 2.0.
- Role-based access control for **Patients, Doctors, and Admins**.

### 2. Patient Management
- Register, update, and manage patient profiles.
- Store medical history and insurance details.
- View past and upcoming appointments.

### 3. Doctor Management
- Register and manage doctor profiles, including specialization.
- View and manage assigned patient appointments.

### 4. Appointment Scheduling
- Patients can **book, reschedule, or cancel appointments**.
- Doctors can **approve or decline appointments**.
- Admins can oversee all appointments.

### 5. Insurance Management
- Link patients with **insurance providers**.
- Validate insurance coverage before appointments.

### 6. Medical Report Management

The **Medical Records** module allows doctors and authorized users to maintain and access patients' medical history. This ensures **continuity of care, accurate diagnosis, and effective treatment planning**.
#### Features:
✅ **Create and manage patient medical records**
✅ **Secure access control (only authorized users can view/edit)**
✅ **Store past diagnoses, treatments, prescriptions, and lab results**
✅ **Integration with appointments and doctor visits**


### 6. API Documentation
- API endpoints are documented using **Swagger/OpenAPI**.
- Available at `/swagger/` for interactive API testing.

---

## System Architecture

### 1. Technology Stack
| Component       | Technology Used |
|----------------|----------------|
| Backend        | Django (Python) |
| Database       | PostgreSQL      |
| Authentication | OAuth 2.0 (Django OAuth Toolkit) |
| API Docs       | Swagger (drf-yasg) |

### 2. System Design
- **Client-Server Model:** Uses a RESTful API to handle requests.
- **Role-based Access Control (RBAC):** Manages access levels for Patients, Doctors, and Admins.
- **Database Design:** Uses PostgreSQL with well-structured models for **Users, Appointments, Insurance, and Medical Records**.

### 3. Database Schema

### 4. Sequence Diagram
