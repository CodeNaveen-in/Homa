from flask import Blueprint, request, redirect, url_for, abort, render_template, flash
from flask_login import login_required, current_user
from app.models import User, Patient, Doctor, UserRole, Department, Appointment, Treatment, db, Doc_Status, AP_Status
from app.decorators import role_required 
from datetime import datetime
from itertools import groupby

doctor_bp = Blueprint("doctor_bp", __name__, url_prefix="/doctor")

@doctor_bp.route("/dashboard")
@login_required
@role_required(UserRole.DOCTOR)
def dashboard():
    doctor = current_user.doctor_profile
    # Order by date so groupby works correctly
    appointments_query = Appointment.query.filter_by(doctor_id=doctor.id)\
        .order_by(Appointment.date.asc(), Appointment.time.asc()).all()
    
    # Group appointments by date
    # This creates a structure like: { datetime.date(2023, 10, 1): [appt1, appt2], ... }
    grouped_appointments = {}
    for date, group in groupby(appointments_query, lambda x: x.date):
        grouped_appointments[date] = list(group)

    return render_template(
        "doctor/dashboard.html", 
        grouped_appointments=grouped_appointments,
        doctor=doctor
    )

@doctor_bp.route("/appointment/<int:appointment_id>/status", methods=["POST"])
@login_required
@role_required(UserRole.DOCTOR)
def update_appointment_status(appointment_id):
    # Goal: Mark appointments as Completed or Cancelled
    appointment = Appointment.query.get_or_404(appointment_id)
    
    # Security check: Ensure this doctor owns the appointment
    if appointment.doctor_id != current_user.doctor_profile.id:
        abort(403)

    new_status = request.form.get("status")
    if new_status in AP_Status.__members__:
        appointment.status = AP_Status[new_status]
        db.session.commit()
        flash(f"Appointment marked as {new_status.lower()}.", "success")
    
    return redirect(url_for("doctor_bp.dashboard"))

@doctor_bp.route("/appointment/<int:appointment_id>/treatment", methods=["GET", "POST"])
@login_required
@role_required(UserRole.DOCTOR)
def add_treatment(appointment_id):
    # Goal: Enter diagnosis, treatment, and prescriptions
    appointment = Appointment.query.get_or_404(appointment_id)
    
    if request.method == "POST":
        new_treatment = Treatment(
            appointment_id=appointment.id,
            diagnosis=request.form.get("diagnosis"),
            prescription=request.form.get("prescription"),
            notes=request.form.get("notes"),
            follow_up='follow_up' in request.form
        )
        
        # Automatically mark appointment as completed when treatment is added
        appointment.status = AP_Status.COMPLETED
        
        db.session.add(new_treatment)
        db.session.commit()
        flash("Treatment records updated.", "success")
        return redirect(url_for("doctor_bp.dashboard"))

    return render_template("doctor/add_treatment.html", appointment=appointment)

@doctor_bp.route("/patient/<int:patient_id>/history")
@login_required
@role_required(UserRole.DOCTOR)
def medical_history(patient_id):
    # Goal: View complete patient medical history
    patient = Patient.query.get_or_404(patient_id)
    
    # Join Treatment with Appointment to find all previous records for this patient
    history = db.session.query(Treatment).join(Appointment).filter(
        Appointment.patient_id == patient_id
    ).order_by(Treatment.created_at.desc()).all()

    return render_template("doctor/medical_history.html", patient=patient, history=history)

@doctor_bp.route("/update-availability", methods=["POST"])
@login_required
@role_required(UserRole.DOCTOR)
def update_availability():
    # Goal: Update their own availability schedule
    doctor = current_user.doctor_profile
    new_status = request.form.get("status")
    
    if new_status in Doc_Status.__members__:
        doctor.status = Doc_Status[new_status]
        db.session.commit()
        flash("Your availability status has been updated.", "info")
    
    return redirect(url_for("doctor_bp.dashboard"))