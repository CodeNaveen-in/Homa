import enum
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash
from flask_login import UserMixin

db=SQLAlchemy()

class UserRole(enum.Enum):
    ADMIN = "admin"
    DOCTOR = "doctor"
    PATIENT = "patient"

class AP_Status(enum.Enum):
    BOOKED = "booked"
    CANCELLED = "cancelled"
    COMPLETED = "completed"

class Doc_Status(enum.Enum):
    AVAILABLE = "available"
    LEAVE = "leave"
    BLOCKED = "blacklisted"

class User(db.Model, UserMixin):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password = db.Column(db.String(256), nullable=False)
    is_blocked = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    role = db.Column(db.Enum(UserRole), default=UserRole.PATIENT)

    patient_profile = db.relationship('Patient', backref='user', uselist=False)
    doctor_profile = db.relationship('Doctor', backref='user', uselist=False)

    @property
    def is_admin_check(self):
        return self.role == UserRole.ADMIN
    
    @staticmethod
    def make_admin():
        admin = User.query.filter_by(role=UserRole.ADMIN).first()
        if not admin:
            print("Admin not present yet, creating one ..")
            default_admin = User ( 
                email = "admin@homa.com",
                password = generate_password_hash("admin123"),
                role = UserRole.ADMIN
            )
            db.session.add(default_admin)
            db.session.commit()
            print("Admin added into Database")
        else:
            print("Admin is present in DB")

class Patient(db.Model):
    __tablename__ = "patients"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    phone = db.Column(db.String(20), nullable=False, unique=True)
    address = db.Column(db.String(256), nullable=True)
    blood_group = db.Column(db.String(3), nullable=True)
    age = db.Column(db.Integer, nullable=False)
    full_name = db.Column(db.String(128), nullable=True)

    appointments = db.relationship('Appointment', backref='patient', lazy=True)

class Doctor(db.Model):
    __tablename__ = "doctors"
    id = db.Column(db.String(16), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    qualification = db.Column(db.String(128), nullable=False, default="MBBS")
    experience = db.Column(db.Integer, nullable=False, default=1)
    full_name = db.Column(db.String(128), nullable=True)
    status = db.Column(db.Enum(Doc_Status), default=Doc_Status.AVAILABLE)
    department_id = db.Column(db.Integer, db.ForeignKey("departments.id"))

    appointments = db.relationship('Appointment', backref='doctor', lazy=True)

class Department(db.Model):
    __tablename__ = "departments"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False, unique=True)
    description = db.Column(db.String(1024), nullable=True)
    is_active = db.Column(db.Boolean, default=True)

    doctors = db.relationship('Doctor', backref='department', lazy=True)

class Appointment(db.Model):
    __tablename__ = "appointments"
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey("patients.id"))
    doctor_id = db.Column(db.String(16), db.ForeignKey("doctors.id"))
    time = db.Column(db.DateTime, default=datetime.utcnow)
    date = db.Column(db.Date)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    status = db.Column(db.Enum(AP_Status), default=AP_Status.BOOKED)

class Treatment(db.Model):
    __tablename__ = "treatments"
    id = db.Column(db.Integer, primary_key=True)
    appointment_id = db.Column(db.Integer, db.ForeignKey("appointments.id"))
    diagnosis = db.Column(db.String(256), nullable=False)
    prescription = db.Column(db.String(512), nullable=False)
    notes = db.Column(db.String(5096), nullable=True)
    follow_up = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)