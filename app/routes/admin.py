from flask import Blueprint, request, redirect, url_for, abort, render_template, flash
from flask_login import login_required, current_user
from app.models import User, Patient, Doctor, UserRole, Department, Appointment, Treatment, db, Doc_Status
from werkzeug.security import generate_password_hash
from app.decorators import role_required 

admin_bp = Blueprint("admin_bp", __name__, url_prefix="/admin")

@admin_bp.route("/dashboard")
@login_required # Protect the route
def dashboard():
    if not current_user.is_admin_check: # Use your model property
        abort(403)

    # Move queries INSIDE the function so they update
    users = User.query.all()
    patients = Patient.query.all()
    doctors = Doctor.query.all()
    departments = Department.query.all()
    appointments = Appointment.query.all()
    treatments = Treatment.query.all()

    return render_template(
        "admin/dashboard.html", 
        users=users, 
        patients=patients, 
        doctors=doctors, 
        departments=departments, 
        appointments=appointments, 
        treatments=treatments
    )

@admin_bp.route("/doctors")
@login_required
@role_required(UserRole.ADMIN)
def admin_doctors():
    doctors = Doctor.query.all()
    return render_template("doctors.html", doctors=doctors)

@admin_bp.route("/patients")
@login_required
@role_required(UserRole.ADMIN)
def admin_patients():
    patients = Patient.query.all()
    return render_template("admin/patients.html", patients=patients)

@admin_bp.route("/appointments")
@login_required
@role_required(UserRole.ADMIN)
def admin_appointments():
    appointments = Appointment.query.all()
    return render_template("admin/appointments.html", appointments = appointments)


@admin_bp.route("/add/doctors")
@login_required
# Corrected to pass the Role Enum, not the Blueprint
@role_required(UserRole.ADMIN) 
def add_doctor():
    departments = Department.query.all()
    if not current_user.is_admin_check:
        abort(403)
    return render_template("admin/add_doctor.html", departments = departments) #forgot to pass over the department query in template

@admin_bp.route("/add/doctors", methods=["POST"])
@login_required
@role_required(UserRole.ADMIN)
def add_doctor_post():
    email = request.form.get("email")

    # 1️⃣ Prevent duplicate users
    if User.query.filter_by(email=email).first():
        flash("Email already registered", "danger")
        return redirect(url_for("admin_bp.add_doctor"))

    try:
        # 2️⃣ Create User
        user = User(
            email=email,
            password=generate_password_hash(request.form.get("password")),
            role=UserRole.DOCTOR
        )
        db.session.add(user)
        db.session.flush()  # get user.id

        # 3️⃣ Read department_id from form
        department_id = int(request.form.get("department_id"))

        # 4️⃣ Create Doctor (WITH ID!)
        new_doc = Doctor(
            id=f"DOC-{department_id}-{user.id}",  # ✅ REQUIRED
            user_id=user.id,
            full_name=request.form.get("full_name"),
            qualification=request.form.get("qualification"),
            experience=int(request.form.get("experience", 1)),
            department_id=department_id,
            status=Doc_Status.AVAILABLE
        )

        db.session.add(new_doc)
        db.session.commit()

        flash(f"Dr. {new_doc.full_name} added successfully!", "success")

    except Exception as e:
        db.session.rollback()
        flash(f"Error adding doctor: {e}", "danger")

    return redirect(url_for("admin_bp.add_doctor"))


@admin_bp.route("/add/department")
@login_required
@role_required(UserRole.ADMIN)
def add_department():
    return render_template("/admin/add_department.html")

@admin_bp.route("/add/department/", methods=["POST"])
@login_required
@role_required(UserRole.ADMIN)
def add_department_post():
    name = request.form.get("name")
    description = request.form.get("description")
    
    if Department.query.filter_by(name=name).first():
        flash("Department already registered", "danger")
        return redirect(url_for("admin_bp.add_department"))
    
    department = Department(
        name = name,
        description = description
    )

    db.session.add(department)
    db.session.commit()

    flash(f"Department {name} has been added", "success")
    return redirect(url_for("admin_bp.add_department"))

@admin_bp.route("/edit/<int:department_id>", methods=["GET","POST"])
@login_required
@role_required(UserRole.ADMIN)
def admin_edit_department_post(department_id):
    department=Department.query.get_or_404(department_id)
    if request.method =="POST":
        name = request.form.get("name")
        description = request.form.get("description")
        if not name : 
            flash("Department name is required.", 'warning')
            return redirect(url_for("admin_bp.admin_edit_department_post",department_id=department_id))
        dept_exist = Department.query.filter_by(name=name).first()
        if dept_exist:
            flash("Department name already exist", "danger")
            return redirect(url_for("admin_bp.admin_edit_department_post"))
        department.name = name
        department.description = description
        db.session.commit()
        flash("Department updated successfully", 'success')
        return redirect(url_for("admin_bp.admin_departments"))
    return render_template("admin/edit_department.html", department=department)

@admin_bp.route("/edit/<string:doctor_id>", methods=["GET","POST"])
@login_required
@role_required(UserRole.ADMIN)
def admin_edit_doctor_post(doctor_id):
    doctor = Doctor.query.get_or_404(doctor_id)
    departments = Department.query.all()
    if request.method == "POST":
        email = request.form.get("email")
        full_name = request.form.get("full_name")
        qualification = request.form.get("qualification")
        department = request.form.get("department")
        experience = request.form.get("experience")
        status = Doc_Status(request.form.get("status"))

        if not all({email, full_name, qualification, department, experience, status}):
            flash("All fields are necessary", 'warning')
            return redirect(url_for("admin_bp.admin_edit_doctor_post"), doctor_id = doctor_id)
        
        doctor.user.email = email
        doctor.full_name = full_name
        doctor.qualification = qualification
        doctor.department = department
        doctor.experience = experience
        doctor.status = status
        
        db.session.commit()
        flash(f"Doctor {doctor.full_name} details are successfully edited", "success")
        return redirect(url_for("admin_bp.admin_doctors"))
    doctors = Doctor.query.all()
    return redirect(url_for('admin_bp.admin_doctors', doctors=doctors, departments=departments))

@admin_bp.route("/blacklist/<user_id>")
@login_required
@role_required(UserRole.ADMIN)
def blacklist(user_id):
    user = User.query.get_or_404(user_id)
    user.is_blocked = True
    db.session.commit()
    flash(f"You have blacklisted {user.email}")
    return(redirect(url_for("admin_bp.dashboard")))

@admin_bp.route("/unblacklist/<user_id>")
@login_required
@role_required(UserRole.ADMIN)
def unblacklist(user_id):
    user = User.query.get_or_404(user_id)
    user.is_blocked = False
    db.session.commit()
    flash(f"You have unblacklisted {user.email}")
    return(redirect(url_for("admin_bp.dashboard")))