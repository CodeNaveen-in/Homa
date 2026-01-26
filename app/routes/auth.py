from flask import Blueprint, request, redirect, url_for, abort, render_template
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import login_user, current_user, login_required, logout_user
from app.models import User, Patient, UserRole, db

auth_bp = Blueprint("auth_bp", __name__)


@auth_bp.route("/")
def index():
    return redirect(url_for('auth_bp.login'))


# ---------------- REGISTER ----------------

@auth_bp.route("/register")
def register():
    return render_template('register.html')

@auth_bp.route("/register", methods=["POST"])
def register_post():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        full_name = request.form.get("full_name") # Get profile info

        if User.query.filter_by(email=email).first():
            return "Email already registered", 400

        # 1. Create User
        new_user = User(
            email=email,
            password=generate_password_hash(password),
            role=UserRole.PATIENT
        )
        db.session.add(new_user)
        db.session.flush() # This gives us new_user.id before committing

        # 2. Create Patient Profile
        new_patient = Patient(
            user_id=new_user.id,
            full_name=full_name,
            gender=request.form.get("gender"),
            phone=request.form.get("phone"),
            age=request.form.get("age")
        )
        db.session.add(new_patient)
        db.session.commit()
        return redirect(url_for("auth_bp.login"))
        
    return "Show Register HTML Here"


# ---------------- LOGIN ----------------
@auth_bp.route("/login")
def login():
    return render_template('login.html')

@auth_bp.route("/login", methods=["GET", "POST"])
def login_post():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            
            # Redirect based on role
            if user.role == UserRole.ADMIN:
                return redirect(url_for("auth_bp.admin_dashboard"))
            elif user.role == UserRole.DOCTOR:
                return redirect(url_for("auth_bp.doctor_dashboard"))
            else:
                return redirect(url_for("auth_bp.patient_dashboard"))

        return "Invalid credentials", 401
    return "Show Login HTML Here"


# ---------------- PROFILE (SESSION TEST) ----------------
@auth_bp.route("/profile")
@login_required
def profile():
    return (
        f"Logged in as: {current_user.email}\n"
        f"Role: {current_user.role.value}"
    )


# ---------------- ADMIN ONLY ----------------
@auth_bp.route("/admin")
@login_required
def admin_dashboard():
    if not current_user.is_admin_check:
        abort(403)
    return "ADMIN ACCESS GRANTED"

# ---------------- PATIENT ONLY ----------------
@auth_bp.route("/patient")
@login_required
def patient_dashboard():
    if current_user.role != UserRole.PATIENT:
        abort(403)
    return "PATIENT ACCESS GRANTED"


# ---------------- DOCTOR ONLY ----------------
@auth_bp.route("/doctor")
@login_required
def doctor_dashboard():
    if current_user.role != UserRole.DOCTOR:
        abort(403)
    return "DOCTOR ACCESS GRANTED"


# ---------------- LOGOUT ----------------
@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return "Logged out successfully"
