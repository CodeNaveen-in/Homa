import os
from flask import Flask
from models import db, User, Patient, Doctor, Appointment, Department, Treatment
from dotenv import load_dotenv

load_dotenv()

app=Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("SQLALCHEMY_DATABASE_URI")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = os.getenv("SQLALCHEMY_TRACK_MODIFICATIONS")
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")

db.init_app(app)
with app.app_context():
    db.create_all()
    User.make_admin()

if (__name__ == "__main__"):
    app.run()