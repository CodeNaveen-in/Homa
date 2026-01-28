from flask import Blueprint, request, jsonify
from app.models import db, User, Patient, Doctor, Appointment, AP_Status, Doc_Status, UserRole
from werkzeug.security import generate_password_hash

api_bp = Blueprint("api_bp", __name__, url_prefix="/api/v1")

# ---------------- DOCTOR API ----------------

@api_bp.route("/doctors", methods=["GET"])
def get_doctors():
    """Retrieve all available doctors."""
    doctors = Doctor.query.all()
    return jsonify([{
        "id": d.id,
        "name": d.full_name,
        "specialization": d.department.name,
        "status": d.status.name
    } for d in doctors]), 200

@api_bp.route("/doctors", methods=["POST"])
def create_doctor():
    """Admin-level API to create a doctor."""
    data = request.json
    # Create User first
    user = User(
        email=data['email'],
        password=generate_password_hash(data['password']),
        role=UserRole.DOCTOR
    )
    db.session.add(user)
    db.session.flush()

    new_doc = Doctor(
        id=f"DOC-{data['department_id']}-{user.id}",
        user_id=user.id,
        full_name=data['full_name'],
        department_id=data['department_id'],
        status=Doc_Status.AVAILABLE
    )
    db.session.add(new_doc)
    db.session.commit()
    return jsonify({"message": "Doctor created", "id": new_doc.id}), 201

# ---------------- APPOINTMENT API ----------------

@api_bp.route("/appointments/<int:id>", methods=["GET"])
def get_appointment(id):
    """Retrieve a single appointment's details."""
    appt = Appointment.query.get_or_404(id)
    return jsonify({
        "patient": appt.patient.full_name,
        "doctor": appt.doctor.full_name,
        "date": appt.date.isoformat(),
        "status": appt.status.name
    }), 200

@api_bp.route("/appointments/<int:id>", methods=["PUT"])
def update_appointment(id):
    """Update appointment status (Reschedule/Cancel)."""
    appt = Appointment.query.get_or_404(id)
    data = request.json
    
    if "status" in data:
        appt.status = AP_Status[data["status"]]
    if "date" in data:
        appt.date = data["date"]
        
    db.session.commit()
    return jsonify({"message": "Appointment updated"}), 200

@api_bp.route("/appointments/<int:id>", methods=["DELETE"])
def delete_appointment(id):
    """Hard delete an appointment record."""
    appt = Appointment.query.get_or_404(id)
    db.session.delete(appt)
    db.session.commit()
    return jsonify({"message": "Appointment deleted"}), 204