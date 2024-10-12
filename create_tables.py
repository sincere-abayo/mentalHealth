from app import app, db
from app.models import Patient, Doctor, Admin, Position  # Import all your models
from datetime import datetime
# from werkzeug.security import generate_password_hash  # To hash passwords securely

with app.app_context():
    # Create tables
    db.create_all()

    # Sample Data for Positions
    positions = [
        "Therapist Case Manager",
        "Therapist Clinician Case Manager",
        "Therapist Case Manager Nursing Director",
        "Clinician Clinical Supervisor Nursing Director",
        "Social Worker Team Leader Program Director",
        "General Practitioner"
    ]

    # Adding positions to the database
    for position_name in positions:
        position = Position(position_name=position_name)
        db.session.add(position)
    
    # Commit the positions to generate IDs
    db.session.commit()

    # Fetch positions from the database
    therapist_case_manager = Position.query.filter_by(position_name="Therapist Case Manager").first()
    general_practitioner = Position.query.filter_by(position_name="General Practitioner").first()

    # Sample Admin User
    admin = Admin(
        fullname='Admin User',
        email='admin@gmail.com',
        password='123'
    )
    db.session.add(admin)

    # # Sample Doctor User
    # doctor = Doctor(
    #     fullname='Dr. John Doctor',
    #     email='doctor@gmail.com',
    #     gender='Male',
    #     contact='1234567890',
    #     password='123',
    #     position=therapist_case_manager  # Link doctor to the "Therapist Case Manager" position
    # )
    # db.session.add(doctor)

    # Commit all changes
    db.session.commit()

    print("Sample data inserted successfully.")
