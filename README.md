# Homa - Hospital Management System

A comprehensive full-stack web application designed to manage hospital operations efficiently. This project demonstrates a complete hospital management system with user authentication, role-based access control, appointment scheduling, and medical record management.

## 📋 Project Overview

Homa is a Flask-based hospital management system that enables seamless interaction between patients, doctors, and administrators. The system streamlines appointment booking, medical history tracking, department management, and staff administration within a hospital environment.

### Key Features

- **User Authentication & Authorization**: Secure login system with role-based access control
- **Multi-Role Support**: Admin, Doctor, and Patient roles with tailored dashboards
- **Appointment Management**: Patients can book appointments; doctors can manage their schedules
- **Medical Records**: Automatic medical history generation from completed appointments and treatments
- **Department Management**: Admins can create and manage hospital departments
- **Doctor Management**: Track doctor qualifications, experience, and availability status
- **Patient Profiles**: Store comprehensive patient information including medical history and blood group

## 🛠️ Technology Stack

### Frontend
- **HTML** with Jinja2 templating engine
- **CSS** with Bootstrap framework for responsive design
- **JavaScript** with ScrollReveal for UI animations

### Backend
- **Python** with Flask web framework
- **Flask-Login** for authentication and session management
- **Flask-SQLAlchemy** for database ORM

### Database
- **SQLite** for lightweight, file-based data persistence

### Dependencies
- Flask 3.1.2
- SQLAlchemy 2.0.46
- Werkzeug for password hashing
- python-dotenv for environment configuration

## 📊 Database Schema

### Core Tables

| Table | Purpose |
|-------|---------|
| **Users** | Central user management with role-based classification |
| **Patients** | Patient profiles with demographics and medical info |
| **Doctors** | Doctor information including qualifications and department |
| **Departments** | Hospital departments and specializations |
| **Appointments** | Scheduling appointments between patients and doctors |
| **Treatments** | Treatment records for completed appointments |

### Enums
- **UserRole**: ADMIN, DOCTOR, PATIENT
- **AppointmentStatus**: BOOKED, CANCELLED, COMPLETED
- **DoctorStatus**: AVAILABLE, LEAVE, BLACKLISTED

### Relationships
- Patients have many Appointments
- Doctors have many Appointments and belong to a Department
- Medical History is virtually created from Completed Appointments + Treatments

## 👥 User Roles & Capabilities

### Admin
- Dashboard with system overview
- Manage departments (create, edit, delete)
- Manage doctors (add, edit, view qualifications)
- View all patients and appointments
- Block/unblock users

### Doctor
- Personal dashboard and appointment schedule
- View assigned patients
- Access to patient medical history
- Manage availability status (Available, On Leave, Blacklisted)
- Manage treatment records

### Patient
- Self-registration with personal information
- Book appointments with available doctors
- Search and filter doctors by department
- View appointment history
- Access personal medical history

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- pip (Python package manager)

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd Homa
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure environment variables**
Create a `.env` file in the root directory:
```env
SQLALCHEMY_DATABASE_URI=sqlite:///instance/Hospital.sqlite3
SQLALCHEMY_TRACK_MODIFICATIONS=False
SECRET_KEY=your-secret-key-here
```

4. **Run the application**
```bash
python run.py
```

The application will start at `http://localhost:5000`

### Default Admin Credentials
- **Email**: admin@homa.com
- **Password**: admin123

## 📁 Project Structure

```
Homa/
├── app/
│   ├── __init__.py                 # Flask app factory
│   ├── api.py                      # API endpoints
│   ├── models.py                   # Database models
│   ├── decorators.py               # Custom decorators
│   ├── routes/
│   │   ├── auth.py                 # Authentication routes
│   │   ├── admin.py                # Admin routes
│   │   ├── doctor.py               # Doctor routes
│   │   └── patient.py              # Patient routes
│   └── templates/
│       ├── base.html               # Base template
│       ├── login.html
│       ├── register.html
│       ├── doctors.html
│       ├── messages.html
│       ├── searchbar.html
│       ├── admin/                  # Admin templates
│       ├── doctor/                 # Doctor templates
│       └── patient/                # Patient templates
├── instance/
│   └── Hospital.sqlite3            # SQLite database
├── run.py                          # Application entry point
├── seed.py                         # Database seeding script
├── requirements.txt                # Python dependencies
└── README.md
```

## 🔧 Development Features

### Database Initialization
- Automatic database creation on first run
- Default admin account creation
- SQLAlchemy ORM for safe database operations

### Password Security
- Passwords hashed using Werkzeug security
- Login manager for session handling
- Role-based access control with custom decorators

## 📝 Additional Notes

- The application uses SQLite for simplicity and easy deployment
- Jinja2 templating allows dynamic HTML generation
- Bootstrap ensures responsive design across devices
- The system automatically generates medical history by combining appointment and treatment records

## 🎯 Learning Outcomes

This project demonstrates:
- Full-stack web development with Flask
- Database design and relationships
- User authentication and authorization
- RESTful API design
- Frontend templating and responsive UI
- Role-based access control implementation