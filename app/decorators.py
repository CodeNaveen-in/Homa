from functools import wraps
from flask import abort, flash
from flask_login import current_user
from app.models import UserRole

def role_required(*roles):
    def wrapper(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('You are not registered, please register first', 'warning')
                abort(401)

            if current_user.is_blocked:
                flash("YOU HAVE BEEN BLOCKED, CONTACT ADMIN FOR FUTHER DETAILS", "danger")
                abort(403)

            if current_user.role not in roles:
                flash("You are not authenticated for the task", "warning")
                abort(403)

            return f(*args, **kwargs)
        return decorated
    return wrapper

