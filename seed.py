from app import create_app
from app.models import db, User, Department, Doctor, Patient, UserRole, Doc_Status
from werkzeug.security import generate_password_hash

app = create_app()

def seed_database():
    with app.app_context():
        print("Starting database seeding...")
        
        # 1. Clear existing data (Optional - use with caution!)
        # db.drop_all()
        # db.create_all()

        # 2. Add Departments
        depts_data = [
            {"name": "Cardiology", "desc": "Heart health and cardiovascular surgery."},
            {"name": "Pediatrics", "desc": "Specialized medical care for children."},
            {"name": "Neurology", "desc": "Disorders of the nervous system and brain."},
            {"name": "Orthopedics", "desc": "Musculoskeletal system injuries."},
            {"name": "General Medicine", "desc": "Primary care and routine checkups."}
        ]
        
        departments = []
        for d in depts_data:
            dept = Department(name=d["name"], description=d["desc"])
            db.session.add(dept)
            departments.append(dept)
        
        db.session.flush() # Push to DB to generate Department IDs

        # 3. Add Doctors
        # Each Doctor needs a User account first
        docs_data = [
            ("DOC-CAR-01", "Dr. Sarah Chen", "MBBS, MD (Cardiology)", "sarah.chen@homa.com", 0),
            ("DOC-PED-02", "Dr. James Wilson", "MBBS, DCH", "j.wilson@homa.com", 1),
            ("DOC-NEU-03", "Dr. Elena Rodriguez", "MBBS, DM (Neurology)", "elena.rod@homa.com", 2),
            ("DOC-ORT-04", "Dr. Marcus Thorne", "MBBS, MS (Ortho)", "m.thorne@homa.com", 3),
            ("DOC-GEN-05", "Dr. Alan Grant", "MBBS", "a.grant@homa.com", 4)
        ]

        for doc_id, name, qual, email, dept_idx in docs_data:
            user = User(
                email=email,
                password=generate_password_hash("doc123"),
                role=UserRole.DOCTOR
            )
            db.session.add(user)
            db.session.flush() # Get user.id

            profile = Doctor(
                id=doc_id,
                user_id=user.id,
                full_name=name,
                qualification=qual,
                department_id=departments[dept_idx].id
            )
            db.session.add(profile)

        # 4. Add Patients
        patients_data = [
            ("John Doe", 34, "Male", "O+", "john.doe@gmail.com"),
            ("Jane Smith", 29, "Female", "A-", "jane.smith@yahoo.com"),
            ("Robert Brown", 52, "Male", "B+", "r.brown@outlook.com"),
            ("Emily White", 19, "Female", "AB+", "e.white@provider.com"),
            ("Michael Scott", 45, "Male", "O-", "m.scott@dunder.com")
        ]

        for name, age, gender, blood, email in patients_data:
            user = User(
                email=email,
                password=generate_password_hash("patient123"),
                role=UserRole.PATIENT
            )
            db.session.add(user)
            db.session.flush()

            profile = Patient(
                user_id=user.id,
                full_name=name,
                age=age,
                gender=gender,
                blood_group=blood,
                phone=f"555-{age}{gender[0]}99" # Unique phone generator
            )
            db.session.add(profile)

        db.session.commit()
        print("Database successfully seeded with 5 Departments, 5 Doctors, and 5 Patients!")

if __name__ == "__main__":
    seed_database()