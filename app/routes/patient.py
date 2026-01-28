from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from app.models import db, User, Patient, Doctor, Department, Appointment, Treatment, AP_Status, Doc_Status, UserRole
from datetime import datetime
from app.decorators import role_required

patient_bp = Blueprint("patient_bp", __name__, url_prefix="/patient")

@patient_bp.route("/dashboard")
@login_required
def dashboard():
    patient = current_user.patient_profile
    
    # Upcoming Appointments
    upcoming = Appointment.query.filter(
        Appointment.patient_id == patient.id,
        Appointment.status == AP_Status.BOOKED
    ).order_by(Appointment.date.asc()).all()


    # Past Appointments with Treatments
    past = Appointment.query.filter(
        Appointment.patient_id == patient.id,
        Appointment.status == AP_Status.COMPLETED
    ).order_by(Appointment.date.desc()).all()

    return render_template("patient/dashboard.html", upcoming=upcoming, past=past)

@patient_bp.route("/doctors", methods=["GET"])
@login_required
def search_doctors():
    q = request.args.get('q', '').strip()
    dept_id = request.args.get('dept_id', type=int)
    
    query = Doctor.query.join(Department).filter(Doctor.status == Doc_Status.AVAILABLE)
    
    if q:
        query = query.filter(Doctor.full_name.ilike(f"%{q}%"))
    if dept_id:
        query = query.filter(Department.id == dept_id)
        
    doctors = query.all()
    departments = Department.query.all()
    return render_template("patient/search_doctors.html", doctors=doctors, departments=departments)

@patient_bp.route("/book/<string:doctor_id>", methods=["GET", "POST"])
@login_required
def book_appointment(doctor_id):
    doctor = Doctor.query.get_or_404(doctor_id)
    
    if request.method == "POST":
        date_str = request.form.get("date")
        time_str = request.form.get("time")
        
        # Simple check for doctor availability
        if doctor.status != Doc_Status.AVAILABLE:
            flash("Doctor is currently unavailable.", "danger")
            return redirect(url_for('patient_bp.search_doctors'))

        new_appt = Appointment(
            patient_id=current_user.patient_profile.id,
            doctor_id=doctor.id,
            date=datetime.strptime(date_str, '%Y-%m-%d').date(),
            time=datetime.strptime(time_str, '%H:%M'),
            status=AP_Status.BOOKED
        )
        db.session.add(new_appt)
        db.session.commit()
        flash("Appointment booked successfully!", "success")
        return redirect(url_for('patient_bp.dashboard'))

    return render_template("patient/book.html", doctor=doctor)

@patient_bp.route("/cancel/<int:appt_id>", methods=["POST"])
@login_required
def cancel_appointment(appt_id):
    appt = Appointment.query.get_or_404(appt_id)
    if appt.patient_id != current_user.patient_profile.id:
        abort(403)
    
    appt.status = AP_Status.CANCELLED
    db.session.commit()
    flash("Appointment cancelled.", "info")
    return redirect(url_for('patient_bp.dashboard'))

@patient_bp.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    patient = current_user.patient_profile
    if request.method == "POST":
        patient.full_name = request.form.get("full_name")
        patient.phone = request.form.get("phone")
        patient.address = request.form.get("address")
        db.session.commit()
        flash("Profile updated.", "success")
        return redirect(url_for('patient_bp.profile'))
    return render_template("patient/profile.html", patient=patient)

@patient_bp.route("/history")
@login_required
def medical_history():
    # Automatically identify the patient from the session
    patient = current_user.patient_profile
    
    if not patient:
        flash("Patient profile not found.", "danger")
        return redirect(url_for('auth_bp.login'))

    # Fetch all COMPLETED appointments that have treatment records
    history = Appointment.query.filter_by(
        patient_id=patient.id, 
        status=AP_Status.COMPLETED
    ).order_by(Appointment.date.desc()).all()

    return render_template("patient/medical_history.html", history=history, patient=patient)