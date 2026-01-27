from datetime import datetime, date, timedelta
import random

from app import create_app
from app.models import (
    db,
    User,
    Department,
    Doctor,
    Patient,
    Appointment,
    Treatment,
    UserRole,
    Doc_Status,
    AP_Status
)
from werkzeug.security import generate_password_hash

app = create_app()


def seed_database():
    with app.app_context():
        print("🌱 Starting database seeding...")

        # -----------------------
        # Prevent duplicate seeding
        # -----------------------
        if Department.query.first():
            print("⚠️ Database already seeded. Skipping.")
            return

        # -----------------------
        # Create Admin
        # -----------------------
        User.make_admin()

        # -----------------------
        # Departments
        # -----------------------
        dept_data = [
            ("Cardiology", "Heart health and cardiovascular care."),
            ("Pediatrics", "Medical care for infants and children."),
            ("Neurology", "Nervous system and brain disorders."),
            ("Orthopedics", "Bone and joint care."),
            ("General Medicine", "Primary healthcare services."),
        ]

        departments = []
        for name, desc in dept_data:
            dept = Department(name=name, description=desc)
            db.session.add(dept)
            departments.append(dept)

        db.session.flush()  # generate IDs

        # -----------------------
        # Doctors
        # -----------------------
        doctors_data = [
            ("Dr. Sarah Chen", "MBBS, MD (Cardiology)", "sarah.chen@homa.com", 0),
            ("Dr. James Wilson", "MBBS, DCH", "j.wilson@homa.com", 1),
            ("Dr. Elena Rodriguez", "MBBS, DM (Neurology)", "elena.rod@homa.com", 2),
            ("Dr. Marcus Thorne", "MBBS, MS (Ortho)", "m.thorne@homa.com", 3),
            ("Dr. Alan Grant", "MBBS", "a.grant@homa.com", 4),
        ]

        doctors = []

        for idx, (name, qualification, email, dept_idx) in enumerate(doctors_data, start=1):
            user = User(
                email=email,
                password=generate_password_hash("doc123"),
                role=UserRole.DOCTOR
            )
            db.session.add(user)
            db.session.flush()

            doctor = Doctor(
                id=f"DOC-{dept_idx}-{user.id}",
                user_id=user.id,
                full_name=name,
                qualification=qualification,
                experience=random.randint(3, 15),
                status=Doc_Status.AVAILABLE,
                department_id=departments[dept_idx].id
            )
            db.session.add(doctor)
            doctors.append(doctor)

        # -----------------------
        # Patients
        # -----------------------
        patients_data = [
            ("John Doe", 34, "Male", "O+", "john.doe@gmail.com"),
            ("Jane Smith", 29, "Female", "A-", "jane.smith@yahoo.com"),
            ("Robert Brown", 52, "Male", "B+", "r.brown@outlook.com"),
            ("Emily White", 19, "Female", "AB+", "e.white@provider.com"),
            ("Michael Scott", 45, "Male", "O-", "m.scott@dunder.com"),
        ]

        patients = []

        for name, age, gender, blood, email in patients_data:
            user = User(
                email=email,
                password=generate_password_hash("patient123"),
                role=UserRole.PATIENT
            )
            db.session.add(user)
            db.session.flush()

            patient = Patient(
                user_id=user.id,
                full_name=name,
                age=age,
                gender=gender,
                blood_group=blood,
                phone=f"555-{user.id:03d}"
            )
            db.session.add(patient)
            patients.append(patient)

        db.session.flush()

        # -----------------------
        # Appointments
        # -----------------------
        appointments = []

        status_pool = (
            [AP_Status.COMPLETED] * 4 +
            [AP_Status.BOOKED] * 3 +
            [AP_Status.CANCELLED] * 3
        )

        random.shuffle(status_pool)

        for status in status_pool:
            patient = random.choice(patients)
            doctor = random.choice(doctors)

            if status == AP_Status.COMPLETED:
                ap_date = date.today() - timedelta(days=random.randint(1, 14))
            else:
                ap_date = date.today() + timedelta(days=random.randint(1, 14))

            appointment = Appointment(
                patient_id=patient.id,
                doctor_id=doctor.id,
                date=ap_date,
                time=datetime.utcnow(),
                status=status
            )
            db.session.add(appointment)
            appointments.append(appointment)

        db.session.flush()

        # -----------------------
        # Treatments (COMPLETED only)
        # -----------------------
        diagnoses = [
            "Common Cold",
            "Hypertension",
            "Migraine",
            "Type 2 Diabetes",
            "Joint Pain"
        ]

        prescriptions = [
            "Paracetamol 500mg twice daily",
            "Amlodipine 5mg once daily",
            "Ibuprofen after meals",
            "Metformin 500mg twice daily",
            "Physiotherapy and pain relievers"
        ]

        for ap in appointments:
            if ap.status == AP_Status.COMPLETED:
                treatment = Treatment(
                    appointment_id=ap.id,
                    diagnosis=random.choice(diagnoses),
                    prescription=random.choice(prescriptions),
                    notes="Patient advised rest, hydration, and follow-up if symptoms persist.",
                    follow_up=random.choice([True, False])
                )
                db.session.add(treatment)

        # -----------------------
        # Commit
        # -----------------------
        db.session.commit()

        print("✅ Database seeded successfully!")
        print("   - 1 Admin")
        print("   - 5 Departments")
        print("   - 5 Doctors")
        print("   - 5 Patients")
        print("   - 10 Appointments (Booked / Completed / Cancelled)")
        print("   - Treatments for completed appointments only")


if __name__ == "__main__":
    seed_database()
