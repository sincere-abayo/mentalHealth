from app import db
from datetime import datetime

# Log model for user login and logout tracking
# class UserLog(db.Model):
#     __tablename__ = 'user_log'
#     log_id = db.Column(db.Integer, primary_key=True)
#     user_id = db.Column(db.Integer, db.ForeignKey('doctor.doctor_id'), nullable=False)
#     loginTime = db.Column(db.DateTime, nullable=False)
#     logoutTime = db.Column(db.DateTime)
#     created_at = db.Column(db.DateTime, default=datetime.utcnow)
#     updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

#     doctor = db.relationship('Doctor', back_populates='logs')

# Doctor model
class Doctor(db.Model):
    __tablename__ = 'doctor'
    doctor_id = db.Column(db.Integer, primary_key=True)
    position_id = db.Column(db.Integer, db.ForeignKey('position.position_id'), nullable=False)
    fullname = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    gender = db.Column(db.Enum('Male', 'Female', 'Other'), nullable=False)
    contact = db.Column(db.String(20))
    profile = db.Column(db.String(100))
    password = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    position = db.relationship('Position', back_populates='doctors')
    # logs = db.relationship('UserLog', back_populates='doctor')
    patient_assignments = db.relationship('DoctorPatientAssignment', back_populates='doctor')

# Admin model
class Admin(db.Model):
    __tablename__ = 'admin'
    admin_id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Position model (for doctor positions)
class Position(db.Model):
    __tablename__ = 'position'
    position_id = db.Column(db.Integer, primary_key=True)
    position_name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    doctors = db.relationship('Doctor', back_populates='position')
    patients = db.relationship('Patient', back_populates='position')

# Questionnaire model
class Questionnaire(db.Model):
    __tablename__ = 'questionnaire'
    question_id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.patient_id'), nullable=False)
    qn1 = db.Column(db.String(100))
    qn2 = db.Column(db.String(100))
    qn3 = db.Column(db.String(100))
    qn4 = db.Column(db.String(100))
    qn5 = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship
    patient = db.relationship('Patient', back_populates='questionnaires')

# progress model

class ProgressLog(db.Model):
    __tablename__ = 'progress_log'
    log_id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.patient_id'), nullable=False)
    mood = db.Column(db.Integer, nullable=False)  # Scale of 1-10
    symptoms = db.Column(db.String(255))
    notes = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship to Patient
    patient = db.relationship('Patient', back_populates='progress_logs')


# Patient model
class Patient(db.Model):
    __tablename__ = 'patient'
    patient_id = db.Column(db.Integer, primary_key=True)
    position_id = db.Column(db.Integer, db.ForeignKey('position.position_id'), nullable=True)
    firstname = db.Column(db.String(50), nullable=False)
    lastname = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    contact = db.Column(db.String(20), unique=True)
    contact_prefer = db.Column(db.Enum('Call', 'Mail', 'Message'))
    address = db.Column(db.String(255))
    dob = db.Column(db.Date, nullable=False)
    gender = db.Column(db.Enum('Male', 'Female', 'Other'), nullable=False)
    progress = db.Column(db.Integer, default=0)  # Progress as a percentage
    status = db.Column(db.Enum('confirmed', 'taken', 'pending', 'inactive'), default='inactive')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    position = db.relationship('Position', back_populates='patients')
    questionnaires = db.relationship('Questionnaire', back_populates='patient')
    doctor_assignments = db.relationship('DoctorPatientAssignment', back_populates='patient')
     # Relationship with ProgressLog
    progress_logs = db.relationship('ProgressLog', back_populates='patient')

# Doctor-Patient Assignment model (core model for assignment tracking)
class DoctorPatientAssignment(db.Model):
    __tablename__ = 'doctor_patient_assignment'
    assignment_id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.doctor_id'), nullable=False)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.patient_id'), nullable=False)
    status = db.Column(db.Enum('accepted', 'rejected', 'pending'), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    doctor = db.relationship('Doctor', back_populates='patient_assignments')
    patient = db.relationship('Patient', back_populates='doctor_assignments')


# message model
class Message(db.Model):
    __tablename__ = 'messages'
    message_id = db.Column(db.Integer, primary_key=True)
    sender_type = db.Column(db.Enum('doctor', 'patient'), nullable=False)
    sender_id = db.Column(db.Integer, nullable=False)
    receiver_type = db.Column(db.Enum('doctor', 'patient'), nullable=False)
    receiver_id = db.Column(db.Integer, nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    doctor_sender = db.relationship('Doctor', foreign_keys=[sender_id], 
                                    primaryjoin="and_(Message.sender_type=='doctor', foreign(Message.sender_id)==Doctor.doctor_id)",
                                    overlaps="patient_sender")
    patient_sender = db.relationship('Patient', foreign_keys=[sender_id], 
                                     primaryjoin="and_(Message.sender_type=='patient', foreign(Message.sender_id)==Patient.patient_id)",
                                     overlaps="doctor_sender")
    doctor_receiver = db.relationship('Doctor', foreign_keys=[receiver_id], 
                                      primaryjoin="and_(Message.receiver_type=='doctor', foreign(Message.receiver_id)==Doctor.doctor_id)",
                                      overlaps="patient_receiver")
    patient_receiver = db.relationship('Patient', foreign_keys=[receiver_id], 
                                       primaryjoin="and_(Message.receiver_type=='patient', foreign(Message.receiver_id)==Patient.patient_id)",
                                       overlaps="doctor_receiver")

